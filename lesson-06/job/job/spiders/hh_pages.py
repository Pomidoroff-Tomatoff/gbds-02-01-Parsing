import scrapy
from scrapy_splash import SplashRequest
from w3lib.url import add_or_replace_parameters
import logging
from job.items import HhPages_JobItem  # класс данных из item.py

import job.spiders.job as job  # Библиотека для парсера


class HhPagesSpider(scrapy.Spider):
    name = 'hh_pages'
    allowed_domains = ['hh.ru']
    transfer_protocol = 'https://'
    url_middle = '/search/vacancy/'
    # start_urls = ['http://hh.ru/']
    # start_url = 'https://hh.ru/search/vacancy/'

    collection_name = HhPages_JobItem.collection_name

    splash_mode = False   # Включение рендеринга SPLASH: True
    count_pages = 0
    max_count_pages = 500000

    custom_settings = {
        # LOG_LEVEL
        # https://docs.scrapy.org/en/latest/topics/settings.html#std-setting-LOG_LEVEL
        # In list: CRITICAL, ERROR, WARNING, INFO, DEBUG
        'LOG_LEVEL': 'ERROR',

        # 'SPLASH_URL': 'http://localhost:8050',
        # 'SPLASH_URL': 'http://127.0.0.1:8050/run',
        # Используем сервер в инете со Splash-ем, случайно найденный...
        # 'SPLASH_URL': 'https://s1.onekkk.com/',

        # Описание других параметров:
        # https://pypi.python.org/pypi/scrapy-splash
    }

    # Параметры поиска вакансий
    # -- примантировать параметры к начальной ссылке можно при помощи хорошей функции
    #      add_or_replace_parameters (w3lib.url)
    #    позволяющей не беспокоится о правилах стыковки частей запроса.

    item_on_page = 20
    params = {
        'area': 1,
        'clusters': 'true',
        'enable_snippets': 'true',
        'items_on_page': item_on_page,
        'ored_clusters': 'true',
        'search_field': 'description',
        'text': 'python',
        'order_by': 'publication_time',
        'hhtmFrom': 'vacancy_search_list',
        'customDomain': 1,
    }

    script = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            splash.resource_timeout = 10.0
            splash: set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36")
            assert(splash:go(args.url))
            assert(splash:wait(1))
            return splash:html()
        end
    '''  # https://splash.readthedocs.io/en/stable/scripting-ref.html

    def get_rendering_request(self, url=None, callback=None):
        ''' Решаем, чем мы будем получать страничку:
            * используя плагин Spash (self.splash_mode == True)
            * при помощи стандартного механизма Скрапи
        '''
        # Проверка параметров
        if not url or not callback:
            logging.log(logging.CRITICAL, "*** ERROR method parameter: url or callback is None")
            return None

        if self.splash_mode:
            logging.log(logging.INFO, "*** INFO: Splash plugin is used.")
            return SplashRequest(
                url=url,  # Сайт, который нужно рендерить
                endpoint='execute',  # Выполнить скрипт?
                callback=callback,  # После выполнения скрипта ответ передать ф. self.parse()
                args={'lua_source': self.script}  # Скрипт для выполнения Spash
            )
        else:
            logging.log(logging.INFO, "*** INFO: Use standard scrapy Request.")
            return scrapy.Request(url=url, callback=callback)

    def start_requests(self):
        ''' Доступ с параметрами нужен только к первой странице списка,
            переход на следующие странице выполняется ссылкой в кнопке перехода на сл. стр.
        '''
        response = self.get_rendering_request(
            url=add_or_replace_parameters(
                self.transfer_protocol + self.allowed_domains[0].strip('/') + '/' + self.url_middle.strip('/'),
                self.params),
            callback=self.parse
        )
        yield response

    def parse(self, response):
        self.count_pages += 1
        if self.count_pages > self.max_count_pages:
            logging.log(logging.INFO, f"Количество страниц списка {self.count_pages + 1} вышло за максимум, листание остановлено...")
            return None

        vacancies = response.xpath('//div[@id="a11y-main-content"]')
        vacancies = vacancies.xpath('./div[contains(@data-qa, "vacancy-serp__vacancy")]')
        print(f"PAGE PROCESSING:{self.count_pages:->5}, {len(vacancies)=}")

        for vacancy in vacancies:
            link = vacancy.xpath('.//h3/*/a[@data-qa="serp-item__title"]/@href').get().split('?')[0]
            yield self.get_rendering_request(url=link, callback=self.parse_item)
            # yield response.follow(url=link, callback=self.parse_item)

        next = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next:
            next_url = self.transfer_protocol + self.allowed_domains[0].strip('/') + "/" + next.strip("/")
            yield self.get_rendering_request(url=next_url, callback=self.parse)
        return None

    def parse_item(self, response):
        item = HhPages_JobItem(
            # ВНИМАНИЕ: хитрый заголовок!
            #   После тега 'h1' указывать тег 'span' нельзя, иначе возвращается None,
            #   вместо текста заголовка
            _id=int(
                response.url.split('/vacancy/')[-1]
            ),
            title=
                response.xpath('//div[@class="vacancy-title"]/h1/text()').get(),
            employer=job.join_clear(
                job.duplicate_remover(
                    response.xpath('//span[@data-qa="bloko-header-2"]/text()').getall()
                )
            ),
            date_publication=job.date_convert(
                response.xpath('//p[contains(@class, "vacancy-creation-time")]/text()').getall()
            ),
                # Варианты: vacancy-creation-time, vacancy-creation-time-redesigned
                # https://hh.ru/vacancy/76132760
                # <p class="vacancy-creation-time">
                # ['Вакансия опубликована ', '24\xa0января\xa02023', ' в ', 'Москве']
            link =
                response.url
        )
        salary = job.get_maney(
            job.join_clear(
                response.xpath('.//div[@class="vacancy-title"]/*[@data-qa="vacancy-salary"]/span/text()').getall()
            )
        )
        item['salary_min'] = salary['min']
        item['salary_max'] = salary['max']
        item['salary_cur'] = salary['cur']
        yield item

import scrapy
from w3lib.url import add_or_replace_parameters

from job.items import HhList_JobItem
from scrapy.loader import ItemLoader

import job.spiders.job as job  # Библиотека для парсера


class HhListSpider(scrapy.Spider):
    name = 'hh_list'
    allowed_domains = ['hh.ru']
    # start_urls = ['http://hh.ru/']
    # start_urls = ['https://hh.ru/search/vacancy?area=1&clusters=true&enable_snippets=true&items_on_page=20&ored_clusters=true&search_field=description&text=python&order_by=publication_time&hhtmFrom=vacancy_search_list']
    start_url = 'https://hh.ru/search/vacancy/'

    # Имя для MongoDB и MySQL для этого паучка
    collection_name = HhList_JobItem.collection_name

    # счётчики-ограничители
    count_pages = 1
    max_count_pages = 500000  # макс. количество страниц со списком вакансий, для отладки

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

    custom_settings = {
        # LOG_LEVEL
        # https://docs.scrapy.org/en/latest/topics/settings.html#std-setting-LOG_LEVEL
        # In list: CRITICAL, ERROR, WARNING, INFO, DEBUG
        'LOG_LEVEL': 'ERROR',

        # Описание других параметров:
        # https://pypi.python.org/pypi/scrapy-splash
    }

    def start_requests(self):
        # Параметры поиска вакансий
        # -- примантировать параметры к начальной ссылке можно при помощи функции
        #      add_or_replace_parameters (w3lib.url)
        #    позволяющей не беспокоится о правилах стыковки частей запроса.
        request = scrapy.Request(
            url=add_or_replace_parameters(self.start_url, self.params),
            callback=self.parse)
        yield request

    def parse(self, response):
        # текущая страница: находим все объекты с вакансиями и разбираем каждую
        vacancies = response.xpath('//div[@id="a11y-main-content"]/div[contains(@class, "serp-item")]')
        print(f"PAGE PROCESSING:{self.count_pages:->5}, {len(vacancies)=}")  # Порядок обрабатываемой страницы может не соотв. номеру страницы.
        for vacancy in vacancies:
            yield self.parse_item(vacancy)

        # Ограничение объёма обработки страниц: можно дальше?
        if self.count_pages >= self.max_count_pages:   # ограничение
            return None  # хватит...
        else:
            self.count_pages += 1

        # следующая страница, если есть...
        next = response.xpath('//div[@data-qa="pager-block"]/a[@data-qa="pager-next"]/@href').get()
        if next:
            yield response.follow(url=next, callback=self.parse)
        return None

    def parse_item(self, vacancy):
        # поехали
        item = HhList_JobItem(
            title =
                vacancy.xpath('.//a[@class="serp-item__title"]/text()').get(),
            link =
                vacancy.xpath('.//a[@class="serp-item__title"]/@href').get().split('?')[0],
            employer = job.join_clear(
                vacancy.xpath('.//a[@data-qa="vacancy-serp__vacancy-employer"]/text()').getall()),
        )
        salary = job.get_maney(
            job.join_clear(
                vacancy.xpath('.//span[@data-qa="vacancy-serp__vacancy-compensation"]/text()').getall()
            )
        )
        item['salary_min'] = salary['min']
        item['salary_max'] = salary['max']
        item['salary_cur'] = salary['cur']
        item['_id'] = int(item['link'].split('/vacancy/')[1])
        return item

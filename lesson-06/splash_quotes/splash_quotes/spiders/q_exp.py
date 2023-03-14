import scrapy


class QExpSpider(scrapy.Spider):
    name = 'q_exp'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/',
                  'http://quotes.toscrape.com/js']

    custom_settings = {
        # In list: CRITICAL, ERROR, WARNING, INFO, DEBUG
        'LOG_LEVEL': 'ERROR',

        # Configure item pipelines
        'ITEM_PIPELINES': {
           'splash_quotes.pipelines.SplashQuotesPipeline': 300,
        },
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        quotes = response.xpath('//div[@class="quote"]')
        print(f"*** PARSE, QUOTES = {len(quotes)}, url = {response.url}, Цитаты:")
        for quote in quotes:
            yield {'author': quote.xpath('.//small[@class="author"]/text()').get(),}

        # next_page_local = response.xpath('//nav').xpath('.//li[@class="next"]/a/@href').get()
        next_page_local = response.xpath('//nav/*/li[@class="next"]/a/@href').get()
        if next_page_local:
            # Далее мы одну и ту же местную ссылку прибавляем к базовым ссылкам, фактическу двух сайтов
            # Это не правильно, но мы хотели здесь проверить работоспособность алгоритма.
            for start_url in self.start_urls:
                next_page = start_url.strip('/') + next_page_local
                print(f"{next_page=}")
                yield scrapy.Request(url=next_page, callback=self.parse)


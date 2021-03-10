import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import VasylItem
from itemloaders.processors import TakeFirst
from scrapy.http import FormRequest
import json

pattern = r'(\xa0)?'


class VasylSpider(scrapy.Spider):
    name = 'vasyl'
    base_url = 'https://www.sparv.dk'

    def start_requests(self):
        yield FormRequest("https://www.sparv.dk/api/sdc/news/search",
                          formdata={"page": '0', "filterType": "categories",
                                    "filterValues": ["Nyheder for privatkunder", "Bolig", "Forsikring", "Investering",
                                                     "Nyheder for erhvervskunder", "Pension", "Priser og renter",
                                                     "Nyheder for foreninger", "Regnskabsmeddelelser",
                                                     "Selvbetjening"]},
                          callback=self.parse,

                          )

    def parse(self, response):
        data = json.loads(response.text)
        for key in data['results']:
            url = key['url']
            full_url = self.base_url + url
            yield response.follow(full_url, self.parse_post)


        for page in range(data['totalPages']):
            yield FormRequest("https://www.sparv.dk/api/sdc/news/search",
                              formdata={"page": str(page), "filterType": "categories",
                                        "filterValues": ["Nyheder for privatkunder", "Bolig", "Forsikring",
                                                         "Investering",
                                                         "Nyheder for erhvervskunder", "Pension", "Priser og renter",
                                                         "Nyheder for foreninger", "Regnskabsmeddelelser",
                                                         "Selvbetjening"]},
                              callback=self.parse,
                              )

    def parse_post(self, response):
        date = response.xpath('//time/text()').get().strip()
        if not date:
            date = "-"
        title = response.xpath('//h1[@class="article-top-a__title"]/text() | //h1[@class="article-top-b__title"]/text()').get()
        content = response.xpath(
            '//div[@class="text-module-a frame rich-text  "]//div[@class="frame__cell-item"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=VasylItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()

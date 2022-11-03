import json
import scrapy
from ..items import EmlakItem


class HepsiemlakSpider(scrapy.Spider):
    name = 'hepsiemlak'
    allowed_domains = ['hepsiemlak.com']
    start_urls = ['https://www.hepsiemlak.com/api/realty-list?urlCriteria=antalya%2Ckepez%2Ckonyaalti%2Cmuratpasa%2Ckiralik%2Ckonut%2C1-1%2C2-1%2C3-1&fillIntentUrls=false']

    def parse(self, response):
        fld_lst = ['id', 'price', 'createDate']
        data = json.loads(response.body)
        lst = data['realtyList']
        for adv in lst:
            item = EmlakItem()
            for fld in fld_lst:
                item[fld] = adv[fld]
            yield item

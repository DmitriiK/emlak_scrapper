import json
import scrapy
import time
from ..items import EmlakItem


class HepsiemlakSpider(scrapy.Spider):
    name = 'hepsiemlak'
    allowed_domains = ['hepsiemlak.com']
    baseURL = 'https://www.hepsiemlak.com/api/realty-list/antalya-kiralik?counties=kepez,konyaalti,muratpasa&page='
    start_urls = [baseURL+'1']

    def parse(self, response):
        fld_lst = {'id', 'age', 'price', 'createDate', 'updatedDate', 'mapLocation/lon', 'mapLocation/lat',
                    'city/id', 'city/name', 'county/id', 'county/name', 'district/id', 'district/name',
                   'sqm/netSqm', 'roomAndLivingRoom', 'floor/count', 'detailDescription'}
        data = json.loads(response.body)
        lst = data['realtyList']
        for adv in lst:
            d_ret = dict()
            for fld in fld_lst:
                flds_down = fld.split('/')
                key = fld.replace('/', '_')
                d_ret[key] = adv[flds_down[0]] if len(flds_down) == 1 else adv[flds_down[0]][flds_down[1]]
            yield d_ret

        totalPages, page = data['totalPages'], data['page']

        if page <= 10: #page != totalPages &
            next_page_url = self.baseURL+str((page+1))
            time.sleep(1)
            yield response.follow(next_page_url, callback=self.parse)

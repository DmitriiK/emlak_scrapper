import json
import scrapy
import time
from ..metadata import JsonSchema, GetParams
from ..items import EmlakItem


class HepsiemlakSpider(scrapy.Spider):
    name = 'hepsiemlak'
    allowed_domains = ['hepsiemlak.com']
    baseURL = 'https://www.hepsiemlak.com/api/realty-list/antalya-kiralik?counties=kepez,konyaalti,muratpasa&page='

    start_urls = []
    for ifp in [GetParams.IsFurnished, GetParams.NotIsFurnished]:
        # for igh in [GetParams.IsGazHeating, GetParams.NotIsGazHeating]:
        url = f'https://www.hepsiemlak.com/api/realty-list/antalya-kiralik?counties=kepez,konyaalti,muratpasa&{ifp}&page=1'
        start_urls.append(url)
    # --https://www.hepsiemlak.com/antalya-kiralik-esyali?counties=kepez,konyaalti,muratpasa&furnishStatus=FURNISHED


    def parse(self, response):
        data = json.loads(response.body)
        current_url = response.request.url
        lst = data[JsonSchema.rootNode]
        for adv in lst:
            d_ret = dict()
            for fld in JsonSchema.hepsiemlak_source_fields:
                flds_down = fld.split('/')
                key = JsonSchema.flat_name(fld)
                if len(flds_down) == 1:
                    d_ret[key] = adv[flds_down[0]]
                else:
                    key2 = int(flds_down[1]) if flds_down[1].isdigit() else flds_down[1]
                    d_ret[key] = adv[flds_down[0]][key2]
            d_ret['is_furnished'] = GetParams.IsFurnished in current_url
            yield d_ret

        totalPages, page = data['totalPages'], data['page']

        if page < totalPages:
            next_page_url = current_url.replace(f'&page={page}', f'&page={page+1}') # yes, I don't like it as well..
            time.sleep(1)
            yield response.follow(next_page_url, callback=self.parse)

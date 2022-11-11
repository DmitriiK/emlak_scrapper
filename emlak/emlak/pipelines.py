# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class EmlakPipeline:
    def process_item(self, item, spider):
        return item


class SavingToPostgresPipeline(object):

    def __init__(self):
        self.create_connection()
        self.lst_flds = ['id',
                         'age',
                         'price',
                         'createDate',
                         'updatedDate',
                         'mapLocation_lon',
                         'mapLocation_lat',
                         'city_id',
                         'city_name',
                         'county_id',
                         'county_name',
                         'district_id',
                         'district_name',
                         'sqm_netSqm',
                         'roomAndLivingRoom',
                         'floor_count',
                         'detailDescription']

    def create_connection(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="emlak",
            user="postgres",
            password="123")

        self.curr = self.connection.cursor()

    def process_item(self, item, spider):
        self.store_db(item)
        # we need to return the item below as scrapy expects us to!
        return item

    def store_db(self, item):
        values = tuple([item[key] for key in self.lst_flds])
        try:
            sql = f"insert into HepsiEmlak({', '.join(self.lst_flds)}) VALUES ({(', ').join(['%s'] * len(self.lst_flds))})"
            self.curr.execute(sql, values)
        except BaseException as e:
            print(e)
            self.connection.commit()
        self.connection.commit()

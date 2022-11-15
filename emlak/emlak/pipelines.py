# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
from metadata import JsonSchema


class EmlakPipeline:
    def process_item(self, item, spider):
        return item


class SavingToPostgresPipeline(object):

    def __init__(self):
        self.create_connection()
        self.curr.execute('INSERT INTO F_LOADS(dt_start) VALUES (now()) RETURNING load_id')
        data = self.curr.fetchone()
        self.load_id = data[0]
        """
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
                         # 'sqm_grossSqm_0'
                         'room_0',
                         'livingRoom_0',
                         'floor_count',
                         'detailDescription',
                         'is_furnished'
                         ]
"""
        self.lst_flds = [JsonSchema.flat_name(x) for x in JsonSchema.hepsiemlak_source_fields] + ['is_furnished']  # ((

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
        values = tuple([self.load_id] + [item[key] for key in self.lst_flds])
        # values = (11, 39741352, 11, 8500)
        try:
            # sql = f"insert into HepsiEmlak({', '.join(self.lst_flds)}) VALUES ({(', ').join(['%s'] * len(self.lst_flds))})"
            sql = f"CALL pr_merge_emlak_data({', '.join(['%s'] * (1 + len(self.lst_flds)))})"
            self.curr.execute(sql, values)
        except BaseException as e:
            print(e)
            self.connection.rollback() # commit()
        self.connection.commit()

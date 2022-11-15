#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding=utf-8
import sys
from scrapy import cmdline
import psycopg2
def main(name):
    """connection = psycopg2.connect( host="localhost",   database="emlak",    user="postgres",       password="123")
    curr = connection.cursor()
    sql = f"CALL pr_merge_emlak_data(%s, %s, %s)"
    values = (1, '2022-11-05T07:50:02.993+0000',  'teststr')
    #  '2022-11-05T07:50:02.993+0000'
    try:
        curr.execute(sql, values)
    except BaseException as e:
        print(e)
        connection.commit()
    """
    if name:
        cmdline.execute(name.split())



if __name__ == '__main__':
    print('[*] beginning main thread')
    name = "scrapy crawl hepsiemlak"
    #name = "scrapy crawl spa"
    main(name)
    print('[*] main thread exited')
    print('main stop====================================================')
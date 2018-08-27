# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FileItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    content=scrapy.Field()
    id=scrapy.Field()
    fileid = scrapy.Field()
    filetype=scrapy.Field()
    end=scrapy.Field()
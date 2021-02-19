# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    book_name = scrapy.Field()  # 小说名
    book_author = scrapy.Field()  # 小说作者
    book_img = scrapy.Field()  # 小说图片url
    book_chapter = scrapy.Field()  # 小说章节


class ChapterItem(scrapy.Item):
    c_name = scrapy.Field()  # 章节名
    c_content = scrapy.Field()  # 章节内容
    c_index = scrapy.Field()  # 章节序号

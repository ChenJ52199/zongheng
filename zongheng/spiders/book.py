import re
from copy import deepcopy

import scrapy
from scrapy_redis.spiders import RedisSpider

from zongheng.items import BookItem, ChapterItem


class BookSpider(RedisSpider):
    name = 'book'
    allowed_domains = ['zongheng.com']
    # start_urls = ['http://book.zongheng.com/store/c0/c0/b0/u2/p1/v0/s9/t0/u0/i1/ALL.html']

    redis_key = 'zongheng:start_urls'

    def parse(self, response, **kwargs):
        div_list = response.xpath('//div[contains(@class,"bookbox")]')  # 当前页书籍分组
        for div in div_list:
            item = BookItem()
            item['book_name'] = div.xpath('.//div[@class="bookname"]/a/text()').extract_first()
            item['book_img'] = div.xpath('./div[@class="bookimg"]//img/@src').extract_first()

            book_url = div.xpath('./div/a/@href').extract_first()
            chapter_url = re.sub(r'/book/', '/showchapter/', book_url)  # 拼接小说章节url
            # print(item, chapter_url)
            yield scrapy.Request(
                url=chapter_url,
                callback=self.parse_chapter,
                meta={'item': item}
            )

    def parse_chapter(self, response):
        item = response.meta['item']
        chapter_list = response.xpath('//li[contains(@class,"col-4")]')  # 章节分组
        # print(len(chapter_list))
        book_chapter = ChapterItem()
        for index, chapter in enumerate(chapter_list):
            book_chapter['c_name'] = chapter.xpath('./a/text()').extract_first()
            book_chapter['c_index'] = index  # 章节序号 用来排序
            item['book_chapter'] = book_chapter
            url = chapter.xpath('./a/@href').extract_first()  # 章节内容url
            # print(book_chapter, url)
            yield scrapy.Request(
                url=url,
                callback=self.parse_chapter_content,
                meta={'item': deepcopy(item)}
            )

    def parse_chapter_content(self, response):
        item = response.meta['item']
        item['book_author'] = response.xpath('//div[@class="bookinfo"]/a[1]/text()').extract_first()
        book_chapter = item['book_chapter']
        book_chapter['c_content'] = response.xpath('//div[@class="content"]/p/text()').extract()
        # print(book_chapter['c_content'])
        yield item

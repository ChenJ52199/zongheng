# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class ZonghengPipeline(object):
    def __init__(self, mongo_url):
        self.mongo_url = mongo_url
        self.mongo_client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL', 'mongodb://127.0.0.1:27017')
        )

    # 爬虫开始时 建立与mongodb的连接
    def open_spider(self, spider):
        self.mongo_client = MongoClient(self.mongo_url)

    # 爬虫结束时 断开时与mongodb的连接
    def close_spider(self, spider):
        self.mongo_client.close()

    def process_item(self, item, spider):
        collection = self.mongo_client['zongheng']['book']
        # book_name = item.get('book_name')
        # book_author = item.get('book_author')
        book_chapter = item.get("book_chapter")
        item['book_chapter']['c_content'] = [p.strip() for p in item.get("book_chapter")['c_content']]
        # print(item)
        # { $push: {field: value}}
        # 把value追加到field里面去，field一定要是数组类型才行，如果field不存在，会新增一个数组类型加进去。
        # upsert: 可选，这个参数的意思是，如果不存在update的记录，是否插入objNew, true为插入，默认是false，不插入
        # collection.update({'book_name': book_name, 'book_author': book_author},
        #                   {'$push': {'book_content': book_chapter}},
        #                   upsert=True
        #                   )
        collection.insert_one(dict(item))
        return item

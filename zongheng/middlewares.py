# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random
from scrapy import signals
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from twisted.internet import defer
from twisted.internet.error import (
    ConnectError,
    ConnectionDone,
    ConnectionLost,
    ConnectionRefusedError,
    DNSLookupError,
    TCPTimedOutError,
    TimeoutError,
)
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.web.client import ResponseFailed


class ZonghengSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ZonghengDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.



    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomProxyMiddleware(object):
    '''添加随机代理ip'''

    EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def process_request(self, request, spider):
        # if request.meta['proxy'] is None and len(spider.settings['PROXIES']) > 0:  # 没有添加代理
        #     request.meta['proxy'] = random.choice(spider.settings['PROXIES'])
        redis_client = spider.server
        random_ip = redis_client.srandmember('ippool')  # 从redis集合中随机取一个ip
        if request.meta.get('proxy') is None and random_ip is not None:  # 没有添加代理
            request.meta['proxy'] = random_ip.decode()
            # print(random_ip.decode())
        return None

    def process_response(self, request, response, spider):
        redis_client = spider.server
        proxy = response.meta.get('proxy')
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            redis_client.srem('ippool', proxy)  # 将该ip移除
            spider.logger.warning('status:{},已经移除ip:{}'.format(response.status, proxy))
            request.meta['proxy'] = redis_client.srandmember('ippool').decode()
            return request
        return response

    def process_exception(self, request, exception, spider):
        redis_client = spider.server
        proxy = request.meta.get('proxy')
        if isinstance(exception, self.EXCEPTIONS):
            redis_client.srem('ippool', proxy)  # 将该ip移除
            spider.logger.warning('{},已经移除ip:{}'.format(exception.__class__, proxy))
            request.meta['proxy'] = redis_client.srandmember('ippool').decode()
            return request


class RandomUserAgentMiddleware(object):
    '''添加随机ua'''

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(spider.settings['USER_AGENTS'])
        # print(request.headers['User-Agent'])
        return None

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

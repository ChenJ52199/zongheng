import json
import requests
import re
from redis.client import StrictRedis


class IPPool(object):
    '''爬取芝麻http免费ip'''
    def __init__(self):
        self.url = 'http://wapi.http.linkudp.com/index/index/get_free_ip'
        self.redis_client = StrictRedis(host='127.0.0.1', port=6379)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        self.session = requests.Session()

    def run(self):
        for page in range(1, 485):
            data = {'page': page}
            response = self.session.post(self.url, data=data, headers=self.headers)
            print(response.status_code)
            html = json.loads(response.content.decode())['ret_data']['html']
            ip_list = re.findall(r'FREE</span>(.+?)</td>\s+<td>(\d+?)</td>', html)
            ip_list = ['http://' + i[0] + ':' + i[1] for i in ip_list]
            for ip in ip_list:
                print(ip)
                self.redis_client.sadd('ippool', ip)


if __name__ == '__main__':
    ippool = IPPool()
    ippool.run()

#coding=utf-8
import os
import sys
import time
import redis
import argparse
import traceback
from datetime import datetime as dt
import multiprocessing as mp
from requests.exceptions import ConnectionError
from template.weibo_config import (
    WEIBO_MANUAL_COOKIES, MANUAL_COOKIES,
    WEIBO_ACCOUNT_PASSWD, 
    TOPIC_URL_QUEUE, TOPIC_INFO_QUEUE,
    INSERT_TOPIC_TREND_SQL, UPDATE_TOPIC_INFO_SQL,
    QCLOUD_MYSQL, OUTER_MYSQL,
    LOCAL_REDIS, QCLOUD_REDIS
)
from template.weibo_utils import (
    create_processes,
    pick_rand_ele_from_list
)
from weibo_topic_spider import WeiboTopicSpider
from weibo_topic_writer import WeiboTopicWriter

reload(sys)
sys.setdefaultencoding('utf-8')

if os.environ.get('SPIDER_ENV') == 'test':
    print "*"*10, "Run in Test environment"
    USED_DATABASE = OUTER_MYSQL
    USED_REDIS = LOCAL_REDIS
elif 'centos' in os.environ.get('HOSTNAME'): 
    print "*"*10, "Run in Qcloud environment"
    USED_DATABASE = QCLOUD_MYSQL
    USED_REDIS = QCLOUD_REDIS
else:
    raise Exception("Unknown Environment, Check it now...")

TEST_CURL_SER = "curl 'http://d.weibo.com/' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: _T_WM=b5108fe62139dbea652e582ba82c646e; ALF=1484368852; SUB=_2A251Vm6EDeTxGeNH41ET-CjOyzqIHXVWuXLMrDV8PUJbkNAKLUPYkW1Ly1s2CfsPG3jr5fY4jA27TqVdnw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW9Bg.ND2DJ.Ju6Rxkffrks5NHD95Qf1Kn0eonceo5cWs4Dqcj_i--fiK.7i-z4i--fiKy8iKLWi--RiKn7i-i2i--RiKnfiK.Xi--Ri-z7iKyF; TC-Page-G0=444eec11edc8886c2f0ba91990c33cda' -H 'Connection: keep-alive' --compressed",


def single_process():
    cache = redis.StrictRedis(**USED_REDIS)
    topic_urls = [ 'http://weibo.com/p/1008080b5803ebf1ece02bbf800acf5d29ee8f', # yes
        'http://weibo.com/p/1008084c60a319140114840d49f2430755d111',  # yes
        'http://weibo.com/p/10080897355eedac5cbb1cdecb5870173678bb',  # no
        'http://weibo.com/p/1008080a206db80769f82677ac44a52aae6879',  # no
        'http://weibo.com/p/100808198be914d3c64217a2be33e043960a3c']  # no
    for url in topic_urls:
        account = 'liekeoth27678@163.com'
        # operate spider
        print url
        spider = WeiboTopicSpider(url, account, WEIBO_ACCOUNT_PASSWD, timeout=20)
        spider.use_abuyun_proxy()
        spider.add_request_header()
        spider.use_cookie_from_curl(cache.hget(MANUAL_COOKIES,account))
        # spider.use_cookie_from_curl(TEST_CURL_SER)
        spider.gen_html_source()
        print spider.parse_topic_info()


if __name__=="__main__":
    print "\n\n" + "%s Began Scraped Weibo Topics Details" % dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    start = time.time()
    single_process()
    print "*"*10, "Totally Scraped Weibo Topics Details Time Consumed : %d seconds" % (time.time() - start), "*"*10

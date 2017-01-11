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
from zc_spider.weibo_config import (
    MANUAL_COOKIES, WEIBO_ACCOUNT_PASSWD, 
    QCLOUD_MYSQL, OUTER_MYSQL,
    LOCAL_REDIS, QCLOUD_REDIS
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

test_curl = "curl 'http://weibo.com/p/1008085fa05adb030c898dd678ab10d0a9529f' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Referer: http://weibo.com/p/100808d3b71e51c1be37b7b4e5e15bdb8412b8' -H 'Cookie: SINAGLOBAL=7912212257618.43.1478585959985; wb_publish_fist100_5843638692=1; wvr=6; _T_WM=03e781554acf9dd24f1be01327a60a32; YF-Page-G0=d0adfff33b42523753dc3806dc660aa7; _s_tentry=-; Apache=9751347814485.37.1483668519299; ULV=1483668519511:25:3:3:9751347814485.37.1483668519299:1483508239455; YF-Ugrow-G0=8751d9166f7676afdce9885c6d31cd61; WBtopGlobal_register_version=c689c52160d0ea3b; SCF=Ap11mp4UEZs9ZcoafG0iD1wVDGjdyuPuLY8BpwtpvSEEvUHF2uToKM-7WlBpLkmhZ8RBzBoq6rkGPr6RQnLxkPM.; SUB=_2A251aoy0DeTxGeNG71EX8ybKwj6IHXVWAfl8rDV8PUNbmtANLXbhkW-Ca4XWBrg6Mlj9Y8JHL6ezeBXp4A..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5HA7SsRPVzLQ_q6ucc2n_c5JpX5K2hUgL.Fo-RShece0nc1Kz2dJLoI0YLxKqL1KMLBK5LxKqL1hnL1K2LxKBLBo.L12zLxK.L1KnLBoeLxKqL1KnL12-LxK-LBo5L1K2LxK-LBo.LBoBt; SUHB=0sqRRqxSCPeB1B; ALF=1484273507; SSOLoginState=1483668708; un=jiangzhibinking@outlook.com; YF-V5-G0=a9b587b1791ab233f24db4e09dad383c; UOR=,,zhiji.heptax.com' -H 'Connection: keep-alive' --compressed"


def single_process():
    topic_urls = [ 'http://weibo.com/p/100808d3b71e51c1be37b7b4e5e15bdb8412b8', # yes
        'http://weibo.com/p/1008088eb814c589f6596493c5bc81d2ccd941', # talk home
        'http://weibo.com/p/1008081ab76ecd3041acd3a572d5395d0e134c']
        # 'http://weibo.com/p/1008080a206db80769f82677ac44a52aae6879',  # no
        # 'http://weibo.com/p/100808198be914d3c64217a2be33e043960a3c']  # no
    for url in topic_urls:
        # account = 'liekeoth27678@163.com'
        # operate spider
        print url
        spider = WeiboTopicSpider(url, '', WEIBO_ACCOUNT_PASSWD, timeout=20)
        spider.use_abuyun_proxy()
        spider.add_request_header()
        # spider.use_cookie_from_curl(cache.hget(MANUAL_COOKIES,account))
        spider.use_cookie_from_curl(test_curl)
        status = spider.gen_html_source()
        if status in [404, 20003]:
            print '404 or 20003'
            continue
        elif 'talk_home' in spider.page and 'talk_home' not in url:
            print 'Talk home'
            topic_urls.append(url+'/talk_home')
            continue
        for k, v in spider.parse_topic_info().items():
            print '(key)%s : (value)%s' % (k, v)
        print "=="*40


if __name__=="__main__":
    print "\n\n" + "%s Began Scraped Weibo Topics Details" % dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    start = time.time()
    single_process()
    print "*"*10, "Totally Scraped Weibo Topics Details Time Consumed : %d seconds" % (time.time() - start), "*"*10

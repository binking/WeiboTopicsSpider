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

TEST_CURL_SER = "curl 'http://d.weibo.com/' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: _T_WM=52765f5018c5d34c5f77302463042cdf; ALF=1484204272; SUB=_2A251S-ugDeTxGeNH41cV8CbLyTWIHXVWt_XorDV8PUJbkNAKLWbBkW0_fe7_8gLTd0veLjcMNIpRdG9dKA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhZLMdo2m4y1PHxGYdNTkzk5JpX5oz75NHD95Qf1KnfSh5RS0z4Ws4Dqcj_i--ciKLsi-z0i--RiK.pi-2pi--ci-zfiK.0i--fi-zEi-zRi--ciKy2i-2E; TC-Page-G0=cdcf495cbaea129529aa606e7629fea7' -H 'Connection: keep-alive' --compressed"

def generate_info(cache1, cache2):
    """
    Producer for users(cache1) and follows(cache2), Consummer for topics
    """
    cp = mp.current_process()
    while True:
        sql = ''
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Generate Follow Process pid is %d" % (cp.pid)
        job = cache1.blpop(TOPIC_URL_QUEUE, 0)[1]   # blpop 获取队列数据
        try:
            all_account = cache1.hkeys(MANUAL_COOKIES)
            if not all_account:  # no any weibo account
                raise Exception('All of your accounts were Freezed')
            account = pick_rand_ele_from_list(all_account)
            # operate spider
            spider = WeiboTopicSpider(job, account, WEIBO_ACCOUNT_PASSWD, timeout=20)
            spider.use_abuyun_proxy()
            spider.add_request_header()
            spider.use_cookie_from_curl(cache1.hget(MANUAL_COOKIES,account))
            # spider.use_cookie_from_curl(TEST_CURL_SER)
            spider.gen_html_source()
            info = spider.parse_topic_info()
            if info:
                if not(info.get('read_num') and info.get('dis_num') and info.get('fans_num')):
                    print "Invalid data(No three numbers) for uri: %s" % info['topic_url']
                    continue
                trend_sql = INSERT_TOPIC_TREND_SQL.format(
                    url=info['topic_url'], date=info['access_time'],
                    read=info.get('read_num', ''), read_dec=info.get('read_num_dec', 0),
                    disc=info.get('dis_num', ''), fans=info.get('fans_num', ''),
                    image=info['image_url']
                )
                topic_sql = UPDATE_TOPIC_INFO_SQL.format(
                    title=info['title'], intro=info['guide'],
                    read=info.get('read_num', ''), read_dec=info.get('read_num_dec', 0),
                    disc=info.get('dis_num', ''), fans=info.get('fans_num', ''),
                    type=info.get('type', ''), region=info.get('region', ''),
                    label=info.get('label', ''), url=info['topic_url'],
                    image=info['image_url']
                )
                # format sql and push them into result queue
                cache2.rpush(TOPIC_INFO_QUEUE, '%s||%s' % (trend_sql, topic_sql))  # push ele to the tail
        except Exception as e:  # no matter what was raised, cannot let process died
            cache1.rpush(TOPIC_URL_QUEUE, job) # put job back
            print 'Raised in gen process', str(e)
        except KeyboardInterrupt as e:
            break


def write_data(cache):
    """
    Consummer for topics
    """
    cp = mp.current_process()
    dao = WeiboTopicWriter(USED_DATABASE)
    while True:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Write Follow Process pid is %d" % (cp.pid)
        res = cache.blpop(TOPIC_INFO_QUEUE, 0)[1]
        try:
            trend_sql, topic_sql = res.split('||')
            dao.update_topics_into_db(trend_sql, topic_sql)
        except Exception as e:  # won't let you died
            print 'Raised in write process', str(e)
            cache.rpush(TOPIC_INFO_QUEUE, res)
        except KeyboardInterrupt as e:
            break
            

def add_jobs(cache):
    todo = 0
    dao = WeiboTopicWriter(USED_DATABASE)
    jobs = dao.read_topic_url_from_db()
    for job in jobs:  # iterate
        todo += 1
        try:
            all_account = cache.hkeys(MANUAL_COOKIES)
            cache.rpush(TOPIC_URL_QUEUE, job)
            if todo > 2:
                break
        except Exception as e:
            print e
    return todo


def run_all_worker():
    job_cache = redis.StrictRedis(**USED_REDIS)  # list
    # result_cache = redis.StrictRedis(**USED_REDIS)  # list
    job_pool = mp.Pool(processes=4,
        initializer=generate_info, initargs=(job_cache, job_cache))
    result_pool = mp.Pool(processes=8, 
        initializer=write_data, initargs=(job_cache, ))

    cp = mp.current_process()
    print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Run All Works Process pid is %d" % (cp.pid)
    try:
        create_processes(add_jobs, (job_cache, ), 1)
        job_pool.close()
        result_pool.close()
        job_pool.join()
        result_pool.join()
        print "+"*10, "jobs' length is ", job_cache.llen(TOPIC_URL_QUEUE) #jobs.llen(TOPIC_URL_QUEUE)
        print "+"*10, "results' length is ", job_cache.llen(TOPIC_INFO_QUEUE) #jobs.llen(TOPIC_URL_QUEUE)
    except Exception as e:
        traceback.print_exc()
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Exception raise in runn all Work"
    except KeyboardInterrupt:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Interrupted by you and quit in force, but save the results"
        print "+"*10, "jobs' length is ", job_cache.llen(TOPIC_URL_QUEUE) #jobs.llen(TOPIC_URL_QUEUE)
        print "+"*10, "results' length is ", job_cache.llen(TOPIC_INFO_QUEUE) #jobs.llen(TOPIC_URL_QUEUE)


if __name__=="__main__":
    print "\n\n" + "%s Began Scraped Weibo Topics Details" % dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    start = time.time()
    run_all_worker()
    # single_process()
    print "*"*10, "Totally Scraped Weibo Topics Details Time Consumed : %d seconds" % (time.time() - start), "*"*10

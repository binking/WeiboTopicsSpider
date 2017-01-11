#coding=utf-8
import os
import sys
import time
import redis
import random
import pickle
import argparse
import traceback
from datetime import datetime as dt
import multiprocessing as mp
from requests.exceptions import ConnectionError
from zc_spider.weibo_utils import RedisException
from zc_spider.weibo_config import (
    TOPIC_COOIKES,
    WEIBO_ERROR_TIME, WEIBO_ACCESS_TIME,
    WEIBO_ACCOUNT_PASSWD, WEIBO_CURRENT_ACCOUNT,
    TOPIC_URL_CACHE, TOPIC_INFO_CACHE,
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

TEST_CURL_SER = "curl 'http://d.weibo.com/' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: _T_WM=52765f5018c5d34c5f77302463042cdf; ALF=1484204272; SUB=_2A251S-ugDeTxGeNH41cV8CbLyTWIHXVWt_XorDV8PUJbkNAKLWbBkW0_fe7_8gLTd0veLjcMNIpRdG9dKA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhZLMdo2m4y1PHxGYdNTkzk5JpX5oz75NHD95Qf1KnfSh5RS0z4Ws4Dqcj_i--ciKLsi-z0i--RiK.pi-2pi--ci-zfiK.0i--fi-zEi-zRi--ciKy2i-2E; TC-Page-G0=cdcf495cbaea129529aa606e7629fea7' -H 'Connection: keep-alive' --compressed"
CURRENT_ACCOUNT = ''

def init_current_account(cache):
    print 'Initializing weibo account'
    global CURRENT_ACCOUNT
    CURRENT_ACCOUNT = cache.hkeys(TOPIC_COOIKES)[0]
    print '1', CURRENT_ACCOUNT
    if not cache.get(WEIBO_CURRENT_ACCOUNT):
        cache.set(WEIBO_CURRENT_ACCOUNT, CURRENT_ACCOUNT)
        cache.set(WEIBO_ACCESS_TIME, 0)
        cache.set(WEIBO_ERROR_TIME, 0)
    

def switch_account(cache):
    global CURRENT_ACCOUNT
    if cache.get(WEIBO_ERROR_TIME) and int(cache.get(WEIBO_ERROR_TIME)) > 9999:  # error count
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), 'Swithching weibo account'
        expired_account = cache.get(WEIBO_CURRENT_ACCOUNT)
        access_times = cache.get(WEIBO_ACCESS_TIME)
        error_times = cache.get(WEIBO_ERROR_TIME)
        print "Account(%s) access %s times but failed %s times" % (expired_account, access_times, error_times)
        cache.hdel(TOPIC_COOIKES, expired_account)
        if len(cache.hkeys(TOPIC_COOIKES)) == 0:
            cache.delete(WEIBO_CURRENT_ACCOUNT)
            cache.set(WEIBO_ACCESS_TIME, 0)
            cache.set(WEIBO_ERROR_TIME, 0)
            raise RedisException('All Weibo Accounts were run out of')
        else:
            new_account = cache.hkeys(TOPIC_COOIKES)[0]
        # init again
        cache.set(WEIBO_CURRENT_ACCOUNT, new_account)
        cache.set(WEIBO_ACCESS_TIME, 0)
        cache.set(WEIBO_ERROR_TIME, 0)
        CURRENT_ACCOUNT = new_account
    elif cache.get(WEIBO_CURRENT_ACCOUNT):
        CURRENT_ACCOUNT = cache.get(WEIBO_CURRENT_ACCOUNT)
    else:
        raise Exception('Unknown Account Error')


def generate_info(cache):
    """
    Producer for users(cache) and follows(cache), Consummer for topics
    """
    error_count = 0
    cp = mp.current_process()
    while True:
        sql = ''
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Generate Follow Process pid is %d" % (cp.pid)
        if error_count > 999:
            print '>'*20, '1000 times of gen ERRORs, quit','<'*20
            break
        job = cache.blpop(TOPIC_URL_CACHE, 0)[1]   # blpop 获取队列数据
        try:
            all_account = cache.hkeys(TOPIC_COOIKES)
            account = random.choice(all_account)
            spider = WeiboTopicSpider(job, account, WEIBO_ACCOUNT_PASSWD, timeout=20)
            spider.use_abuyun_proxy()
            # spider.add_request_header()
            spider.use_cookie_from_curl(cache.hget(TOPIC_COOIKES, account))
            status = spider.gen_html_source()
            if status in [404, 20003]:
                print '404 or 20003'
                continue
            elif 'talk_home' in spider.page and 'talk_home' not in job:
                print 'Talk home'
                cache.rpush(TOPIC_URL_CACHE, job+'/talk_home')
                continue
            info = spider.parse_topic_info()
            if info:
                if not(info.get('read_num') and info.get('dis_num') and info.get('fans_num')):
                    print "Invalid data(No three numbers) for uri: %s" % info['topic_url']
                elif len(info) > 4:
                    cache.rpush(TOPIC_INFO_CACHE, pickle.dumps(info))  # push ele to the tail
        except RedisException as e:
            print e
            break
        except Exception as e:  # no matter what was raised, cannot let process died
            print str(e)
            cache.rpush(TOPIC_URL_CACHE, job) # put job back
            print 'Failed to parse job: %s' % job
            error_count += 1
       

def write_data(cache):
    """
    Consummer for topics
    """
    cp = mp.current_process()
    error_count = 0
    dao = WeiboTopicWriter(USED_DATABASE)
    while True:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Write Follow Process pid is %d" % (cp.pid)
        if error_count > 999:
            print '>'*20, '1000 times of write ERRORs, quit','<'*20
            break
        res = cache.blpop(TOPIC_INFO_CACHE, 0)[1]
        try:
            dao.update_topics_into_db(pickle.loads(res))
        except Exception as e:  # won't let you died
            print 'Failed to write result: %s' % pickle.loads(res)
            cache.rpush(TOPIC_INFO_CACHE, res)
            error_count += 1
        except KeyboardInterrupt as e:
            break
            

def add_jobs(cache):
    todo = 0
    dao = WeiboTopicWriter(USED_DATABASE)
    for job in dao.read_topic_url_from_db():
        todo += 1
        try:
            cache.rpush(TOPIC_URL_CACHE, job)
        except Exception as e:
            print e
    print 'There are totally %d jobs to process' % todo
    return todo


def run_all_worker():
    r = redis.StrictRedis(**USED_REDIS)  # list
    if not r.llen(TOPIC_URL_CACHE):
        add_jobs(r)
        print 'Add jobs done, I quit...'
        return 0
    else:
        print "Redis has %d records in cache" % r.llen(TOPIC_URL_CACHE)
    # init_current_account(r)
    job_pool = mp.Pool(processes=8,
        initializer=generate_info, initargs=(r, ))
    result_pool = mp.Pool(processes=4, 
        initializer=write_data, initargs=(r, ))

    cp = mp.current_process()
    print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Run All Works Process pid is %d" % (cp.pid)
    try:
        job_pool.close()
        result_pool.close()
        job_pool.join()
        result_pool.join()
        print "+"*10, "jobs' length is ", r.llen(TOPIC_URL_CACHE) #jobs.llen(TOPIC_URL_CACHE)
        print "+"*10, "results' length is ", r.llen(TOPIC_INFO_CACHE) #jobs.llen(TOPIC_URL_CACHE)
    except Exception as e:
        traceback.print_exc()
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Exception raise in runn all Work"
    except KeyboardInterrupt:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Interrupted by you and quit in force, but save the results"
        print "+"*10, "jobs' length is ", r.llen(TOPIC_URL_CACHE) #jobs.llen(TOPIC_URL_CACHE)
        print "+"*10, "results' length is ", r.llen(TOPIC_INFO_CACHE) #jobs.llen(TOPIC_URL_CACHE)


if __name__=="__main__":
    print "\n\n" + "%s Began Scraped Weibo Topics Details" % dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    start = time.time()
    run_all_worker()
    print "*"*10, "Totally Scraped Weibo Topics Details Time Consumed : %d seconds" % (time.time() - start), "*"*10

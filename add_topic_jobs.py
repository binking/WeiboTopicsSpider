#-*- coding: utf-8 -*-
#--------  Update话题  --------
import os
import sys
import time
import redis
from datetime import datetime as dt
from zc_spider.weibo_config import (
    TOPIC_URL_CACHE,  # weibo:blog:urls
    QCLOUD_MYSQL, OUTER_MYSQL,
    LOCAL_REDIS, QCLOUD_REDIS
)
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


def add_jobs(target):
    todo = 0
    dao = WeiboTopicWriter(USED_DATABASE)
    for job in dao.read_topic_url_from_db():  # iterate
        todo += 1
        if target.lrem(TOPIC_URL_CACHE, 0, job):
            # the job had existed in the queue
            target.lpush(TOPIC_URL_CACHE, job)
        else:
            target.rpush(TOPIC_URL_CACHE, job)
    print 'There are totally %d jobs to process' % todo
    return todo

if __name__=='__main__':
    print "\n\n" + "%s Began Scraped Weibo Tweets" % dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    start = time.time()
    r = redis.StrictRedis(**USED_REDIS)
    add_jobs(r)
    print "*"*10, "Totally Scraped Weibo Tweets Time Consumed : %d seconds" % (time.time() - start), "*"*10

"""
33 */3 * * * . /etc/profile; cd /home/jiangzhibin/PythonProgramming/ZhicangSpiders/WeiboTopicsSpider;  /home/jiangzhibin/PythonProgramming/ZhicangSpiders/spider_env/bin/python add_topic_jobs.py >> ./log/add_topic_jobs.log 2>&1
"""
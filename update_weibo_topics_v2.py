#coding=utf-8
import sys
import time
import redis
import argparse
import traceback
from datetime import datetime as dt
import multiprocessing as mp
from requests.exceptions import ConnectionError
from config.weibo_config import (
    OUTER_MYSQL,
    WEIBO_ACCOUNT_LIST, 
    WEIBO_ACCOUNT_PASSWD, 
    ACTIVATED_COOKIE,
    REDIS_SETTING,
)
from utils.weibo_utils import (
    create_processes,
    pick_rand_ele_from_list
)
from weibo_topic_spider import WeiboTopcSpider
from dao.weibo_writer import WeiboTopicWriter


reload(sys)
sys.setdefaultencoding('utf-8')


def topic_info_generator(jobs, results, rconn):
    """
    Producer for urls and topics, Consummer for topics
    """
    cp = mp.current_process()
    while True:
        info = {}
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Generate Topic Process pid is %d" % (cp.pid)
        topic_url = jobs.get()
        all_account = rconn.hkeys(ACTIVATED_COOKIE)
        if not all_account:  # no any weibo account
            print 'All of your accounts were Freezed'
            break
        auth = pick_rand_ele_from_list(all_account)
        account, pwd = auth.split('--')
        spider = WeiboTopcSpider(topic_url, account, pwd)
        spider.use_abuyun_proxy()
        spider.add_request_header()
        spider.read_cookie(rconn)
        try:
            spider.gen_html_source()
        except ConnectionError as e:
            print str(e)
            jobs.put(topic_url)
        if spider.check_abnormal_status():
            print 'Oh baby baby, your account was blocked. '
            spider.remove_cookie(rconn)
        else:
            info = spider.parse_topic_info()
        if info and len(info) > 2:  # except access_time and url
            results.put(info)
        jobs.task_done()


def topic_db_writer(results):
    """
    Consummer for topics
    """
    cp = mp.current_process()
    dao = WeiboTopicWriter(OUTER_MYSQL)
    while True:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Write Topics Process pid is %d" % (cp.pid)
        info = results.get()
        dao.update_topics_into_db(info)
        results.task_done()


def add_jobs(target, start_date, end_date, interval):
    todo = 0
    dao = WeiboTopicWriter(OUTER_MYSQL)
    topics = dao.read_topic_url_from_db(start_date=start_date, end_date=end_date, interval=interval)
    if not topics:
        return -1
    for t in topics:
        todo += 1
        target.put(t)
        # if todo > 9:
        #    break
    return todo

def run_all_worker(date_start, date_end, days_inter):
    try:
        # load weibo account into redis cache
        r = redis.StrictRedis(**REDIS_SETTING)
        # init_cookie(r)
        # Producer is on !!!
        jobs = mp.JoinableQueue()
        results = mp.JoinableQueue()
        create_processes(topic_info_generator, (jobs, results, r), 4)
        create_processes(topic_db_writer, (results,), 8)

        cp = mp.current_process()
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Run All Works Process pid is %d" % (cp.pid)
        num_of_topics = add_jobs(target=jobs, start_date=date_start, 
            end_date=date_end, interval=days_inter
        )
        print "<"*10, 
        print "There are %d topics to process" % (num_of_topics), 
        print ">"*10
        jobs.join()
        results.join()

        print "+"*10, "jobs' length is ", jobs.qsize()
        print "+"*10, "results' length is ", results.qsize()
    except Exception as e:
        traceback.print_exc()
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Exception raise in runn all Work"
    except KeyboardInterrupt:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Interrupted by you and quit in force, but save the results"


def test(date_start, date_end, days_inter):
    rconn = redis.StrictRedis(**REDIS_SETTING)
    dao = WeiboTopicWriter(OUTER_MYSQL)
    for topic_url in dao.read_topic_url_from_db(date_start, date_end, days_inter):
        all_account = rconn.hkeys(ACTIVATED_COOKIE)
        if not all_account:  # no any weibo account
            raise Exception('All of your accounts were Freezed')
        account, pwd = pick_rand_ele_from_list(all_account).split("--")
        spider = WeiboTopcSpider(topic_url, account, pwd)
        spider.use_abuyun_proxy()
        spider.read_cookie(rconn)
        spider.add_request_header()
        try:
            spider.gen_html_source()
        except ConnectionError as e:
            pass
        if spider.check_abnormal_status():
            print 'Oh baby baby, your account was blocked. '
            spider.remove_cookie(rconn)
        else:
            info = spider.parse_topic_info()

if __name__=="__main__":
    print "\n" + "%s Began Update Weibo Topics" % dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    start = time.time()
    parser = argparse.ArgumentParser(description='Select date interval to update topics.')
    parser.add_argument('--from', dest='start', help='start date')
    parser.add_argument('--to', dest='end', help='end date')
    parser.add_argument('--inter', dest='interval', type=int, help='default from 7 days ago')
    args = parser.parse_args()
    if args.start or args.end or args.interval:
        run_all_worker(date_start=args.start, date_end=args.end, days_inter=args.interval)
        # test(date_start=args.start, date_end=args.end, days_inter=args.interval)
    else:
        parser.print_usage()
    # test_parse_baidu_results()
    print "*"*10, "Totally Update Weibo Topics Time Consumed : %d seconds" % (time.time() - start), "*"*10

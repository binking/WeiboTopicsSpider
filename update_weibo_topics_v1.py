#coding=utf-8
import sys
import time
import argparse
import traceback
from datetime import datetime as dt
import multiprocessing as mp
from decrators import catch_database_error
from utils import create_processes
from weibo_topics_spider import extract_topic_info
from database_operator import read_topic_url_from_db, update_topics_into_db

reload(sys)
sys.setdefaultencoding('utf-8')


def topic_info_generator(topic_jobs, topic_results):
    """
    Producer for urls and topics, Consummer for topics
    """
    cp = mp.current_process()
    while True:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Generate Urls Process pid is %d" % (cp.pid)
        topic_url = topic_jobs.get()
        print 'Parsing ', topic_url
        info_dict = extract_topic_info(topic_url)
        if len(info_dict) > 2:  # except access_time and url
            topic_results.put(info_dict)
        topic_jobs.task_done()
    

def topic_db_writer(topic_results):
    """
    Consummer for topics
    """
    cp = mp.current_process()
    while True:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Write Topics Process pid is %d" % (cp.pid)
        info_dict = topic_results.get()
        print 'Writing ', info_dict['topic_url']
        write_status = update_topics_into_db(info_dict)
        topic_results.task_done()
        

def add_topic_jobs(target, start_date, end_date, interval):
    todo = 0
    list_of_kw = read_topic_url_from_db(start_date=start_date, end_date=end_date, interval=interval)
    if not list_of_kw:
        return -1
    for kw in list_of_kw:
        todo += 1
        target.put(kw)
    return todo


def run_all_worker(date_start, date_end, days_inter):
    try:
        # Producer is on !!!
        topic_jobs = mp.JoinableQueue()
        topic_results = mp.JoinableQueue()
        create_processes(topic_info_generator, (topic_jobs, topic_results), 1)
        create_processes(topic_db_writer, (topic_results,), 2)

        cp = mp.current_process()
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Run All Works Process pid is %d" % (cp.pid)
        num_of_topics = add_topic_jobs(target=topic_jobs, 
            start_date=date_start, 
            end_date=date_end, 
            interval=days_inter
        )
        print "<"*10, 
        print "There are %d topics to process" % (num_of_topics), 
        print ">"*10
        topic_jobs.join()
        topic_results.join()

        print "+"*10, "topic_jobs' length is ", topic_jobs.qsize()
        print "+"*10, "topic_results' length is ", topic_results.qsize()
    except Exception as e:
        traceback.print_exc()
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Exception raise in runn all Work"
    except KeyboardInterrupt:
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Interrupted by you and quit in force, but save the results"


def test():
    test_uris = ['http://weibo.com/p/1008085c488e8064b0c99acbb919d7870ccddd']
    for i, url in enumerate(test_uris):
        print i, url
        topic_info = extract_topic_info(url)
        if len(topic_info) > 2:
            update_topics_into_db(topic_info)
        if i > 1:
            break


if __name__=="__main__":
    print "\n" + "%s Began Update Weibo Topics" % dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    start = time.time()
    parser = argparse.ArgumentParser(description='Select date interval to update topics.')
    parser.add_argument('--from', dest='start', help='start date')
    parser.add_argument('--to', dest='end', help='end date')
    parser.add_argument('--inter', dest='interval', type=int, help='default from 7 days ago')
    args = parser.parse_args()
    run_all_worker(date_start=args.start, date_end=args.end, days_inter=args.interval)
    # test_parse_baidu_results()
    print "*"*10, "Totally Update Weibo Topics Time Consumed : %d seconds" % (time.time() - start), "*"*10

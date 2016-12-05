#coding=utf-8
import sys
import time
import random
import sqlite3
import traceback
from datetime import datetime as dt, timedelta
import MySQLdb as mdb
from decrators import catch_database_error
from config import MAIL_CURL_DICT
reload(sys)
sys.setdefaultencoding('utf-8')


OUTER_MYSQL = {
    'host': '582af38b773d1.bj.cdb.myqcloud.com',
    'port': 14811,
    'db': 'webcrawler',
    'user': 'web',
    'passwd': "Crawler20161231",
    'charset': 'utf8',
    'connect_timeout': 20,
}

QCLOUD_LOCAL_MYSQL = {
    'host': '10.66.110.147',
    'port': 3306,
    'db': 'webcrawler',
    'user': 'web',
    'passwd': "Crawler20161231",
    'charset': 'utf8',
    'connect_timeout': 20,
}


def connect_database():
    """
    We can't fail in connect database, which will make the subprocess zoombie
    """
    attempt = 1
    for _ in range(16):
        seconds = 3*attempt
        try:
            WEBCRAWLER_DB_CONN = mdb.connect(**QCLOUD_LOCAL_MYSQL)
            # WEBCRAWLER_DB_CONN = mdb.connect(**OUTER_MYSQL)
            return WEBCRAWLER_DB_CONN
        except mdb.OperationalError as e:
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Sleep %s seconds cuz we can't connect MySQL..." % seconds
        except Exception as e:
            traceback.print_exc()
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Sleep %s cuz unknown connecting database error." % seconds
        attempt += 1
        time.sleep(seconds)
        print "@"*10, "Connecting database at %d-th time..." % attempt
   

@catch_database_error
def update_topics_into_db(info_dict):
    """
    info_dict(dict) = {
        topic_url:,
        access_time:,
        read_num(utf-8, Chinese number):,
        dis_num:,
        fans_num:,
        guide:,
        image_url:,
    }
    """
    if not(info_dict.get('read_num') and info_dict.get('dis_num') and info_dict.get('fans_num')):
        print "Invalid data for uri: %s" % info_dict['topic_url']
        return True
    insert_trend_sql = """
        INSERT INTO topictrend (topic_url, crawl_dt, read_num, read_num_dec, discussion_num, fans_num, logo_img_url) 
        SELECT %s, %s, %s, %s, %s, %s, %s
        FROM DUAL WHERE NOT EXISTS (
        SELECT * FROM topictrend 
        WHERE topic_url = %s AND crawl_dt = %s)
    """
    update_info_sql = """
        UPDATE topicinfo 
        set title=%s, introduction=%s, read_num=%s, read_num_dec=%s, discussion_num=%s, fans_num=%s, topic_type=%s, topic_region=%s, label=%s, topic_url=%s, logo_img_url=%s
        WHERE topic_url=%s
    """
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(insert_trend_sql, (
        info_dict['topic_url'],
        info_dict['access_time'],
        info_dict.get('read_num', ''),
        info_dict.get('read_num_dec', 0),
        info_dict.get('dis_num', ''),
        info_dict.get('fans_num', ''),
        info_dict.get('image_url', ''),
        info_dict['topic_url'],
        info_dict['access_time']
    ))

    cursor.execute(update_info_sql, (
        info_dict['title'],
        info_dict['guide'],
        info_dict.get('read_num', ''),
        info_dict.get('read_num_dec', 0),
        info_dict.get('dis_num', ''),
        info_dict.get('fans_num', ''),
        info_dict.get('type', ''),
        info_dict.get('region', ''),
        info_dict.get('label', ''),
        info_dict['topic_url'],
        info_dict['image_url'],
        info_dict['topic_url']
    ))
    conn.commit()
    print 'Writing topic %s DONE !!!' % info_dict['topic_url']
    cursor.close()
    conn.close()


@catch_database_error
def read_topic_url_from_db(start_date, end_date, interval=7):
    """
    read the urls of topic from db. return iterator object
    """
    select_topic_sql = """
        SELECT DISTINCT topic_url FROM topicinfo
        -- WHERE theme LIKE '新浪微博_热门话题%'
        where createdate > '{fr}'
        and createdate < '{to}'
        ORDER BY createdate DESC 
    """
    if interval:
        days_ago = (dt.today() - timedelta(interval)).strftime("%Y-%m-%d")
        next_day = (dt.today() + timedelta(1)).strftime("%Y-%m-%d")
        select_topic = select_topic_sql.format(fr=days_ago, to=next_day)
    else:
        select_topic = select_topic_sql.format(fr=start_date, to=end_date)
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(select_topic)  # filter by date: >_< , include >, exclude <

    for res in cursor.fetchall():
        yield res[0]


def pick_cookie_from_sqlite(db_file):
    # db_name = 'cookies.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM cookies
        WHERE is_freezed='N'
    """)
    c_id = random.randint(0, len(fetchall()) - 1)
    cursor.execute("""
        SELECT cookie FROM cookies
        WHERE id=%s
    """, (c_id, ))
    return cursor.fetchone()[0]


def create_sqlite_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE cookies (
        id varchar(10) primary key, 
        mail varchar(20),
        cookie text,
        is_freezed varchar(5) default 'N')
    """)
    for key in MAIL_CURL_DICT:
        cursor.execute("""
            INSERT INTO cookies
            (mail, cookie)
            values (%s, %s)
        """, (key, MAIL_CURL_DICT[key]))
    cursor.close()
    conn.commit()
    conn.close()

def expired_cookie(db_file, mail):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE TABLE cookies
        SET is_freezed='Y'
        WHERE mail=%s
    """, (mail, ))
    cursor.close()
    conn.commit()
    conn.close()
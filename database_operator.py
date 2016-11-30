#coding=utf-8
import sys
import time
import traceback
from datetime import datetime as dt, timedelta
import MySQLdb as mdb
from decrators import catch_database_error
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
            WEBCRAWLER_DB_CONN = mdb.connect(**OUTER_MYSQL)
            # print '$'*10, 'Connected database succeeded...'
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
    insert_trend_sql = """
        INSERT INTO topictrend (topic_url, crawl_dt, read_num, discussion_num, fans_num, logo_img_url) 
        SELECT '{url}', '{date}', '{read}', '{dis}', '{fans}', '{img}'
        FROM DUAL WHERE NOT EXISTS (
        SELECT * FROM topictrend 
        WHERE topic_url = '{url}' AND crawl_dt = '{date}')
    """
    update_info_sql = """
        UPDATE topicinfo 
        set title='{title}', introduction='{guide}', read_num='{read}', discussion_num='{dis}', fans_num='{fans}', topic_url='{url}', logo_img_url='{img}'
        WHERE topic_url='{url}'
    """
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(insert_trend_sql.format(
        url=info_dict['topic_url'],
        date=info_dict.get('access_time', ''),
        read=info_dict.get('read_num', ''),
        dis=info_dict.get('dis_num', ''),
        fans=info_dict.get('fans_num', ''),
        img=info_dict.get('image_url', ''),
    ))

    cursor.execute(update_info_sql.format(
        title=info_dict['title'],
        url=info_dict['topic_url'],
        guide=info_dict.get('guide', ''),
        read=info_dict.get('read_num', ''),
        dis=info_dict.get('dis_num', ''),
        fans=info_dict.get('fans_num', ''),
        img=info_dict.get('image_url', ''),
    ))

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

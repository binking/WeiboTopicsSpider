#coding=utf-8
import sys
import time
import traceback
from datetime import datetime as dt
import MySQLdb as mdb
from zc_spider.weibo_writer import DBAccesor, database_error_hunter

reload(sys)
sys.setdefaultencoding('utf-8')

class WeiboTopicWriter(DBAccesor):

    def __init__(self, db_dict):
        DBAccesor.__init__(self, db_dict)

    def connect_database(self):
        return DBAccesor.connect_database(self)

    def update_topics_into_db(self, info):
        """
        info(dict) = {topic_url:, access_time:, read_num(utf-8, Chinese number):,
            dis_num:, fans_num:, guide:, image_url:, }
        """
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
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute(insert_trend_sql, (
            info['topic_url'], info['access_time'],
            info.get('read_num', ''), info.get('read_num_dec', 0),
            info.get('dis_num', ''), info.get('fans_num', ''),
            info.get('image_url', ''), info['topic_url'],
            info['access_time']
        ))
        cursor.execute(update_info_sql, (
            info['title'], info['guide'],
            info.get('read_num', ''), info.get('read_num_dec', 0),
            info.get('dis_num', ''), info.get('fans_num', ''),
            info.get('type', ''), info.get('region', ''),
            info.get('label', ''), info['topic_url'],
            info['image_url'], info['topic_url']
        ))
        print 'Writed topic and trend DONE(%s)!!!' % info['topic_url']
        conn.commit(); cursor.close(); conn.close()

    @database_error_hunter
    def read_topic_url_from_db(self):  #, start_date, end_date, interval=7):
        """
        read the urls of topic from db. return iterator object
        """
        # select_topic_sql = """
        #     SELECT DISTINCT topicurl FROM topicanalysis.topic t 
        #     WHERE 1 = 1 AND createdate > date_sub(NOW(), INTERVAL 30 DAY )
        #     AND is_active = 1
        # """
        select_topic_sql = """
            SELECT DISTINCT topic_url FROM topicinfo 
            -- WHERE  theme LIKE '新浪微博_热门话题%' 
            WHERE createdate > date_sub(NOW(), INTERVAL 5 DAY )
            -- Update 5 days' Topics Detail pre day
        """
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute(select_topic_sql)  # filter by date: >_< , include >, exclude <
        for res in cursor.fetchall():
            yield res[0]
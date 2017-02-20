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
            INSERT INTO WeiboTrend (topic_url, crawl_dt, read_num, read_num_dec, discussion_num, fans_num, logo_img_url) 
            SELECT %s, %s, %s, %s, %s, %s, %s
            FROM DUAL WHERE NOT EXISTS (
            SELECT * FROM WeiboTrend 
            WHERE topic_url = %s AND crawl_dt = %s)
        """
        update_info_sql_1 = """
            UPDATE weibotopic 
            set title=%s, introduction=%s, read_num=%s, read_num_dec=%s, 
            discussion_num=%s, fans_num=%s, topic_type=%s, topic_region=%s, 
            label=%s, topic_url=%s, logo_img_url=%s
            WHERE topic_url=%s
        """
        Topicinfo(createdate, title, logo_img_url, label, introduction, topic_type, 
keywords, event_class)
        update_info_sql_2 = """
            UPDATE Topicinfo 
            set introduction=%s, topic_type=%s, topic_region=%s, label=%s, logo_img_url=%s
            WHERE title=%s
        """
        conn = self.connect_database()
        cursor = conn.cursor()
        try:
            if not info.get('guide', ''):
                print info
            cursor.execute(insert_trend_sql, (
                info['topic_url'], info['access_time'],
                info.get('read_num', ''), info.get('read_num_dec', 0),
                info.get('dis_num', ''), info.get('fans_num', ''),
                info.get('image_url', ''), info['topic_url'],
                info['access_time']
            ))
            cursor.execute(update_info_sql_1, (
                info['title'], info.get('guide', ''),
                info.get('read_num', ''), info.get('read_num_dec', 0),
                info.get('dis_num', ''), info.get('fans_num', ''),
                info.get('type', ''), info.get('region', ''),
                info.get('label', ''), info['topic_url'],
                info['image_url'], info['topic_url']
            ))
            cursor.execute(update_info_sql_2, (
                info.get('guide', ''), info.get('type', ''), 
                info.get('region', ''), info.get('label', ''),
                info['image_url'], info['title']
            ))
            print 'Writed topic and trend DONE(%s)!!!' % info['title']
            conn.commit(); cursor.close(); conn.close()
        except Exception as e:
            traceback.print_exc()
            conn.commit(); cursor.close(); conn.close()
            raise Exception(str(e))

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
            SELECT DISTINCT topic_url FROM weibotopic 
            -- WHERE  theme LIKE '新浪微博_热门话题%' 
            WHERE createdate > date_sub(NOW(), INTERVAL 5 DAY )
            -- Update 30 days' Topics Detail pre day
        """
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute(select_topic_sql)  # filter by date: >_< , include >, exclude <
        for res in cursor.fetchall():
            yield res[0]
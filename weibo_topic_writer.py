#coding=utf-8
import sys
import time
import traceback
from datetime import datetime as dt
import MySQLdb as mdb
from template.weibo_writer import DBAccesor, database_error_hunter

reload(sys)
sys.setdefaultencoding('utf-8')

class WeiboTopicWriter(DBAccesor):

    def __init__(self, db_dict):
        DBAccesor.__init__(self, db_dict)

    def connect_database(self):
        return DBAccesor.connect_database(self)

    @database_error_hunter
    def update_topics_into_db(self, insert_trend_sql, update_info_sql):
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute(insert_trend_sql)
        cursor.execute(update_info_sql)
        print 'Writed topic and trend DONE !!!'
        conn.commit(); cursor.close();  conn.close()


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
            SELECT topic_url FROM topicinfo 
            -- WHERE  theme LIKE '新浪微博_热门话题%' 
            AND createdate > date_sub(NOW(), INTERVAL '5' DAY )
            -- Update 5 days' Topics Detail pre day
        """
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute(select_topic_sql)  # filter by date: >_< , include >, exclude <
        for res in cursor.fetchall():
            yield res[0]
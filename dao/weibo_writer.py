#coding=utf-8
import traceback
from datetime import datetime as dt, timedelta
from dao import DBAccesor, database_error_hunter


class WeiboTopicWriter(DBAccesor):

    def __init__(self, db_dict):
        DBAccesor.__init__(self, db_dict)

    def connect_database(self):
        return DBAccesor.connect_database(self)

    @database_error_hunter
    def update_topics_into_db(self, info_dict):
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
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute(insert_trend_sql, (
            info_dict['topic_url'], info_dict['access_time'],
            info_dict.get('read_num', ''), info_dict.get('read_num_dec', 0),
            info_dict.get('dis_num', ''), info_dict.get('fans_num', ''),
            info_dict.get('image_url', ''), info_dict['topic_url'],
            info_dict['access_time']
        ))

        cursor.execute(update_info_sql, (
            info_dict['title'], info_dict['guide'],
            info_dict.get('read_num', ''), info_dict.get('read_num_dec', 0),
            info_dict.get('dis_num', ''), info_dict.get('fans_num', ''),
            info_dict.get('type', ''), info_dict.get('region', ''),
            info_dict.get('label', ''), info_dict['topic_url'],
            info_dict['image_url'], info_dict['topic_url']
        ))
        conn.commit()
        print 'Writing topic %s DONE !!!' % info_dict['topic_url']
        cursor.close()
        conn.close()


    @database_error_hunter
    def read_topic_url_from_db(self, start_date, end_date, interval=7):
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
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute(select_topic)  # filter by date: >_< , include >, exclude <

        for res in cursor.fetchall():
            yield res[0]
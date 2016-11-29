#coding=utf-8
import sys
import time
import traceback
from datetime import datetime as dt
import MySQLdb as mdb
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
        print "@"*10, "Connecting database at %d-th time..." % attempt
        try:
            WEBCRAWLER_DB_CONN = mdb.connect(**OUTER_MYSQL)
            print '$'*10, 'Connected database succeeded...'
            return WEBCRAWLER_DB_CONN
        except mdb.OperationalError as e:
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Sleep %s seconds cuz we can't connect MySQL..." % seconds
        except Exception as e:
            traceback.print_exc()
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Sleep %s cuz unknown connecting database error." % seconds
        attempt += 1
        time.sleep(seconds)


def write_record_into_db(tag, v_list):
    """
    param v_list(list): a list of info dict
    """
    print "Writing tag ", tag
    is_succeed = False
    is_exited_sql = """
        SELECT id FROM weibokoltype
        WHERE KOL_weibo_label=%s and KOL_url=%s
    """
    update_sql = """
        UPDATE weibokoltype
        SET focus_num=%d, fans_num=%d, blogs_num=%d, KOL_type='%s'
        WHERE KOL_weibo_label='%s' and KOL_url='%s'
    """
    insert_sql = """
        INSERT INTO weibokoltype
        (KOL_weibo_label, KOL_url, KOL_type)
        VALUES (%s, %s, %s)
    """
    conn = connect_database()
    cursor = conn.cursor()
    try:
        for info_dict in v_list:
            user_type = info_dict.get('user_type', '')
            v_user = info_dict.get('user_url', '')
            focus_num = info_dict.get('focus_num', -1)
            fans_num = info_dict.get('fans_num', -1)
            blogs_num = info_dict.get('blogs_num', -1)
            is_exited = cursor.execute(is_exited_sql, (tag, v_user))
            if is_exited:
                # import ipdb; ipdb.set_trace()
                cursor.execute(update_sql % (focus_num, fans_num, blogs_num, user_type, tag, v_user))
                is_succeed = True
                conn.commit()
                print "$"*10, "Update Weibo %s succeeded..." % v_user
            else:
                cursor.execute(insert_sql, (tag, v_user, user_type))
                is_succeed = True
                conn.commit()
                print "$"*10, "Insert Weibo %s succeeded..." % v_user
    except (mdb.ProgrammingError, mdb.OperationalError) as e:
        traceback.print_exc()
        if 'MySQL server has gone away' in e.message:
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "MySQL server has gone away"
        elif 'Deadlock found when trying to get lock' in e.message:
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "You did not solve dead lock"
        elif 'Lost connection to MySQL server' in e.message:
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Lost connection to MySQL server"
        elif e.args[0] in [1064, 1366]:
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Wrong Tpoic String"
        else:
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Other Program or Operation Errors"
    except Exception as e:
        traceback.print_exc()
        print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Write topic failed"
    finally:
        cursor.close()
        conn.close()
    return is_succeed


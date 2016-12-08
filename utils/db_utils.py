import traceback
import MySQLdb as mdb
from datetime import datetime as dt

def catch_database_error(db_func):
    """
    A decrator that catch exceptions and print relative infomation
    """
    def handle_exception(*args, **kargs):
        try:
            return db_func(*args, **kargs)
        except(mdb.ProgrammingError, mdb.OperationalError) as e:
            traceback.print_exc()
            if 'MySQL server has gone away' in e.message:
                print dt.now().strftime("%Y-%m-%d %H:%M:%S"), ERROR_MSG_DICT[DB_SEVER_GONE_AWAY],
            elif 'Deadlock found when trying to get lock' in e.message:
                print dt.now().strftime("%Y-%m-%d %H:%M:%S"), ERROR_MSG_DICT[DB_FOUND_DEADLOCK],
            elif 'Lost connection to MySQL server' in e.message:
                print dt.now().strftime("%Y-%m-%d %H:%M:%S"), ERROR_MSG_DICT[DB_LOST_CONNECTION],
            elif 'Lock wait timeout exceeded' in e.message:
                print dt.now().strftime("%Y-%m-%d %H:%M:%S"), ERROR_MSG_DICT[DB_LOCK_WAIT_TIMEOUT],
            elif e.args[0] in [1064, 1366]:
                print dt.now().strftime("%Y-%m-%d %H:%M:%S"), ERROR_MSG_DICT[DB_UNICODE_ERROR],
            else:
                print dt.now().strftime("%Y-%m-%d %H:%M:%S"), ERROR_MSG_DICT[DB_UNKNOW_ERROR],
        except Exception as e:
            traceback.print_exc()
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), ERROR_MSG_DICT[DB_WRITE_FAILED],
    return handle_exception
# -*- coding: utf-8 -*-

# Related to  aybu cloud proxy, proxy server
ABUYUN_USER = "H778U07K14M4250P"
ABUYUN_PASSWD = "FE04DDEF88A0CC9B"
ABUYUN_HOST = "proxy.abuyun.com"
ABUYUN_PORT = "9010"

# database setting
OUTER_MYSQL = {
    'host': '582af38b773d1.bj.cdb.myqcloud.com',
    'port': 14811,
    'db': 'webcrawler',
    'user': 'web',
    'passwd': "Crawler20161231",
    'charset': 'utf8',
    'connect_timeout': 20,
}
QCLOUD_MYSQL = {
    'host': '10.66.110.147',
    'port': 3306,
    'db': 'webcrawler',
    'user': 'web',
    'passwd': 'Crawler20161231',
    'charset': 'utf8',
    'connect_timeout': 20,
}
REDIS_SETTING = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
}

# Execute result number
SUCCESSED = 1
FAILED = -1
REQUEST_ERROR = -100
PARSE_HTML_ERROR = -101
ACCESS_URL_ERROR = -102
IGNORE_RECORD = -102

# Database Error number using 2XX
DB_WRITE_FAILED = -200
DB_CANNOT_CONNECT = -201
DB_LOST_CONNECTION = -203
DB_SYNTAX_ERROR = -204
DB_LOCK_WAIT_TIMEOUT = -205
DB_FOUND_DEADLOCK = -206
DB_SEVER_GONE_AWAY = -213
DB_UNICODE_ERROR = -207
DB_UNKNOW_ERROR = -299

# Network Error number using 3XX
NETWORK_CONNECTION_ERROR = -300
NETWORK_PROXY_ERROR = -301
NETWORK_TIMEOUT = -302

# Execute result message
ERROR_MSG_DICT = {
    SUCCESSED: "Succeeded",
    FAILED: "Failed",
    REQUEST_ERROR: "Request Target Fialed",
    PARSE_HTML_ERROR: "Parsed url or html FAILED",
    ACCESS_URL_ERROR: "Send requests FAILED",
    IGNORE_RECORD: "The record would be ignored",

    # for database
    DB_WRITE_FAILED: "Write data into database FAILED",
    DB_CANNOT_CONNECT: "Can't connect to MySQL.(服务器资源紧张，导致无法连接)",
    DB_LOCK_WAIT_TIMEOUT: "Lock wait timeout exceeded, try restarting transaction and check if someone manages the table",
    DB_SEVER_GONE_AWAY: "MySQL server has gone away",
    DB_SYNTAX_ERROR: "You have an error in your SQL syntax.(SQL语句有语法错误)",
    DB_LOST_CONNECTION: "Lost connection to MySQL server during query",
    DB_FOUND_DEADLOCK: "Deadlock found when trying to get lock; try restarting transaction",
    DB_UNICODE_ERROR: "Incorrect string value.(不能写入字符串到数据库)",
    DB_UNKNOW_ERROR: "Unknown Program or Operation Errors",

    # for network
    NETWORK_CONNECTION_ERROR: "Connection Error",
    NETWORK_TIMEOUT: "Timeout",
    NETWORK_PROXY_ERROR: "(连接池满了)Max retries exceeded with url",
}
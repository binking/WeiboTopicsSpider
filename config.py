#coding=utf-8

# Related to  aybu cloud proxy
ABUYUN_USER = "H778U07K14M4250P"
ABUYUN_PASSWD = "FE04DDEF88A0CC9B"
ABUYUN_HOST = "proxy.abuyun.com"
ABUYUN_PORT = "9010"

# Related to send requests
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17'}
WEIBO_ACCOUNT = [
    'zhejxoxv185015@163.com', 'yejljz606482@163.com', 
    'manggylv618836@163.com', 'muvsqd834154@163.com',
    'choubcsx105093@163.com'
]
MAIL_CURL_DICT = {
    'zhejxoxv185015@163.com': "curl 'http://weibo.com/p/1008089bbbb864e39fa2369f4110c605573757/home?from=page_100808&mod=TAB' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Referer: http://weibo.com/u/5978968551/home?wvr=5&lf=reg' -H 'Cookie: TC-Ugrow-G0=0149286e34b004ccf8a0b99657f15013; login_sid_t=48831d9c6748a98e5a7dca28329beb84; TC-V5-G0=ffc89a27ffa5c92ffdaf08972449df02; WBStorage=2c466cc84b6dda21|undefined; _s_tentry=-; Apache=6946442829325.034.1480584860812; SINAGLOBAL=6946442829325.034.1480584860812; ULV=1480584860822:1:1:1:6946442829325.034.1480584860812:; SCF=AqheAJG6CGkZCfX_T3nL_ODuxCJs9OlIQE0NKwo59sqccLC7vmA0okX7JO3jXGyE0UkzHgYBY9dJzMOluoJ15zI.; SUB=_2A251O57uDeTxGeNH7FoY9ibJzj2IHXVWMPcmrDV8PUNbmtAKLXOkkW-aTasE6s408zGBYidLjXAw7Zo7iw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFeW27owGRPpMd86BMDO-AY5JpX5K2hUgL.Fo-4S0n4SonfSK22dJLoIpD39PS0McLoqCH8SCHFeF-RxbH8SEHFeb-R1Btt; SUHB=0WGMtsQ5SQFmRc; ALF=1512120894; SSOLoginState=1480584894; un=zhejxoxv185015@163.com; wvr=6; wb_bub_find_5978968551=1; TC-Page-G0=1ac1bd7677fc7b61611a0c3a9b6aa0b4' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' --compressed",
    'yejljz606482@163.com': "curl 'http://weibo.com/p/1008089bbbb864e39fa2369f4110c605573757/home?from=page_100808&mod=TAB' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: TC-Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; login_sid_t=20cee4bf64b943ea5846b841bf6c4237; TC-V5-G0=666db167df2946fecd1ccee47498a93b; _s_tentry=-; wb_bub_find=1; Apache=5725456927528.101.1480585378996; SINAGLOBAL=5725456927528.101.1480585378996; ULV=1480585379003:1:1:1:5725456927528.101.1480585378996:; SCF=Avcs1SB7M0-NRswzEKy3Le096ao_dfQ2FSWhuoyZrXcmT25fs_i5ZlMAl-_AN6Azn9BAanLDr2_AfuFx_nKNKMg.; SUB=_2A251O4DoDeTxGeNH7FoW8C_LwzSIHXVWMPUgrDV8PUNbmtAKLUrFkW8BUvGpGLrtCzfa9UiWr-7_Pr2Oow..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFo_OV9O6evKOAk2G2bynyW5JpX5K2hUgL.Fo-4S0nNeh2N1hn2dJLoIEBLxK.LB.zL1K2LxK.LB-zLB--LxKqLBoeLBo5LxK-LBKqL12Bt; SUHB=0KAhfwB5lSeHog; ALF=1512121400; SSOLoginState=1480585401; un=yejljz606482@163.com; wvr=6; WBStorage=2c466cc84b6dda21|undefined; TC-Page-G0=07e0932d682fda4e14f38fbcb20fac81' -H 'Connection: keep-alive' --compressed",
    'manggylv618836@163.com': "curl 'http://weibo.com/p/1008089bbbb864e39fa2369f4110c605573757/home?from=page_100808&mod=TAB' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: TC-Ugrow-G0=0149286e34b004ccf8a0b99657f15013; login_sid_t=931964454f0da652f6863983ba1d692a; TC-V5-G0=ffc89a27ffa5c92ffdaf08972449df02; WBStorage=2c466cc84b6dda21|undefined; _s_tentry=-; Apache=7893740303698.811.1480585507304; SINAGLOBAL=7893740303698.811.1480585507304; ULV=1480585507319:1:1:1:7893740303698.811.1480585507304:; SCF=AmYrlj7iR5fa3jt33GzVs6z-9hKE61MHip0P9KLT5spHMERqJIxTiAS3eezJyJHE8PxrjJRWk5vB3l6vYKaii6w.; SUB=_2A251O4F8DeTxGeNH7FoY9yzKyjuIHXVWMPW0rDV8PUNbmtAKLRT7kW93lxF9Uj5b6YGfs9UI3HKcEdismA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhU..YjRpMI9mZMoER0EXqK5JpX5K2hUgL.Fo-4S0n4S0zceKM2dJLoI7p-IsHyMJ_kIs8jds2t; SUHB=0WGMtsPRCQFlUb; ALF=1512121516; SSOLoginState=1480585516; un=manggylv618836@163.com; wvr=6; wb_bub_find_5978972617=1; TC-Page-G0=1e758cd0025b6b0d876f76c087f85f2c' -H 'Connection: keep-alive' --compressed",
    'muvsqd834154@163.com': "curl 'http://weibo.com/p/1008089bbbb864e39fa2369f4110c605573757/home?from=page_100808&mod=TAB' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: TC-Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; login_sid_t=475694eaf799c76223e97664d0c0dc30; TC-V5-G0=9ec894e3c5cc0435786b4ee8ec8a55cc; WBStorage=2c466cc84b6dda21|undefined; _s_tentry=-; wb_bub_find=1; Apache=2601290618479.7104.1480585623873; SINAGLOBAL=2601290618479.7104.1480585623873; ULV=1480585623885:1:1:1:2601290618479.7104.1480585623873:; SCF=AqcJkIvBEvxxy3xYYq2h66CFI7qwyj3cDx7jATTY5sh1UCCC6khgxO-OvafZQLFaJX-_eERFqWpdP1_Qu5sDJUo.; SUB=_2A251O4HwDeTxGeNH7FoR-SfFwjyIHXVWMPQ4rDV8PUNbmtAKLRTlkW8kC4hOYLDZuZxNk1iz52xXz-Er2A..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF6aE2S5aOeXORD0ITiH2dK5JpX5K2hUgL.Fo-4S0n71K.41K52dJLoIpWhIs8V9cLV9NxQMJ809JU3; SUHB=06ZVcl_zYV5xNB; ALF=1512121632; SSOLoginState=1480585632; un=muvsqd834154@163.com; wvr=6; wb_bub_find_5978099990=1; TC-Page-G0=b1761408ab251c6e55d3a11f8415fc72' -H 'Connection: keep-alive' --compressed",
    'choubcsx105093@163.com': "curl 'ws://1.49.web1.im.weibo.com/im' -H 'Pragma: no-cache' -H 'Origin: http://weibo.com' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Sec-WebSocket-Version: 13' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Sec-WebSocket-Key: FCAGIupx6R1JqsuPYoRdpA==' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Upgrade: websocket' -H 'Cache-Control: no-cache' -H 'Cookie: login_sid_t=9c2af85d422e61cfc67a8cd3f67dca89; _s_tentry=-; Apache=4268336548064.244.1480585860370; SINAGLOBAL=4268336548064.244.1480585860370; ULV=1480585860382:1:1:1:4268336548064.244.1480585860370:; SCF=AmumktIOv6aAXYIhLTxdUeBEF9lCU3jSNlUJNJRQwwlensw7kMnQNhtKL37V7EYyOxIn3cl5_hO0JTfK2FOEXlw.; SUB=_2A251O4LJDeTxGeNH7FoW8CnIyz6IHXVWMPMBrDV8PUNbmtAKLWLYkW8aeptFBSr1nI0fOFyno2kBJCKuFg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWOvlDyBkhsmxW9EYPSXxSP5JpX5K2hUgL.Fo-4S0nNehMXehz2dJLoIp90dJ8Vi--NiKLWiKnX-cy4Mcy4Mcy4; SUHB=06ZVcl8OQV5wpQ; ALF=1512121880; SSOLoginState=1480585881; un=choubcsx105093@163.com; wvr=6' -H 'Connection: Upgrade' -H 'Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits' --compressed",
    # 'x55120806qinping@163.com': "",
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

BAIDU_CURL_STR = """curl 'https://www.baidu.com/s?ie=utf-8&mod=1&isbd=1&isid=73D1C879AE736221&ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd={kw}&rsv_pq=cbbdd19c00019da4&rsv_t=f3caeinSf3EIdOwk9OYq11erzbHt0TEYxnpR%2BF2TtmSJA%2FT875hqGQSVIWk&rqlang=cn&rsv_enter=1&gpc=stf={start},{end}|stftype=1&tfflag=1&rsv_sid=undefined&_ss=1&clist=&hsug=&f4s=1&csor=3&_cr1=29723' -H 'Cookie: BAIDUID=73D1C894D6EA1C8C35BAA51C16979AE7:FG=1; BIDUPSID=73D1C894D6EA1C8C35BAA51C16979AE7; PSTM=1478583844; __cfduid=dd3986b6e9eb2e4dd47d954b8a76ae6801478744553; BDUSS=GVkYkdnSWNzeEdUb2FyMHNZNTRRR3hsZFVCblhhLXA0YWplYi1CNkZpM0RmVXRZSVFBQUFBJCQAAAAAAAAAAAEAAABPwzQQOTY1MDc2Mzc3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMPwI1jD8CNYV; BD_CK_SAM=1; PSINO=2; H_PS_PSSID=1445_21078_21454_21409_21377_21526_21190_20930; BD_UPN=12314753; sugstore=1; H_PS_645EC=f3caeinSf3EIdOwk9OYq11erzbHt0TEYxnpR%2BF2TtmSJA%2FT875hqGQSVIWk' -H 'is_xhr: 1' -H 'Accept-Encoding: gzip, deflate, sdch, br' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: */*' -H 'Referer: https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd={kw}&rsv_pq=cbbdd19c00019da4&rsv_t=f3caeinSf3EIdOwk9OYq11erzbHt0TEYxnpR%2BF2TtmSJA%2FT875hqGQSVIWk&rqlang=cn&rsv_enter=1&gpc=stf={start},{end}|stftype=1&tfflag=1' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' -H 'is_referer: https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd={kw}&rsv_pq=cbbdd19c00019da4&rsv_t=bf0dy07frZ1UKtJW01IYbfJGeI%2BhOMsDi%2BC%2BEQBWBb8oxFu2c53n31gktrg&rqlang=cn' --compressed"""

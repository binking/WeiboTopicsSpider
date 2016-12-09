#coding=utf-8
import json
import time
import redis
import base64
import requests
from config.weibo_config import *
from config.weibo_config import (
    WEIBO_ACCOUNT_LIST, 
    WEIBO_ACCOUNT_PASSWD, 
    ACTIVATED_COOKIE,
    REDIS_SETTING,
)
from utils.weibo_utils import gen_abuyun_proxy, change_tunnel, retry
exc_list = (Exception)


@retry(exc_list, tries=3, delay=3, backoff=2)
def gen_cookie(account, pwd, proxy={}):
    """ 获取一个账号的Cookie """
    cookie = ""
    loginURL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)"
    username = base64.b64encode(account.encode("utf-8")).decode("utf-8")
    postData = {
        "entry": "sso", "gateway": "1",
        "from": "null", "savestate": "30",
        "useticket": "0", "pagerefer": "",
        "vsnf": "1", "su": username,
        "service": "sso", "sp": pwd,
        "sr": "1440*900", "encoding": "UTF-8",
        "cdult": "3", "domain": "sina.com.cn",
        "prelt": "0", "returntype": "TEXT",
    }
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://weibo.com/sorry?pagenotfound&',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    }
    session = requests.Session()
    r = session.post(loginURL, data=postData, proxies=proxy, headers=headers, timeout=10)
    jsonStr = r.content.decode("gbk")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        # logger.warning("Get Cookie Success!( Account:%s )" % account)
        print "Get Cookie Success!( Account:%s )" % account
        cookie = json.dumps(session.cookies.get_dict())
    else:
        # logger.warning("Failed!( Reason:%s )" % info["reason"])
        # import ipdb; ipdb.set_trace()
        print "Failed!( Reason:%s )" % info["reason"].encode('utf8')
    return cookie


def init_cookie(rconn):
    failed_count = 0
    print "Length: ", len(WEIBO_ACCOUNT_LIST)
    for account in WEIBO_ACCOUNT_LIST:
        auth = '%s--%s' % (account, WEIBO_ACCOUNT_PASSWD)
        if auth in rconn.hkeys(ACTIVATED_COOKIE):
            continue
        aby_proxy = gen_abuyun_proxy()
        cookie = gen_cookie(account, WEIBO_ACCOUNT_PASSWD, aby_proxy)
        if cookie:
            r.hset(ACTIVATED_COOKIE, auth, cookie)
            time.sleep(2)
        else:
            change_tunnel()
            failed_count += 1
        if failed_count >= 5:
            print 'Failed in login too many times.'
            break

if __name__=='__main__':
    r = redis.StrictRedis(**REDIS_SETTING)
    init_cookie(r)
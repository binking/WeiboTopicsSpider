#coding=utf-8
import time, traceback
from datetime import datetime as dt, timedelta
from abuyun_proxy import change_tunnel


def wrap_print(tag, center, repeat=10):
    print tag * repeat,
    print center,
    print tag * repeat


def handle_sleep(seconds):
    print "Sleeping %d seconds " % seconds, 'zZ'*10
    time.sleep(seconds)


def handle_proxy_error(seconds):
    print "Sleep %d seconds " % seconds, 
    handle_sleep(seconds)
    changed_proxy = change_tunnel()  # Change IP tunnel of Abuyun
    if changed_proxy:
        print "and change IP to %s " % changed_proxy.get("ip_addr")
    else:
        print "but Change Proxy Error"


def str_2_int(num_str):
    try:
        return int(num_str.replace(',', ''))
    except:
        return -1


def extract_cookie_from_curl(curl):
    url = ''
    cookie_dict = {}
    tokens = curl.split("'")
    try:
        for i in range(0, len(tokens)-1, 2):
            if tokens[i].startswith("curl"):
                url = tokens[i+1]
            if "-H" in tokens[i]:
                attr, value = tokens[i+1].split(": ")  # be careful space
                if 'Cookie' in attr:
                    cookie_dict[attr] = value
    except Exception as e:
        print "!"*20, "Parsed cURL Failed"
        traceback.print_exc()
    return url, cookie_dict


def curl_str2post_data(curl):
    """
    Given curl that was cpoied from Chrome, no matter baidu or sogou, 
    parse it and then get url and the data you will post/get with requests
    """
    url = ""
    post_data = {}
    tokens = curl.split("'")
    try:
        for i in range(0, len(tokens)-1, 2):
            if tokens[i].startswith("curl"):
                url = tokens[i+1]
            elif "-H" in tokens[i]:
                attr, value = tokens[i+1].split(": ")  # be careful space
                post_data[attr] = value
    except Exception as e:
        print "!"*20, "Parsed cURL Failed"
        traceback.print_exc()
    return url, post_data

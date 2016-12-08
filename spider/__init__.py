#coding=utf-8
import os
import re
import json
import time
import redis
import requests
import traceback
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from requests.exceptions import (
    ProxyError,
    Timeout,
    ConnectionError,
    ConnectTimeout,
)
from utils import (
    extract_cookie_from_curl,
    extract_post_data_from_curl,
    gen_abuyun_proxy, 
    handle_proxy_error, 
    handle_sleep, 
    catch_network_error, 
    retry
)
from config.weibo_config import *

weibo_ranks = ['icon_member', 'icon_club', 'icon_female', 'icon_vlady', 'icon_pf_male', 'W_icon_vipstyle']
exc_list = (IndexError, ProxyError, Timeout, ConnectTimeout, ConnectionError, Exception)


class Spider(object):
    def __init__(self, start_url, curl='', timeout=10, delay=1, proxy={}):
        self.url = start_url
        self.curl = curl
        self.cookie = {}  # self.extract_cookie_from_curl()
        self.post = {}  # self.extract_post_data_from_curl()
        self.headers = {}
        self.timeout = timeout
        self.proxy = proxy
        self.delay = delay
        self.page = ''

    def extract_cookie_from_curl(self):
        cookie_dict = {}
        tokens = self.curl.split("'")
        if not tokens:
            # curl is empty string
            return cookie_dict
        try:
            for i in range(0, len(tokens)-1, 2):
                # if tokens[i].startswith("curl"):
                #     url = tokens[i+1]
                if "-H" in tokens[i]:
                    attr, value = tokens[i+1].split(": ")  # be careful space
                    if 'Cookie' in attr:
                        cookie_dict[attr] = value
        except Exception as e:
            print "!"*20, "Parsed cURL Failed"
            traceback.print_exc()
        return cookie_dict

    def extract_post_data_from_curl(self):
        """
        Given curl that was cpoied from Chrome, no matter baidu or sogou, 
        parse it and then get url and the data you will post/get with requests
        """
        post_data = {}
        tokens = self.curl.split("'")
        if not tokens:
            # curl is empty string
            return cookie_dict
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
        return post_data

    @catch_network_error(exc_list)
    @retry(exc_list, tries=4, delay=2, backoff=2)
    def gen_html_source(self, method='python'):
        """
        Separate get page and parse page
        """
        if not self.cookie:
            return None
        request_args = {'timeout': self.timeout,
            'cookies': self.cookie, 'proxies': self.proxy,
        }
        if method == 'python':
            # proxy = gen_abuyun_proxy()
            source_code = requests.get(self.url, **request_args).text
        else:
            if '--silent' not in self.curl:
                self.curl += '--silent'
            source_code = os.popen(self.curl).read()
        # parser = bs(source_code, 'html.parser')
        elminate_white = re.sub(r'\\r|\\t|\\n', '', source_code)
        elminate_quote = re.sub(r'\\"', '"', elminate_white)
        elminate_slash = re.sub(r'\\/', '/', elminate_quote)
        handle_sleep(self.delay)
        return elminate_slash.encode('utf8')

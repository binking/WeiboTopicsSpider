#coding=utf-8
import os
import re
import json
import time
import redis
import base64
import requests
from lxml import etree
from datetime import datetime as dt
from requests.exceptions import (
    ProxyError,
    Timeout,
    ConnectionError,
    ConnectTimeout,
)
from . import Spider
from utils.weibo_utils import (
    extract_header_from_curl,
    catch_network_error, 
    catch_parse_error,
    gen_abuyun_proxy,
    retry
)
from config.weibo_config import ACTIVATED_COOKIE

exc_list = (IndexError, ProxyError, Timeout, ConnectTimeout, ConnectionError, Exception)


def extract_chinese_info(source):
    eliminate_chars = r'[!"#$%&\'\*\+\./;\<=\>\?@\[\\\]\^_`\{\|\}~a-zA-Z]'
    eliminate_num1 = re.sub(r'"https?://.+?"', '', source)  # elminate numbers in url
    eliminate_num2 = re.sub(r'\</?\w+\d+\>|', '', eliminate_num1)  # eliminate numbers in tag
    eliminate_num3 = re.sub(r'(\w+?)(-?)(\w+)="[\w ]+?"', '', eliminate_num2)  # eliminate numbers and - in attr
    eliminate_num4 = re.sub(eliminate_chars, '', eliminate_num3)
    return re.sub(r'\s+', ' ', eliminate_num4).strip()  # elimnate blank

class WeiboSpider(Spider):
    def __init__(self, start_url, account, password, timeout=10, delay=1, proxy={}):
        Spider.__init__(self, start_url, timeout=10, delay=1, proxy={})
        self.account = account
        self.password = password
        self.is_abnormal = False
        print 'Parsing %s using Account %s' % (self.url, self.account)

    def use_abuyun_proxy(self):
        self.proxy = gen_abuyun_proxy()

    def add_request_header(self):
        # self.headers = extract_header_from_curl(curl)
        self.headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://weibo.com/sorry?pagenotfound&',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        }

    def check_abnormal_status(self):
        import ipdb; ipdb.set_trace()
        if len(self.page) < 10000:  # Let IndexError disappear
            print >>open('./html/block_error_%s.html' % self.account, 'w'), self.page
            self.is_abnormal = True
        elif self.page.find('<title>404错误</title>') > 0:  # <title>404错误</title>
            print >>open('./html/freezed_account_%s.html' % self.account, 'w'), self.page
            self.is_abnormal = True
        return self.is_abnormal

    def read_cookie(self, rconn):
        auth = '%s--%s' % (self.account, self.password)
        if auth in rconn.hkeys(ACTIVATED_COOKIE):
            print 'Existed'
            self.cookie = json.loads(rconn.hget(ACTIVATED_COOKIE, auth))
            return True
        else:
            print "New"
            status = self.gen_cookie(rconn)
            if status:
                return True
        # time.sleep(2)
        return False

    def gen_cookie(self, rconn):
        """ 
        获取一个账号的Cookie
        Cookie is str
        """
        auth = '%s--%s' % (self.account, self.password)
        loginURL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)"
        username = base64.b64encode(self.account.encode("utf-8")).decode("utf-8")
        postData = {
            "entry": "sso", "gateway": "1",
            "from": "null", "savestate": "30",
            "useticket": "0", "pagerefer": "",
            "vsnf": "1", "su": username,
            "service": "sso", "sp": self.password,
            "sr": "1440*900", "encoding": "UTF-8",
            "cdult": "3", "domain": "sina.com.cn",
            "prelt": "0", "returntype": "TEXT",
        }
        # import ipdb; ipdb.set_trace()
        session = requests.Session()
        r = session.post(loginURL, data=postData, headers=self.headers, proxies=self.proxy)
        jsonStr = r.content.decode("gbk")
        info = json.loads(jsonStr)
        if info["retcode"] == "0":
            # logger.warning("Get Cookie Success!( Account:%s )" % account)
            print "Get Cookie Success!( Account:%s )" % self.account
            self.cookie = session.cookies.get_dict()
            # save cookie into Redis
            rconn.hset(ACTIVATED_COOKIE, auth, json.dumps(self.cookie))
            return True
        else:
            # logger.warning("Failed!( Reason:%s )" % info["reason"])
            print "Failed!( Reason:%s )" % info["reason"]
            return False

    def update_cookie(self, rconn):
        """ 更新一个账号的Cookie """
        auth = '%s--%s' % (self.account, self.password)
        status = self.gen_cookie(self.account, self.password)
        if status:
            # logger.warning("The cookie of %s has been updated successfully!" % account)
            print "The cookie of %s has been updated successfully!" % account
            rconn.hset(ACTIVATED_COOKIE, auth, self.cookie)
        else:
            # logger.warning("The cookie of %s updated failed! Remove it!" % accountText)
            print "The cookie of %s updated failed! Remove it!" % accountText
            self.removeCookie(rconn)

    def remove_cookie(self, rconn):
        """ 删除某个账号的Cookie """
        auth = '%s--%s' % (self.account, self.password)
        rconn.hdel(ACTIVATED_COOKIE, auth)
        cookie_num = rconn.hlen(ACTIVATED_COOKIE)
        print "The num of the cookies left is %s" % cookie_num

    # @catch_network_error(exc_list)
    @retry(exc_list, tries=3, delay=2, backoff=2)
    def gen_html_source(self):
        """
        Separate get page and parse page
        """
        if not self.cookie:
            return False
        # proxy = gen_abuyun_proxy()
        # import ipdb; ipdb.set_trace()
        r = requests.get(self.url, timeout=self.timeout, headers=self.headers,
            cookies=self.cookie, proxies=self.proxy)
        # print r.text
        if len(r.text) < 1:
            raise ConnectionError('Access nothing back')
        elif 16000<len(r.text)<18000:
            raise ConnectionError('Ghost Error, incorrect source code but not freezed')
        if r.status_code == 200:
            self.page = r.text.encode('utf8')
        return True

"""
theme  新浪微博_博主详细信息48992_daily
middle  default
createdate   write date
bucketName  follower
uri
weibo_user_url  exclude info
nickname   <li class="li_1 clearfix"><span class="pt_title S_txt2">昵称：</span><span class="pt_detail">杰女王</span></li>

\<li class="li_1 clearfix"\>\<\w+ class="pt_title S_txt2"\>(.+?)\</\w+?\>\<\w+? (class|href)=".+?"\>(http://)?(.+?)\</\w+?\>\</li\>

realname   li class="li_1 clearfix"><span class="pt_title S_txt2">真实姓名：</span><span class="pt_detail">王杰</span></li>
gender   <li class="li_1 clearfix"><span class="pt_title S_txt2">性别：</span><span class="pt_detail">女</span></li>
introduction  <li class="li_1 clearfix"><span class="pt_title S_txt2">简介：</span><span class="pt_detail">感恩！</span></li>
location   <li class="li_1 clearfix"><span class="pt_title S_txt2">所在地：</span><span class="pt_detail">北京 海淀区</span></li>
registration_date  <li class="li_1 clearfix"><span class="pt_title S_txt2">注册时间：</span><span class="pt_detail">2011-05-18</span></li>
label
date_of_birth   <li class="li_1 clearfix"><span class="pt_title S_txt2">生日：</span><span class="pt_detail">1990年12月8日</span></li>
company
preliminary_school
middle_school
high_school
tech_school   职业中专学校
university
blog_url   <li class="li_1 clearfix"><span class="pt_title S_txt2">博客：</span><a href="http://blog.sina.com.cn/weiaijiaz?from=inf&wvr=5&loc=infblog">http://blog.sina.com.cn/weiaijiaz</a></li>
domain   <li class="li_1 clearfix"><span class="pt_title S_txt2">个性域名：</span><span class="pt_detail"><a href="http://weibo.com/weiaijiaz?from=inf&wvr=5&loc=infdomain">http://weibo.com/weiaijiaz</a></span></li>
msn
QQ
email
sex_tendancy
emotion
blood_type
KOL
focus_num   <a bpfilter="page_frame"  class="t_link S_txt1" href="http://weibo.com/p/1005051791434577/follow?from=page_100505&wvr=6&mod=headfollow#place" ><strong class="W_f18">212</strong>
fans_num   <a bpfilter="page_frame"  class="t_link S_txt1" href="http://weibo.com/p/1005051791434577/follow?relate=fans&from=100505&wvr=6&mod=headfans&current=fans#place" ><strong class="W_f18">49775</strong>
weibo_num   <a bpfilter="page_frame"  class="t_link S_txt1" href="http://weibo.com/p/1005051791434577/home?from=page_100505_profile&wvr=6&mod=data#place" ><strong class="W_f18">1027</strong>

r'\<a bpfilter="page_frame"  class="t_link S_txt1" href="http://weibo.com/p/100\d+/.*?" \>\<(\w+) class=".+?"\>(\d+)\</(\w+)\>'
 @catch_parse_error((AttributeError, Exception))
    def parse_bozhu_info_2(self):
        res = {}
        if not self.page:
            return res
        # Parse game is on !!!
        tree = etree.HTML(self.page.decode('utf8'))
        # The three numbers
        import ipdb; ipdb.set_trace()
        focus_num_xpath = tree.xpath('//*[@id="Pl_Core_T8CustomTriColumn__55"]/div/div/div/table/tbody/tr/td[1]/a/strong')
        fans_num_xpath = tree.xpath('//*[@id="Pl_Core_T8CustomTriColumn__55"]/div/div/div/table/tbody/tr/td[2]/a/strong')
        weibo_num_xpath = tree.xpath('//*[@id="Pl_Core_T8CustomTriColumn__55"]/div/div/div/table/tbody/tr/td[3]/a/strong')
        if focus_num_xpath and fans_num_xpath and weibo_num_xpath:
            self.info['focus_num'] = int(focus_num_xpath[0].text)
            self.info['fans_num'] = int(fans_num_xpath[0].text)
            self.info['weibo_num'] = int(weibo_num_xpath[0].text)
        else:
            return res
        kol_type_xpath = tree.xpath('//*[@id="Pl_Official_Headerv6__1"]/div/div/div[2]/div[2]/span/a/i')
        if kol_type_xpath:
            self.info['kol'] = kol_type_xpath[0].text
        # parse basic info
        # info_units = tree.xpath('//*[@id="Pl_Official_PersonalInfo__59"]/div/div/div[2]/div/ul/li')
        info_units = tree.findall('//ul[@class="clearfix"]/li[@class="li_1 clearfix"]')
        if not info_units:
            return res
        for unit in info_units:
            attr_tag = unit.find('//*[class="pt_title S_txt2"]')  # 390336
            value_tag = unit.find('//*[class="pt_detail"]')
            if not(attr and value):
                continue
            attr = attr_tag.text; value = value_tag.text
            if '昵称' in attr:
                self.info['nickname'] = value
            elif '真实姓名' in attr:
                self.info['realname'] = value
            elif '所在地' in attr:
                self.info['location'] = value
            elif '性别' in attr:
                self.info['gender'] = value
            elif '性取向' in attr:
                self.info['sex_tendancy'] = value
            elif '感情状况' in attr:
                self.info['emotion'] = value
            elif '生日' in attr:
                self.info['date_of_birth'] = value
            elif '简介' in attr:
                self.info['introduction'] = value
            elif '邮箱' in attr:  # http://weibo.com/5666208404/info  Empty email
                self.info['email'] = value
            elif 'QQ' in attr:
                self.info['qq'] = value
            elif '注册时间' in attr:
                self.info['registration_date'] = value
            elif '博客' in attr:
                self.info['blog_url'] = value
                if 'href' in value and unit.find('//a'):
                    self.info['blog_url'] = unit.find('//a').text
            elif '个性域名' in attr:
                self.info['domain'] = value
                if 'href' in value and unit.find('//a'):
                    self.info['domain'] = unit.find('//a').text
            elif '大学' in attr:
                self.info['university'] = extract_chinese_info(value)
            elif '高中' in attr:
                self.info['high_school'] = extract_chinese_info(value)
            elif '标签' in attr:
                self.info['label'] = extract_chinese_info(value)
            elif '公司' in attr:
                tags = unit.find_all('//*[@class="pt_detail"]')
                if tags:
                    self.info['company'] = ' '.join([tag.text.strip() for tag in tags])
        # fill other info
        # import ipdb; ipdb.set_trace()
        self.info['uri'] = self.url
        self.info['weibo_user_url'] = '/'.join(self.url.split('/')[:-1])
        # for k,v in self.info.items():
        #     print k, v
        return self.info
""" 
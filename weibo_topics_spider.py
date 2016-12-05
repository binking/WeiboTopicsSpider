#coding=utf-8
import re
import json
import redis
import random
import requests
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from requests.exceptions import (
    ProxyError,
    Timeout,
    ConnectionError,
    ConnectTimeout,
)
from abuyun_proxy import gen_abuyun_proxy
from config import MAIL_CURL_DICT
from utils import chin_num2dec, extract_cookie_from_curl
from decrators import retry, catch_network_error

EXC_LIST = (IndexError, KeyError, ProxyError, Timeout, ConnectTimeout, ConnectionError, Exception)


@catch_network_error(EXC_LIST)
@retry(EXC_LIST, tries=2)
def extract_topic_info(topic_uri, redis_key):
    """
    Given topic url, parse HTML code and get topic info
    redis_key = weibo:account:mail, its value is set of email addresses
    """
    info_dict = {}
    # pick mail account randomly
    r2 = redis.StrictRedis(host='localhost', port=6379, db=0)
    # rand_account = r2.srandmember(redis_key)
    rand_account = 'laoshi968020@163.com'
    if not rand_account:
        print 'Weibo Accounts were run out of...'
        return {}
    print 'Parsing: ', topic_uri, ' with account: ', rand_account
    curl_str = MAIL_CURL_DICT[rand_account].format(uri=topic_uri)
    _, cookie = extract_cookie_from_curl(curl_str)
    if not cookie:
        return info_dict
    # aby_proxy = gen_abuyun_proxy()
    r = requests.get(topic_uri, timeout=10, proxies={}, cookies=cookie)
    parser = bs(r.text, 'html.parser')
    if len(r.text) < 10000 or parser.find('div', {'class': 'W_error_bg'}):
        print >>open('./html/access_error_%s.html' % dt.now().strftime("%Y-%m-%d %H:%M:%S"), 'w'), parser
        r2.srem(redis_key, rand_account)
        raise ConnectionError('Hey, boy, account %s was freezed' % rand_account)
    # exclude micro discussion
    page_title = parser.find('title')
    if page_title and '在微话题一起聊聊吧！' in page_title.text.encode('utf8'):
        print 'Ignore Micro Discussion: %s' % page_title.text.split('-')[0]
        return info_dict
    # -- parse description of topic
    meta_tag = parser.find('meta', {'name': 'description'})
    if meta_tag:
        info_dict['guide'] = meta_tag.get('content', '').encode('utf8').strip()

    image_url_parser = None; stat_nums_parser = None; about_parser = None
    for script in parser.find_all('script'):
        script_text = script.text.encode('utf8')
        if 'pf_head S_bg2 S_line1' in script_text:
            image_url_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
        elif 'PCD_counter' in script_text:
            stat_nums_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
        # elif 'topic_PCD_guide' in script_text or '导语' in script_text:
        #     guide_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
        elif 'Pl_Core_T5MultiText__31' in script_text and '关于' in script_text:
            # no about: http://weibo.com/p/100808bcd9f210dc631a1eec4a9e1bef001f59
            about_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
    # extract image url
    if image_url_parser:
        div_tag = image_url_parser.find('div', {'class': 'pf_username clearfix'})
        if div_tag and div_tag.find('h1'):
            info_dict['title'] = div_tag.find('h1').get('title', '').strip()[1:-1]  # remove # sign
        div_tag = image_url_parser.find('div', {'class': 'pf_head S_bg2 S_line1'})
        if div_tag and div_tag.find('img'):
            info_dict['image_url'] = div_tag.find('img').get('src')
    # extract the numbers of read, discuss, and fans
    if stat_nums_parser:
        div_tag = stat_nums_parser.find('div', {'class': 'PCD_counter'})
        
        if div_tag and len(div_tag.find_all(attrs={'class': re.compile(r'W_f')})) == 3:  # span or strong
            # info_dict['read_num'] = chin_num2dec(div_tag.find_all(attrs={'class': re.compile(r'W_f')})[0].text)
            info_dict['read_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[0].text.strip()
            info_dict['dis_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[1].text.strip()
            info_dict['fans_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[2].text.strip()
            info_dict['read_num_dec'] = chin_num2dec(info_dict['read_num'])
        else:
            counters = div_tag.find('td').text.split()
            info_dict['read_num'] = counters[0][:-2]
            info_dict['dis_num'] = counters[1][:-2]
            info_dict['fans_num'] = counters[2][:-2]
            info_dict['read_num_dec'] = chin_num2dec(info_dict['read_num'])
    # extract guide article
    # if guide_parser:
    #     div_tag = guide_parser.find('div', {'class': 'topic_PCD_guide'})
    #     if div_tag and div_tag.find('p', {'class': re.compile(r'W_f')}):
            
    # extract type, label, and region of topic
    # import ipdb; ipdb.set_trace()
    if about_parser:
        for li_tag in about_parser.find_all('li'):
            title_tag = li_tag.find(attrs={'class': re.compile('pt_title')})
            detail_tag = li_tag.find(attrs={'class': re.compile('pt_detail')})
            title = title_tag.text.encode('utf8')
            if not detail_tag:
                print >>open('Other_unknown_abount_parser_%s.html' % dt.now().strftime("%Y-%m-%d %H:%M:%S"), 'w'), about_parser
                continue
            detail = ' '.join([a_tag.text.strip() for a_tag in detail_tag.find_all('a')])
            if '分类' in title:  # http://weibo.com/3238362920/about
                info_dict['type'] = detail
            elif '地区' in title:
                info_dict['region'] = detail
            elif '标签' in title:
                info_dict['label'] = detail
            else:
                print >>open('Other_unknown_attr_%s.html' % dt.now().strftime("%Y-%m-%d %H:%M:%S"), 'w'), about_parser
    if info_dict['title'] and info_dict['image_url']:  # can't be none
        info_dict['access_time'] = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        info_dict['topic_url'] = topic_uri
    return info_dict

def test_extract_topic_info():
    redis_key = 'weibo:account:mail'
    # print 'test case 1'
    # for key, value in extract_topic_info('http://weibo.com/p/100808f9a9c4d653810aa0a0c0f748baf056d1', redis_key).items():
    #     print key, value
    print 'test case 2'
    for key, value in extract_topic_info('http://weibo.com/p/1008087eadf177091b5221806c23b7cb64f451', redis_key).items():
        print key, value
    # print 'test case 3'
    # for key, value in extract_topic_info('http://weibo.com/p/100808fe0981c53b23fbf9d839602cf9ba1a44', redis_key).items():
    #    print key, value


test_extract_topic_info()
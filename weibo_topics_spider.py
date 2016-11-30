#coding=utf-8
import re
import json
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
from utils import chin_num2dec, extract_cookie_from_curl
from decrators import retry, catch_network_error

TOPIC_CURL_STR = "curl '{topic_uri}?from=faxian_huati' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Referer: http://d.weibo.com/100803' -H 'Cookie: SINAGLOBAL=7912212257618.43.1478585959985; _T_WM=86d2f9fdad4fd8343aa9ddd0620ab738; TC-Page-G0=cdcf495cbaea129529aa606e7629fea7; TC-V5-G0=28bf4f11899208be3dc10225cf7ad3c6; TC-Ugrow-G0=0149286e34b004ccf8a0b99657f15013; _s_tentry=weibo.com; Apache=508038804601.5982.1480474268587; ULV=1480474268594:13:13:3:508038804601.5982.1480474268587:1480385082935; login_sid_t=80e48a13934430fcb97989a0ba7312cd; WBtopGlobal_register_version=e91f392a3df0305e; UOR=,,www.google.co.jp; SCF=Ap11mp4UEZs9ZcoafG0iD1wVDGjdyuPuLY8BpwtpvSEErQlo5SNaLf7wohVf8bgai_0rueZk0YFeoLHHVVDh-_4.; SUB=_2A251OgrwDeTxGeNG71EX8ybKwj6IHXVWTns4rDV8PUNbmtAKLWzckW-GZdInr7X3ic6hEjlvqcExoB_xfw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5HA7SsRPVzLQ_q6ucc2n_c5JpX5K2hUgL.Fo-RShece0nc1Kz2dJLoI7viKg4lHGWEdcUEqgf_9Pzt; SUHB=0QSpqbgsn69_jg; ALF=1512025632; SSOLoginState=1480489632; un=jiangzhibinking@outlook.com; wvr=6' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' --compressed"
EXC_LIST = (IndexError, KeyError, ProxyError, Timeout, ConnectTimeout, ConnectionError, Exception)


@catch_network_error(EXC_LIST)
@retry(EXC_LIST, tries=3)
def extract_topic_info(topic_uri):
    """
    Given topic url, parse HTML code and get topic info
    """
    url, cookie = extract_cookie_from_curl(TOPIC_CURL_STR.format(topic_uri=topic_uri))
    proxy = gen_abuyun_proxy()
    # import ipdb; ipdb.set_trace()
    r = requests.get(topic_uri, cookies=cookie)
    info_dict = {
        'access_time': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
        'topic_url': topic_uri,
    }
    parser = bs(r.text, 'html.parser')
    if parser.find('div', {'class': 'W_error_bg'}):
        print '小鬼，你的微博账号被冻结了！！！'
        return {}
    image_url_parser = None; stat_nums_parser = None; guide_parser = None
    for script in parser.find_all('script'):
        if 'pf_head S_bg2 S_line1' in script.text:
            image_url_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
        elif 'PCD_counter' in script.text:
            stat_nums_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
        elif 'topic_PCD_guide' in script.text:
            guide_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
    # import ipdb; ipdb.set_trace()
    # extract image url
    if image_url_parser:
        div_tag = image_url_parser.find('div', {'class': 'pf_username clearfix'})
        if div_tag and div_tag.find('h1'):
            info_dict['title'] = div_tag.find('h1').get('title').encode('utf8')[1:-1]  # remove # sign
        else:
            return {}
        div_tag = image_url_parser.find('div', {'class': 'pf_head S_bg2 S_line1'})
        if div_tag and div_tag.find('img'):
            info_dict['image_url'] = div_tag.find('img').get('src')
    # extract the numbers of read, discuss, and fans
    if stat_nums_parser:
        div_tag = stat_nums_parser.find('div', {'class': 'PCD_counter'})
        if div_tag and len(div_tag.find_all(attrs={'class': re.compile(r'W_f')})) == 3:  # span or strong
            # info_dict['read_num'] = chin_num2dec(div_tag.find_all(attrs={'class': re.compile(r'W_f')})[0].text)
            info_dict['read_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[0].text.encode('utf8')
            info_dict['dis_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[1].text.encode('utf8')
            info_dict['fans_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[2].text.encode('utf8')
    # extract guide article
    if guide_parser:
        div_tag = guide_parser.find('div', {'class': 'topic_PCD_guide'})
        if div_tag and div_tag.find('p', {'class': re.compile(r'W_f')}):
            info_dict['guide'] = div_tag.find('p', {'class': re.compile(r'W_f')}).text.encode('utf8')
    return info_dict


def test_chin_num2dec():
    test_words = ['11.8亿', '100.2万', '5770']
    for w in test_words:
        print chin_num2dec(w)

def test_extract_topic_info():
    print 'test case 1'
    print extract_topic_info('http://weibo.com/p/100808d9d36d82afccaa73f80e8ef9c11c2c17')
    print 'test case 2'
    print extract_topic_info('http://weibo.com/p/10080890d8e011e4d65f67a67cf9acdc23a18e')

# test_extract_topic_info()
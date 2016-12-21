#coding=utf-8
import re
import json
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from template.weibo_spider import WeiboSpider
from template.weibo_utils import chin_num2dec, catch_parse_error

class WeiboTopicSpider(WeiboSpider):
    def __init__(self, start_url, account, password, timeout=10, delay=1, proxy={}):
        WeiboSpider.__init__(self, start_url, account, password, timeout=10, delay=1, proxy={})
        self.topic_info = {}

    @catch_parse_error((Exception, ))
    def parse_topic_info(self):
        """
        Given topic url, parse HTML code and get topic info
        """
        res = {}
        if not self.page:
            return res
        parser = bs(self.page, 'html.parser')
        meta_tag = parser.find('meta', {'name': 'description'})
        if meta_tag:  # guide is optional
            self.topic_info['guide'] = meta_tag.get('content', '').encode('utf8').strip()
        image_url_parser = None; stat_nums_parser = None; about_parser = None
        for script in parser.find_all('script'):
            script_text = script.text.encode('utf8')
            if 'pf_head S_bg2 S_line1' in script_text and "\"html\"" in script_text:
                # import ipdb; ipdb.set_trace()
                image_url_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
            elif 'PCD_counter' in script_text and "\"html\"" in script_text:
                # <script>FM.view({"ns":"","domid":"Pl_Core_T8CustomTriColumn__12","css":["style/css/module/pagecard/PCD_counter.css?version=321967be9a0c2834"]})</script>
                stat_nums_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
            elif 'Pl_Core_T5MultiText__31' in script_text and '关于' in script_text and "\"html\"" in script_text:
                # no about: http://weibo.com/p/100808bcd9f210dc631a1eec4a9e1bef001f59
                about_parser = bs(json.loads(script.text[8:-1])['html'], 'html.parser')
        if not stat_nums_parser:
            print 'It\'s a pity not to stat.. Dammit'
        # extract image url
        # import ipdb; ipdb.set_trace()
        if image_url_parser:
            div_tag = image_url_parser.find('div', {'class': 'pf_username clearfix'})
            if div_tag and div_tag.find('h1'):
                self.topic_info['title'] = div_tag.find('h1').get('title', '').strip()[1:-1]  # remove # sign
            div_tag = image_url_parser.find('div', {'class': 'pf_head S_bg2 S_line1'})
            if div_tag and div_tag.find('img'):
                self.topic_info['image_url'] = div_tag.find('img').get('src')
        # extract the numbers of read, discuss, and fans
        if stat_nums_parser:
            div_tag = stat_nums_parser.find('div', {'class': 'PCD_counter'})
            
            if div_tag and len(div_tag.find_all(attrs={'class': re.compile(r'W_f')})) == 3:  # span or strong
                # info_dict['read_num'] = chin_num2dec(div_tag.find_all(attrs={'class': re.compile(r'W_f')})[0].text)
                self.topic_info['read_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[0].text.strip()
                self.topic_info['dis_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[1].text.strip()
                self.topic_info['fans_num'] = div_tag.find_all(attrs={'class': re.compile(r'W_f')})[2].text.strip()
                self.topic_info['read_num_dec'] = chin_num2dec(self.topic_info['read_num'])
            else:
                counters = div_tag.find('td').text.split()
                self.topic_info['read_num'] = counters[0][:-2]
                self.topic_info['dis_num'] = counters[1][:-2]
                self.topic_info['fans_num'] = counters[2][:-2]
                self.topic_info['read_num_dec'] = chin_num2dec(self.topic_info['read_num'])        
        # extract type, label, and region of topic
        # 
        if about_parser:
            for li_tag in about_parser.find_all('li'):
                title_tag = li_tag.find(attrs={'class': re.compile('pt_title')})
                detail_tag = li_tag.find(attrs={'class': re.compile('pt_detail')})  # pt_detail is optional
                title = title_tag.text.encode('utf8')
                if not detail_tag:
                    detail = ''
                else:
                    detail = ' '.join([a_tag.text.strip() for a_tag in detail_tag.find_all('a')])
                if '分类' in title:  # http://weibo.com/3238362920/about
                    self.topic_info['type'] = detail
                elif '地区' in title:
                    self.topic_info['region'] = detail
                elif '标签' in title:
                    self.topic_info['label'] = detail
        if self.topic_info.get('title') and self.topic_info.get('image_url'):  # can't be none
            self.topic_info['access_time'] = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            self.topic_info['topic_url'] = self.url
        # for k,v in self.topic_info.items():
        #     print k, v
        return self.topic_info

def test_extract_topic_info():
    redis_key = 'weibo:account:mail'
    # print 'test case 1'
    # for key, value in extract_topic_info('http://weibo.com/p/100808f9a9c4d653810aa0a0c0f748baf056d1', redis_key).items():
    #     print key, value
    print 'test case 2'
    for key, value in extract_topic_info('http://weibo.com/p/1008087eadf177091b5221806c23b7cb64f451', redis_key).items():
        print key, value

"""
extract guide article
if guide_parser:
     div_tag = guide_parser.find('div', {'class': 'topic_PCD_guide'})
     if div_tag and div_tag.find('p', {'class': re.compile(r'W_f')}):
# exclude micro discussion
# if '访谈问答' in r.text.encode('utf-8'):
#     print 'Ignore Micro Discussion: %s' % topic_uri
#     return info_dict
# -- parse description of topic
"""

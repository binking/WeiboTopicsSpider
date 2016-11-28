import re
import requests
from bs4 import BeautifulSoup as bs

TOPIC_CURL_STR = "curl '{topic_uri}' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Cookie: SINAGLOBAL=7912212257618.43.1478585959985; _T_WM=86d2f9fdad4fd8343aa9ddd0620ab738; ALF=1482487825; SUB=_2A251MRtBDeTxGeVG7FYT8i_OzzWIHXVW3aUJrDV8PUJbkNAKLVLQkW2UJqEwxq67M2IQIPSfHhrqMs7qDQ..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhxM.AD9EjGmQSc51FnJvMU5JpX5oz75NHD95Q01hMXeozpeoB4Ws4Dqcj.i--4iK.Ri-z0i--ciK.RiKy8i--fi-z7iK.pi--fi-z4i-zX; wvr=6; UOR=,,www.gooseeker.com; TC-Page-G0=4e714161a27175839f5a8e7411c8b98c; TC-Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; TC-V5-G0=914ba011d20e5b7f25fe12574c186eda; _s_tentry=d.weibo.com; Apache=6137717990708.824.1480302995773; ULV=1480302995842:11:11:1:6137717990708.824.1480302995773:1480080279392' -H 'Connection: keep-alive' --compressed"

def chin_num2dec(num_str):
	res = -1
	try:
		num = re.search(r'\d+\.?\d*', num_str).group(0)
		res = int(num)
	except ValueError as e:
		if '亿' in num_str:
			if len(num.split('.')) == 2:
				left, right = num.split('.')
				res = int(left)*pow(10, 8) + int(right)*pow(10, 8-len(right))
			else:
				res = int(num) * pow(10, 8)
		elif '万' in num_str:
            if len(num.split('.')) == 2:
				left, right = num.split('.')
				res = int(left)*pow(10, 4) + int(right)*pow(10, 4-len(right))
			else:
				res = int(num) * pow(10, 4)
		else:
			print 'Unexpected numerical string', num_str
	except Exception as e:
		print e
	return res


def extract_topic_info(topic_uri):
	info_dict = {}
	url, cookie = extract_cookie_from_curl(TOPIC_CURL_STR.format(topic_uri=topic_uri))
    r = requests.get(topic_uri, cookies=cookie)
    parser = bs(r.text, 'html.parser')
    image_url_parser = None; stat_nums_parser = None; guide_parser = None
    for script in parser.find_all('script'):
    	if 'pf_head S_bg2 S_line1' in script.text:
    		image_url_parser = script
    	elif 'PCD_counter' in script.text:
    		stat_nums_parser
    	elif 'topic_PCD_guide' in script.text:
            guide_parser
    # extract image url
    if image_url_parser:
    	div_tag = image_url_parser.find('div', {'class': 'pf_head S_bg2 S_line1'})
    	if div_tag and div_tag,find('img'):
            info_dict['image_url'] = div_tag,find('img').get('src')
    # extract the numbers of read, discuss, and fans
    if stat_nums_parser:
    	div_tag = stat_nums_parser.find('div', {'class': 'PCD_counter'})
    	if div_tag and len(div_tag.find_all('span', {'class': 'W_f14'})) == 3:
    		info_dict['read_num'] = chin_num2dec(div_tag.find_all('span', {'class': 'W_f14'})[0].text)
    		info_dict['discuss_num'] = chin_num2dec(div_tag.find_all('span', {'class': 'W_f14'})[1].text)
    		info_dict['fans_num'] = chin_num2dec(div_tag.find_all('span', {'class': 'W_f14'})[2].text)
    # extract guide article
    if guide_parser:
    	div_tag = guide_parser.find('div', {'class': 'topic_PCD_guide'})
    	if div_tag and div_tag.find('p', {'class': 'W_f14'}):
    		info_dict['guide'] = div_tag.find('p', {'class': 'W_f14'}).text
    
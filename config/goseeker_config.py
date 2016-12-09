CHUNK_SIZE = 10000

TOPIC_URL_DICT = {
    '新浪微博_评论48992': """
        SELECT weibo_url, createdate FROM weibo w 
        WHERE 1=1   -- Weibo 还没有爬过comment 的列表
        AND createdate  > date_sub(NOW(), INTERVAL '5' DAY)
        AND  not exists(
        SELECT * FROM weibocomment WHERE weibo_url = w.weibo_url)
        AND cast(weibo_thumb_up_num AS signed) > 100 
        ORDER BY w.createdate DESC
    """,
    '知乎_关键词搜索': """
        SELECT CONCAT('http://www.zhihu.com/search?type=content&q=', REPLACE (title, '#', '')) 
        AS zhihu_search_url from topicinfo t
        WHERE theme LIKE '新浪微博_热门话题%'
        AND not exists (
        SELECT * FROM zhihusearchtopic WHERE search_keyword  = t.title)
        AND createdate > DATE_SUB(now(),INTERVAL '5' DAY)
    """,
    '新浪微博_话题48992': """
        SELECT topic_url, createdate FROM topicinfo t
        -- TopicInfo 没有爬过的Topic数据
        WHERE 1 = 1 AND createdate > date_sub(NOW(), INTERVAL '5' DAY )
        AND theme LIKE '新浪微博_热门话题%'
        AND not exists (
        SELECT * FROM topicweiborelation 
        WHERE topic_url = t.topic_url)
        UNION  -- TopicInfo 微博数量太少的话题
        SELECT t.topic_url, max(t.createdate) AS createdate 
        FROM topicinfo t, topicweiborelation tw
        WHERE t.topic_url = tw.topic_url
        AND createdate > date_sub(NOW(), INTERVAL '5' DAY )
        GROUP BY topic_url
        HAVING count(*) < 20 
    """, 
    '新浪微博_话题详情48992': """
        SELECT  topic_url FROM topicinfo 
        WHERE theme LIKE '新浪微博_热门话题%' 
        AND createdate > date_sub(NOW(), INTERVAL '5' DAY )
    """,
    # '新浪微博_KOL_Gold_详细信息48992': """
    #     SELECT DISTINCT KOL_url from weibokoltype 
    #     WHERE KOL_type like '%_icon%'
    #     AND fans_num > 0
    # """,
    '新浪微博_博主详细信息48992_daily': """
        SELECT DISTINCT concat(CommentAuthor.weibocomment_author_url, '/info') FROM 
        (SELECT  wc.weibocomment_author_url FROM topicinfo t, topicweiborelation twr, weibocomment wc
        WHERE t.createdate > date_sub(now(), INTERVAL '1' DAY)
        AND t.topic_url = twr.topic_url
        AND twr.weibo_url = wc.weibo_url
        ) AS CommentAuthor LEFT JOIN WeiboUser wu ON CommentAuthor.weibocomment_author_url = wu.weibo_user_url 
        WHERE wu.weibo_user_url IS NULL
    """,
    '新浪微博_博主详细信息48992':"""
        SELECT CONCAT(tu.weibocomment_author_url ,'/info') 
        FROM temp_weibo_user_label tu LEFT JOIN weibouser wu 
        ON tu.weibocomment_author_url = wu.weibo_user_url 
        WHERE wu.weibo_user_url is  NULL AND tu.id > 2700645 
        ORDER BY tu.id LIMIT 500000, 1000000
    """,
}

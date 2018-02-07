# -*- coding: utf-8 -*-
"""
A simple example, have fun!
"""
__title__ = 'pgrsearch'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

from TEDT import TEDT

urls = [
    'http://www.cankaoxiaoxi.com/china/20170630/2158196.shtml',  # 参考消息
    'http://news.ifeng.com/a/20180121/55332303_0.shtml',  # 凤凰资讯
    'http://china.huanqiu.com/article/2018-01/11541273.html',  # 环球网
    'http://news.china.com/socialgd/10000169/20180122/31990621.html',  # 中华网
    'http://www.thepaper.cn/newsDetail_forward_1962275',  # 澎湃新闻
    # 'http://news.szu.edu.cn/info/1003/4989.htm',  # 深圳大学新闻网
    'http://www16.zzu.edu.cn/msgs/vmsgisapi.dll/onemsg?msgid=1712291126498126051',  # 郑州大学新闻网
    'http://news.ruc.edu.cn/archives/194824',  # 人民大学新闻网
    'http://xinwen.ouc.edu.cn/Article/Class3/xwlb/2018/01/22/82384.html',  # 中国海洋大学新闻网
    'http://news.sjtu.edu.cn/info/1002/1645201.htm',  # 上海交通大学新闻网
]
for url in urls:
    t = TEDT(url, LOG_LEVEL='INFO',)
    t.ie()

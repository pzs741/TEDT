# -*- coding: utf-8 -*-
"""
util主要完成了以下工作：
1.提供分句符、词性、特殊中文字符、转义字符
2.构造单词之间的边
3.将单词按关键程度从大到小排序
"""
__title__ = 'TEDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import networkx as nx
import numpy as np
import logging

chinese_character = ['来源', '编辑', '收藏', '分享', '评论', '参考消息', '责任编辑', '海外', '微', '信', '扫描',
                     '二维码', '好友', '朋友', '朋友圈', '参与', '月', '日', '星期', '联合', '联合早报', '早报', '新华社',
                     '人民网', '人民日报', '日报', '经济网', '新闻', '央视', '缩小', '字体', '放大', '字体', '微博', '腾讯',
                     '空间', '环球网', '扫', '一', '手机', '阅读', '空间', '新浪', 'qq', '日报', '作者', '记者', '姓名',
                     '责任', '参与', '互动', '点击', '下一页', '继续', '阅读', '全文', '看过', '本文', '文章', '记者',
                     '通讯', '通讯员', '热词', '澎湃', '新闻', '报料', '未经', '授权', '不得', '转载', '关键', '关键词',
                     '人民', '人民日报', '声明', '本文', '入驻', '搜狐', '作者', '撰写', '官方', '账号', '观点', '电题',
                     '作者', '本人', '立场', '阅读', '投诉', '关键', '关键字', '打印', '网页', '反馈', '首页', '人人网',
                     '百度', '贴吧', '朋友', '开心网', '一键', '分享', '本版', '导读', '日期', '版次', '快报', '未经',
                     '未经许可', '许可', '禁止', '转载', '更多', '精彩', '精彩内容', '内容', '登录', '关注', '中新网',
                     '字号', '超大', '标准', '跟踪', '更多', '下载', '小时', '客户', '客户端', '订阅', '手机报', '手机',
                     '推荐', '标签', '原标题', '新闻网', '网', '您', '位置', '联络', '邮箱', '凤凰', '产品', '注册',
                     '标题', '图片', '版权', '作品', '违者', '追究', '法律', '责任', '书面', '授权', '环球网', '生活',
                     '文史', '审批', '职务', '撰稿', '摄影', '联系', '电话', '浏览', '次数', '发表', '撰稿',
                     '撰稿人', '供稿', '单位', '总数', '访问', '建议', '浏览器', '浏览', '本站', '版权', '所有', '投稿',
                     '人', '上一条', '摄影', '系统', '管理员', '主办', '网管',  '来稿', '关闭', '窗口', '网易',
                     '首页', '应用', '公开课', '直播', '欢迎', '安全', '退出', '下载', '小时', '手机', '订阅', '移动',
                     '联通', '电信', '用户', '发送', '短信', '信息', '内容', '浏览', '次数', '在线', '其它', '首页',
                     '业界', '正文', '凤凰网', '频道','组图','国际'
                     ]
html_character = {'&spades;': '♠', '&clubs;': '♣', '&hearts;': '♥', '&diams;': '♦', '&loz;': '◊', '&dagger;': '†',
                  '&Dagger;': '‡', '&iexcl;': '¡', '&iquest;': '¿', '&larr;': '←', '&uarr;': '↑', '&rarr;': '→',
                  '&darr;': '↓', '&harr;': '↔', '&crarr;': '↵', '&lceil;': '⌈', '&rceil;': '⌉', '&lfloor;': '⌊',
                  '&rfloor;': '⌋', '&lt;': '<', '&gt;': '>', '&le;': '≤', '&ge;': '≥', '&times;': '×', '&divide;': '÷',
                  '&minus;': '−', '&plusmn;': '±', '&ne;': '≠', '&sup1;': '1¹', '&sup2;': '2²', '&sup3;': '3³',
                  '&frac12;': '½', '&frac14;': '¼', '&frac34;': '¾', '&permil;': '‰', '&deg;': '°', '&radic;': '√',
                  '&infin;': '∞', '&curren;': '¤', '&'',36;': '$', '&cent;': '¢', '&pound;': '£', '&yen;': '¥',
                  '&euro;': '€', '&nbsp;': '', '&amp;': '&', '&quot;': '"', '&copy;': '©', '&reg;': '®', '&trade;': '™',
                  '&ldquo;': '“', '&rdquo;': '”', '&lsquo;': '‘', '&rsquo;': '’', '&laquo;': '«', '&raquo;': '»',
                  '&lsaquo;': '‹', '&rsaquo;': '›', '&sect;': '§', '&para;': '¶', '&bull;': '•', '&middot;': '•',
                  '&hellip;': '…', '&'',124;': '|', '&brvbar;': '¦', '&ndash;': '–', '&mdash;': '—', '&copy;': '©',
                  '&'',124;': '|', '&middot;': '•', '&uarr;': '↑', '&euro;': '€', '&sup2;': '²²', '&frac12': '½',
                  '&hearts;': '♥', '\a': '', '\b': '', '\f': '', '\r': '', '\t': '', '\v': '', '\\': '', '\'': '',
                  '\"': '',
                  '\?': '', '\0': '', '\ooo': '', ' ': '', '　': '', }
allow_speech_tags = ['an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt', 'nz', 't', 'v', 'vd', 'vn', 'eng']
sentence_delimiters = ['?', '!', ';', '？', '！', '。', '；', '，','\n']
no_chinese = "[^\u4e00-\u9fa5\\[\\]?!;？！。；“”0-9]"
chinese = "[\u4e00-\u9fa5]"
number = "[0-9]"


class AttrDict(dict):
    """将字典转换成对象的小技巧"""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


DEBUG = True


def log(level, msg):
    global DEBUG
    if DEBUG:
        if level == 'info':
            logging.info(msg)
        elif level == 'warning':
            logging.warning(msg)
        elif level == 'debug':
            logging.debug(msg)
        elif level == 'error':
            logging.error(msg)
    else:
        pass


def combine(word_list, window=2):
    """构造在window下的单词组合，用来构造单词之间的边。

    Keyword arguments:
    word_list  --  list of str, 由单词组成的列表。
    windows    --  int, 窗口大小。
    """
    if window < 2: window = 2
    for x in range(1, window):
        if x >= len(word_list):
            break
        word_list2 = word_list[x:]
        res = zip(word_list, word_list2)
        for r in res:
            yield r


def sort_words(vertex_source, edge_source, window=2, pagerank_config={'alpha': 0.85, }):
    """将单词按关键程度从大到小排序

    Keyword arguments:
    vertex_source   --  二维列表，子列表代表句子，子列表的元素是单词，这些单词用来构造pagerank中的节点
    edge_source     --  二维列表，子列表代表句子，子列表的元素是单词，根据单词位置关系构造pagerank中的边
    window          --  一个句子中相邻的window个单词，两两之间认为有边
    pagerank_config --  pagerank的设置
    """
    sorted_words = []
    word_index = {}
    index_word = {}
    _vertex_source = vertex_source
    _edge_source = edge_source
    words_number = 0
    for word_list in _vertex_source:
        for word in word_list:
            if not word in word_index:
                word_index[word] = words_number
                index_word[words_number] = word
                words_number += 1

    graph = np.zeros((words_number, words_number))

    for word_list in _edge_source:
        for w1, w2 in combine(word_list, window):
            if w1 in word_index and w2 in word_index:
                index1 = word_index[w1]
                index2 = word_index[w2]
                graph[index1][index2] = 1.0
                graph[index2][index1] = 1.0

    nx_graph = nx.from_numpy_matrix(graph)
    scores = nx.pagerank(nx_graph, **pagerank_config)
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    for index, score in sorted_scores:
        item = AttrDict(word=index_word[index], weight=score)
        sorted_words.append(item)

    return sorted_words

def extend_config(config, config_items):
    """
    We are handling config value setting like this for a cleaner api.
    Users just need to pass in a named param to this source and we can
    dynamically generate a config object for it.
    """
    for key, val in list(config_items.items()):
        if hasattr(config, key):
            setattr(config, key, val)

    return config

class Configuration(object):
    def __init__(self):
        """
        Modify any of these Article / Source properties
        TODO: Have a separate ArticleConfig and SourceConfig extend this!
        """

        self.CENTER_DISTANCE_MIN = 0  #最小文本行间距
        self.CENTER_DISTANCE_MAX = 10  # 最大文本行间距
        self.TITLE_MIN_LENGTH = 5  # 最小标题长度
        self.TITLE_MAX_LENGTH = 50  # 最大标题长度
        self.LOG_ENABLE = True  # 是否开启日志
        self.LOG_LEVEL  = 'WARNING' #默认日志等级
        self.ADAPTIVE = True #是否自适应网页密度结构



if __name__ == '__main__':
    pass

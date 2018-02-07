# -*- coding: utf-8 -*-
"""
candidate_corpus主要完成了
1.url获取            -- 自动编解码
2.网页源代码预处理    -- 只保留文本行和空行
3.初始化语料库       -- 依据风险因子（虚假标题强化语料）
4.生成语料库         -- CDM模型双向判定
5.生成标题候选队列    -- 依据风险因子过滤
"""
__title__ = 'TEDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import requests
import re

from .segmentation import get_default_stop_words_file
from .corpus_decision_model import CDM
from .util import html_character, log
from jieba import cut_for_search


def get_url(url):
    """获取url地址并根据网页编码格式自动解析

    Keyword arguments:
    url                    -- 用户传入地址，头部必须含有http：//
    Return:
        网页源代码（为了下一步预处理方便，所有英文字母转换为小写）
        网页编解码
    """

    r = requests.get(url)
    charset = r.apparent_encoding
    r.encoding = charset
    html_code = r.text.lower()

    log('debg', '获取【{}】成功，网页编码格式为：【{}】'.format(url, charset))
    return html_code, charset


def html_clean(html_code):
    """获取网页源代码并进行预处理

    Keyword arguments:
    html_code           -- 网页源代码，字符串类型
    Return:
        清洗后的网页源代码（只包含文本和换行符\n）
    """
    temp = re.sub('<script([\s\S]*?)</script>', '', html_code)
    temp = re.sub('<style([\s\S]*?)</style>', '', temp)
    html_cleaned = re.sub('(?is)<.*?>', '', temp)
    for item in html_character:
        html_cleaned = html_cleaned.replace(item, html_character[item])

    log('debug', '网页源代码预处理完成：\n【{}】'.format(html_cleaned))
    return html_cleaned


def intersection(fake_title, unit):
    """对两个list求交集，并返回相同元素的个数

    Keyword arguments:
    fake_title, unit            -- 列表类型
    Return:
        相同元素的个数
    """
    same = 0
    for i in fake_title:
        if i in unit:
            same += 1
    return same


def drop_stopwords(list):
    """去停词

    Keyword arguments:
    list            -- 列表类型
    Return:
        不含停词的list
    """
    stopwords_list = []
    with open(get_default_stop_words_file(), encoding='utf-8') as stopwords:
        for line in stopwords:
            stopwords_list.append(line.replace('\n', ''))

    list_clean = []
    for i in list:
        if i not in stopwords_list:
            list_clean.append(i)
    return list_clean


def list_mapping(html_cleaned):
    """将预处理后的网页文档映射成列表和字典，并提取虚假标题

    Keyword arguments:
    html_cleaned            -- 预处理后的网页源代码，字符串类型
    Return:
        unit_raw                -- 网页文本行
        init_dict               -- 字典的key是索引，value是网页文本行，并按照网页文本行长度降序排序
        fake_title              -- 虚假标题，即网页源代码<title>中的文本行
    """
    unit_raw = html_cleaned.split('\n')
    for i in unit_raw:
        c = CDM(i)
        if c.PTN is not 0:
            fake_title = i
            break

    init_list = []
    init_dict = {}
    for i in unit_raw:
        init_list.append(len(i))
    for i in range(0, len(init_list)):
        init_dict[i] = init_list[i]
    init_dict = sorted(init_dict.items(), key=lambda item: item[1], reverse=True)
    try:
        log('debug', '映射成功，提取的虚假标题为：【{}】'.format(fake_title))
    except UnboundLocalError:
        fake_title = ''
        log('err', '虚假标题提取失败')
    return unit_raw, init_dict, fake_title


def first_unit(unit_raw, init_dict, fake_title):
    """初始化语料库，提取的是文本行长度最大且与虚假标题相似度最大的文本行

    Keyword arguments:
    unit_raw                -- 预处理后的网页文本行，只有文本行和空行
    Return:
        init_corpus               -- 第一个加入语料库的文本行
    """
    init_corpus = {}
    for i in range(0, 3):
        try:
            c = CDM(unit_raw[init_dict[i][0]])
            init_corpus[init_dict[i][0]] = c.get_alpha([i for i in cut_for_search(fake_title)]) + c.SN
        except IndexError:
            break
    init_corpus = sorted(init_corpus.items(), key=lambda item: item[1], reverse=True)

    log('debug', '\n初始化语料库完成，初始语料为：【{}】\n'.format(unit_raw[init_corpus[0][0]]))
    return init_corpus


class CandidateCorpus(object):
    """ 选取语料库 """

    def __init__(self, url,CENTER_DISTANCE_MIN,CENTER_DISTANCE_MAX,TITLE_MIN_LENGTH,TITLE_MAX_LENGTH):
        """
        Keyword arguments:
        url             -- 网页地址，str类型
        html_code       -- 网页源代码，str类型
        html_cleaned    -- 预处理后的网页源代码，str类型
        unit_raw        -- 网页文本行，list类型
        init_corpus     -- 初始化的语料库
        index           -- 初始化语料库的索引值
        """
        self.url = url
        self.cd_min = CENTER_DISTANCE_MIN
        self.cd_max = CENTER_DISTANCE_MAX
        self.title_min = TITLE_MIN_LENGTH
        self.title_max = TITLE_MAX_LENGTH
        self.html_code, self.charset = get_url(url)
        self.html_cleaned = html_clean(self.html_code)
        self.unit_raw, self.init_dict, self.fake_title = list_mapping(self.html_cleaned)
        self.init_corpus = first_unit(self.unit_raw, self.init_dict, self.fake_title)
        self.index = None


    def get_corpus(self):
        """获取语料库

        Return:
        corpus               -- 语料库，str类型
        """

        # 正向判定
        corpus = []
        cd = 0
        tag = None
        for i in range(0, self.init_corpus[0][0]):
            init_unit = self.unit_raw[self.init_corpus[0][0] - i]
            cdm = CDM(init_unit)
            alpha = cdm.get_alpha()

            if cd <= self.cd_min and cdm.NC is not 0:
                tag = True
            if cd > self.cd_max or cdm.NC == 0:
                tag = False
            if cd in range(self.cd_min + 1, self.cd_max) and cdm.NC is not 0:
                if alpha > 0:
                    tag = True
                else:
                    tag = False

            if cdm.NC == 0:
                cd += 1
            else:
                cd = 0

            if tag == True:
                corpus.append(init_unit)
            elif tag == False:
                if alpha < 0 or cd > self.cd_max:
                    break
                else:
                    continue
        corpus = list(reversed(corpus))
        try:
            self.index = self.init_corpus[0][0] - i + 1
        except UnboundLocalError:
            log('err', '正向判定完成，索引定位出错')
            self.index = self.init_corpus[0][0]

        # 反向判定
        cd = 0
        tag = None
        for i in range(1, len(self.unit_raw) - self.init_corpus[0][0]):
            init_unit = self.unit_raw[self.init_corpus[0][0] + i]
            cdm = CDM(init_unit)
            alpha = cdm.get_alpha()

            if cd <= self.cd_min and cdm.NC is not 0:
                tag = True
            if cd > self.cd_max or cdm.NC == 0:
                tag = False
            if cd in range(self.cd_min + 1, self.cd_max) and cdm.NC is not 0:
                if alpha > 0:
                    tag = True
                else:
                    tag = False

            if cdm.NC == 0:
                cd += 1
            else:
                cd = 0

            if tag == True:
                corpus.append(init_unit)
            elif tag == False:
                if alpha < 0 or cd > self.cd_max:
                    break
                else:
                    continue
        log('debug', '\n获取语料库成功:【{}】\n'.format(corpus))
        return ''.join(corpus)

    def get_queue(self):
        """获取新闻标题候选队列

        Return:
        queue               -- 新闻标题候选队列，list类型
        """
        queue = []
        for i in range(0, self.index):
            unit = self.unit_raw[i]
            c = CDM(unit)
            # 过滤
            if c.get_alpha() > 0 and c.PTN in range(self.title_min, self.title_max):
                queue.append(unit)

        if queue == []:
            pass
        else:
            log('debug', '\n获取标题候选队列成功：【{}】\n'.format(queue))

        return queue


if __name__ == '__main__':
    pass

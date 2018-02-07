# -*- coding: utf-8 -*-
"""
information_extraction主要完成了：
1.生成语料库         -- CDM模型
2.计算单词权重集合   -- TextRank算法
3.抽取新闻标题       -- 改进的Jaccard相似度计算公式
"""
__title__ = 'TEDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import logging
import re

from .candidate_corpus import CandidateCorpus
from .candidate_title import CandidateTitle
from .release_time import TimeExtractor
from .text_rank import TextRank
from .util import log, extend_config, Configuration


def fake_title_cut(fake_title):
    try:
        matching = re.match('^(.*?)[-_|]', fake_title)
        title = matching.group(0)[:-1]
        return title
    except:
        return fake_title


class TEDT(object):
    """ 基于密度及文本特征的新闻标题抽取算法 """

    def __init__(self, url, config=None, **kwargs):

        """
        Keyword arguments:
        url                -- 网页地址，str类型
        corpus             -- 语料库，str类型
        queue              -- 标题候选队列，list类型
        title              -- 新闻标题，str类型
        time               -- 发布时间，date类型
        """
        self._config = config or Configuration()
        self._config = extend_config(self._config, kwargs)
        if self._config.LOG_ENABLE:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=self._config.LOG_LEVEL)
        self.url = url
        self.corpus = None
        self.queue = None
        self.title = None
        self.time = None
        self._wordvector = None
        self._faketitle = None
        self._html_cleaned = None

    def cdm(self):
        # 语料判定模型
        cc = CandidateCorpus(self.url, self._config.CENTER_DISTANCE_MIN, self._config.CENTER_DISTANCE_MAX,
                                 self._config.TITLE_MIN_LENGTH, self._config.TITLE_MAX_LENGTH)
        self.corpus = cc.get_corpus()
        self.queue = cc.get_queue()
        self._faketitle = cc.fake_title
        self._html_cleaned = cc.html_cleaned

    def queue_adaptive(self):
        # 标题候选队列生成自适应
        while self.queue == [] and self._config.CENTER_DISTANCE_MIN >= -1:
            self._config.CENTER_DISTANCE_MIN -= 1
            log('warning', '获取标题候选队列失败，自动调节CDM模型参数CD：{}'.format(self._config.CENTER_DISTANCE_MIN))
            cc = CandidateCorpus(self.url, self._config.CENTER_DISTANCE_MIN, self._config.CENTER_DISTANCE_MAX,
                                 self._config.TITLE_MIN_LENGTH, self._config.TITLE_MAX_LENGTH)
            self.corpus = cc.get_corpus()
            self.queue = cc.get_queue()

    def text_rank(self):
        # 通过TextRank算法构建key-value权重集合，获得词（key）和词对应的权重（value）
        tr = TextRank()
        tr.analyze(self.corpus)
        self._wordvector = tr.wordvector()

    def title_extractor(self):
        # 利用改进的相似度计算方法，从标题候选队列中抽取新闻标题。
        ct = CandidateTitle(self.queue, self._wordvector, self._faketitle)
        self.title = ct.vote()

    def title_adaptive(self):
        # 标题抽取自适应
        while self.title == '' and self._config.CENTER_DISTANCE_MIN >= -1:
            self._config.CENTER_DISTANCE_MIN -= 1
            log('warning', '获取新闻标题失败，自动调节CDM模型参数CD：{}'.format(self._config.CENTER_DISTANCE_MIN))
            cc = CandidateCorpus(self.url, self._config.CENTER_DISTANCE_MIN, self._config.CENTER_DISTANCE_MAX,
                                 self._config.TITLE_MIN_LENGTH, self._config.TITLE_MAX_LENGTH)
            self.corpus = cc.get_corpus()
            self.queue = cc.get_queue()
            self.text_rank()
            self.title_extractor()

        if self.title == '':
            log('warning', '真实标题抽取失败,返回<title>标签文本。')
            self.title = fake_title_cut(self._faketitle)
            if self.title == '':
                log('error', 'TEDT算法抽取失败')

    def time_extractor(self):
        # 时间信息抽取算法
        te = TimeExtractor()
        self.time = te.find(self._html_cleaned)

    def ie(self):
        """信息抽取"""

        self.cdm()
        if self._config.ADAPTIVE:
            self.queue_adaptive()
        self.text_rank()
        self.title_extractor()
        if self._config.ADAPTIVE:
            self.title_adaptive()
        self.time_extractor()

        log('info', '------------------------------TEDT------------------------------')
        log('info', '标题：【{}】'.format(self.title))
        log('info', '时间：【{}】'.format(self.time))
        log('info', '正文：【{}】'.format(self.corpus))
        log('info', '*****************************************************************')


if __name__ == '__main__':
    pass

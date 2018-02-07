# -*- coding: utf-8 -*-
"""
corpus_decision_model主要完成了：
1.计算六大参数            -- 文本特征
2.强化因子EF              -- 通过词语权重集合强化标题候选队列文本行
3.计算风险因子            -- 正文分布密度与语言特征相融合
"""
__title__ = 'TEDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import re

from .util import chinese_character, sentence_delimiters, chinese, number, no_chinese, log
from jieba import cut_for_search
from math import log as ln


def get_ptn(unit):
    """获取文本行的中文字符的个数

    Keyword arguments:
    unit                    -- 文本行
    Return:
        ptn                 -- 纯文本数
    """
    ptn = 0
    match_re = re.findall(chinese, unit)
    if match_re:
        string = ''.join(match_re)
        ptn = len(string)
    return int(ptn)


def get_sn(unit):
    """获取文本行的句子数量

    Keyword arguments:
    unit                    -- 文本行
    Return:
        sn                  -- 句数
    """
    sn = 0
    match_re = re.findall(str(sentence_delimiters), unit)
    if match_re:
        string = ''.join(match_re)
        sn = len(string)
    return int(sn)


def get_nn(unit):
    """获取文本行中阿拉伯数字数的个数

    Keyword arguments:
    unit                    -- 文本行
    Return:
        nn                  -- 数字数
    """
    nn = 0
    match_re = re.findall(number, unit)
    if match_re:
        string = ''.join(match_re)
        nn = len(string)
    return int(nn)


def get_spn(unit):
    """获取文本行中非中文字符数的个数

    Keyword arguments:
    unit                    -- 文本行
    Return:
        spn                 -- 特殊字符数
    """
    spn = 0
    match_re = re.findall(no_chinese, unit)
    if match_re:
        string = ''.join(match_re)
        spn = len(string)
    return int(spn)


def get_scn(unit):
    """获取文本行中可能不属于新闻正文的单词的个数

    Keyword arguments:
    unit                    -- 文本行
    Return:
        scn                  -- 特殊中文字符
    """
    scn = 0
    list = cut_for_search(unit)
    for x in list:
        for y in chinese_character:
            if x == y:
                scn += len(y)
    return int(scn)


def get_ef(unit, iterative):
    ef = 0
    list = cut_for_search(unit)
    for x in list:
        for y in iterative:
            if x == y:
                ef += len(y)
    return int(ef)


class CDM(object):
    """ 语料判定模型 """

    def __init__(self, unit):
        """
        Keyword arguments:
        unit            -- 文本行，str类型
        PTN             -- 纯文本数，int类型
        SN              -- 句数，int类型
        NN              -- 数字数，int类型
        SPN             -- 特殊字符数，int类型
        SCN              -- 特殊中文字符，int类型
        NC              -- 字符数，int类型
        """
        self._unit = unit
        self.PTN = get_ptn(unit)
        self.SN = get_sn(unit)
        self.NN = get_nn(unit)
        self.SPN = get_spn(unit)
        self.SCN = get_scn(unit)
        self.NC = len(unit)
        self.EF = 0

    def get_alpha(self, *args):
        """计算风险因子

        Return:
        alpha               -- 风险因子，float类型
        """
        for x in args:
            self.EF += get_ef(self._unit, x)
        molecular = self.PTN + self.EF - self.SCN + 1
        denominator = self.NN + self.SPN + self.SCN - self.EF + 1
        if molecular <= 0:
            molecular = 1
        if denominator <=0:
            denominator = 1
        fraction = molecular / denominator
        if args:
            alpha = ln(fraction)
            log('debug',
                '当前参数如下：\n文本行：【{}】\n纯文本数：【{}】，强化因子：【{}】，数字数：【{}】，特殊字符数：【{}】，特殊中文字符：【{}】，字符数：【{}】\n风险因子：【{}】，句数：【{}】'.format(
                    self._unit, self.PTN, self.EF, self.NN, self.SPN, self.SCN, self.NC, alpha, self.SN))
        else:
            alpha = ln(fraction) + self.SN
            log('debug',
                '当前参数如下：\n文本行：【{}】\n纯文本数：【{}】，句数：【{}】，数字数：【{}】，特殊字符数：【{}】，特殊中文字符：【{}】，字符数：【{}】\n风险因子：【{}】'.format(
                    self._unit, self.PTN, self.SN, self.NN, self.SPN, self.SCN, self.NC, alpha))
        return alpha


if __name__ == '__main__':
    pass

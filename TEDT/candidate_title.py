# -*- coding: utf-8 -*-
"""
candidate_title主要完成了：
0.规避虚假标题       -- TEDT与所有标题抽取算法最大的区别在于通用且准确抽取真实新闻标题
1.计算相似度         -- 改进的jaccard相似度计算公式
2.归一化风险因子     -- 风险因子强化标题
2.选举标题           -- 位置权重*调整后的风险因子*jaccard系数
"""
__title__ = 'TEDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

from .segmentation import WordSegmentation
from .corpus_decision_model import CDM
from .util import log


def convert_to_set(unit):
    """将文本行转换成集合形式

    Keyword arguments:
    unit                    -- 文本行
    Return:
        set_unit            -- 切分、去停词、去重后的文本行，list类型
    """
    w = WordSegmentation()
    set_unit = set(w.segment(unit))
    set_unit = [i for i in set_unit]
    return set_unit


def get_beta_list(queue, *args):
    """获取调整后的风险因子列表，用于归一化风险因子系数

    Keyword arguments:
    queue                    -- 标题候选队列
    *args                    -- 强化ef，客串如多个list
    Return:
        beta_list            -- 所有候选标题的beta，list类型
    """
    beta_list = []
    for i in queue:
        c = CDM(i)
        beta_list.append(c.get_alpha(*args))
    return beta_list


def normalized(beta, beta_list):
    """归一化函数

    Keyword arguments:
    beta                     -- 当前文本行的beta值，float类型
    beta_list                -- 标题候选队列的beta队列，list类型
    Return:
        result               -- 归一化结果，区间【0，1】
    """
    if len(beta_list) <= 2:
        # beta_list元素小于等于2时，根据jiaccard相似度公式进行判定
        return 1
    try:
        result = (beta - min(beta_list)) / (max(beta_list) - min(beta_list))
    except ZeroDivisionError:
        result = 1
    return result


class CandidateTitle(object):
    """ 新闻标题 """

    def __init__(self, queue, wordvector, fake_titile):
        """
        Keyword arguments:
        queue             -- 标题候选队列，list类型
        wordvector        -- 语料库单词权重集合，dict类型
        wordvector_word   -- 所有单词，list类型
        wordvector_weight -- 单词对应的权重，list类型
        """
        #过滤虚假新闻标题
        try:
            if queue[0] == fake_titile:
                self._queue = [i for i in queue[1:]]
            else:
                self._queue = [i for i in queue]
        except IndexError:
            self._queue = queue
        self._fake_titile = fake_titile
        self.wordvector = wordvector
        self.wordvector_word = [i.word for i in wordvector]
        self.wordvector_weight = [i.weight for i in wordvector]
        self.beta_list = get_beta_list(self._queue, self.wordvector_word)

    def vote(self):
        """选举新闻标题

        Return:
        title               -- 新闻标题，str类型
        """

        # 初始化
        weight_queue = []
        sameKV = 0
        count = 0
        # 相似度计算
        for unit in self._queue:
            unit_set = convert_to_set(unit)
            for i in unit_set:
                if i in self.wordvector_word:
                    sameKV += self.wordvector_weight[self.wordvector_word.index(i)]

            if len(self._queue) >= 5:
                # k是位置权重，离语料库越近的文本行，权重越大，区间【0，1】
                k = (count + 1) / len(self._queue)
                beta = normalized(self.beta_list[count], self.beta_list)
                count += 1
            else:
                k = 1
                beta = normalized(self.beta_list[count], self.beta_list)
                count += 1
            jaccard = sameKV / len(
                (set(unit_set) | set(self.wordvector_word)) - (set(unit_set) & set(self.wordvector_word)))
            unit_weight = k * beta * jaccard
            weight_queue.append(unit_weight)
            sameKV = 0
            log('debug',
                '文本行【{}】\n相似度计算参数，unit_weight:【{}】，k:【{}】,beta:【{}】,jaccard:【{}】\n'.format(unit, unit_weight, k, beta,
                                                                                           jaccard))

        # 过滤
        try:
            title = self._queue[weight_queue.index(sorted(weight_queue, reverse=True)[0])]
        except:
            title = ''

        return title


if __name__ == '__main__':
    pass

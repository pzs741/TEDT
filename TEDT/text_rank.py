# -*- coding: utf-8 -*-
"""
TEDT的TextRank算法部分借鉴了大量TextRank4ZH关键词抽取算法中的代码，下面是他们的许可证：
https://github.com/letiantian/TextRank4ZH/blob/master/LICENSE
再次对TextRank4ZH作者letiantian表示感谢

text_rank主要完成了：
1.按照完整句子，分割corpus集合
2.对于每个句子进行分词和词性标注处理，并过滤掉停用词，只保留指定词性的单词
3.构建单词有向图
4.迭代传播各节点的权重，直至收敛
5.输出单词权重集合
"""
__title__ = 'TEDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

from .segmentation import Segmentation
from . import util


class TextRank(object):
    def __init__(self, stop_words_file=None,
                 allow_speech_tags=util.allow_speech_tags,
                 delimiters=util.sentence_delimiters):
        """
        Keyword arguments:
        stop_words_file  --  str，指定停止词文件路径（一行一个停止词），若为其他类型，则使用默认停止词文件
        delimiters       --  默认值是`?!;？！。；…\n`，用来将文本拆分为句子。
        
        Object Var:
        self.words_no_filter      --  对sentences中每个句子分词而得到的两级列表。
        self.words_no_stop_words  --  去掉words_no_filter中的停止词而得到的两级列表。
        self.words_all_filters    --  保留words_no_stop_words中指定词性的单词而得到的两级列表。
        """
        self.text = ''
        self.keywords = None

        self.seg = Segmentation(stop_words_file=stop_words_file,
                                allow_speech_tags=allow_speech_tags,
                                delimiters=delimiters)

        self.sentences = None
        self.words_no_filter = None  # 2维列表
        self.words_no_stop_words = None
        self.words_all_filters = None

    def analyze(self, text,
                window=2,
                lower=False,
                vertex_source='all_filters',
                edge_source='no_stop_words',
                pagerank_config={'alpha': 0.85, }):
        """分析文本

        Keyword arguments:
        text       --  文本内容，字符串。
        window     --  窗口大小，int，用来构造单词之间的边。默认值为2。
        lower      --  是否将文本转换为小写。默认为False。
        vertex_source   --  选择使用words_no_filter, words_no_stop_words, words_all_filters中的哪一个来构造pagerank对应的图中的节点。
                            默认值为`'all_filters'`，可选值为`'no_filter', 'no_stop_words', 'all_filters'`。关键词也来自`vertex_source`。
        edge_source     --  选择使用words_no_filter, words_no_stop_words, words_all_filters中的哪一个来构造pagerank对应的图中的节点之间的边。
                            默认值为`'no_stop_words'`，可选值为`'no_filter', 'no_stop_words', 'all_filters'`。边的构造要结合`window`参数。
        """

        self.text = text
        self.word_index = {}
        self.index_word = {}
        self.keywords = []
        self.graph = None

        result = self.seg.segment(text=text, lower=lower)
        self.sentences = result.sentences
        self.words_no_filter = result.words_no_filter
        self.words_no_stop_words = result.words_no_stop_words
        self.words_all_filters = result.words_all_filters

        options = ['no_filter', 'no_stop_words', 'all_filters']

        if vertex_source in options:
            _vertex_source = result['words_' + vertex_source]
        else:
            _vertex_source = result['words_all_filters']

        if edge_source in options:
            _edge_source = result['words_' + edge_source]
        else:
            _edge_source = result['words_no_stop_words']

        self.keywords = util.sort_words(_vertex_source, _edge_source, window=window, pagerank_config=pagerank_config)

    def wordvector(self, word_min_len=2):
        """获取所有单词和权重。

        Return:
        result      --单词权重集合
        """
        result = []
        count = 0
        for item in self.keywords:
            if len(item.word) >= word_min_len:
                result.append(item)
                count += 1
        util.log('debug','获取单词权重集合成功：【{}】'.format(result))
        return result


if __name__ == '__main__':
    pass

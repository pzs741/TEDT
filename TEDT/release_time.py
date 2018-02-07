# -*- coding: utf-8 -*-
"""
release_time主要完成了：
1.中文、英文、特殊时间识别
2.新闻发布时间抽取
"""
__title__ = 'TEDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import datetime
import re
from .util import log


class TimeExtractor(object):
    """ 时间抽取 """

    def __init__(self):
        """
        Keyword arguments:
        year                -- 年，str类型
        month               -- 月，str类型
        day                 -- 日，str类型
        year_check          -- 年份检查，bool类型
        month_check         -- 月份检查，bool类型
        day_check           -- 日期检查，bool类型
        """
        self.year = ''
        self.month = ''
        self.day = ''
        self.year_check = False
        self.month_check = False
        self.day_check = False

    def str_to_num(self, arg):
        """将中文数字转换成阿拉伯数字

        Keyword arguments:
        arg             -- 含有时间的文本，str类型
        Return:
        test            -- 切转换后的阿拉伯数字
        """

        if len(arg) == 1:
            ten = '10'
        else:
            ten = ''
        switcher = {
            '一': '1',
            '二': '2',
            '三': '3',
            '四': '4',
            '五': '5',
            '六': '6',
            '七': '7',
            '八': '8',
            '九': '9',
            '十': ten,
            '〇': '0',
            '○': '0',
        }
        test = ''
        for i in arg:
            test = test + switcher.get(i, None)
        return int(test)

    def easy_time_extrator(self, string):
        """简单时间抽取，即年月日同时出现

        Keyword arguments:
        string              -- 含有时间的文本，str类型
        """
        try:
            if not self.year_check and not self.month_check and not self.day_check:
                str_all = re.search('([\u4e00-\u9fa5〇○]{4})年([\u4e00-\u9fa5]{1,3})月([\u4e00-\u9fa5]{1,3})日', string)
                str_year = self.str_to_num(str_all.group(1))
                str_month = self.str_to_num(str_all.group(2))
                str_day = self.str_to_num(str_all.group(3))
                check_year = datetime.datetime.now().year
                if str_year in range(1970, check_year + 1) and str_month in range(1, 13) and str_day in range(1,
                                                                                                              32):
                    self.year = str_year
                    self.month = str_month
                    self.day = str_day
                    self.year_check = True
                    self.month_check = True
                    self.day_check = True
        except:
            pass
        try:
            if not self.year_check and not self.month_check and not self.day_check:
                str_all = re.search('(\d{4})[-._年](\d{1,2})[-._月](\d{1,2})', string)
                str_year = int(str_all.group(1))
                str_month = int(str_all.group(2))
                str_day = int(str_all.group(3))
                check_year = datetime.datetime.now().year
                if str_year in range(1970, check_year + 1) and str_month in range(1, 13) and str_day in range(1,
                                                                                                              32):
                    self.year = str_year
                    self.month = str_month
                    self.day = str_day
                    self.year_check = True
                    self.month_check = True
                    self.day_check = True
        except:
            pass


    def common_time_extrator(self, string):
        """一般时间抽取，即年月日分别出现

        Keyword arguments:
        string              -- 含有时间的文本，str类型
        """

        try:
            if not self.year_check:
                str_year = int(re.search('(\d{4})年', string).group(1))
                check_year = datetime.datetime.now().year
                if str_year in range(1970, check_year + 1):
                    self.year = str_year
                    self.year_check = True
        except:
            pass
        try:
            if not self.month_check:
                str_month = int(re.search('(\d{1,2})月', string).group(1))
                if str_month in range(1, 13):
                    self.month = str_month
                    self.month_check = True
        except:
            pass
        try:
            if not self.day_check:
                str_day = int(re.search('(\d{1,2})[日号]', string).group(1))
                if str_day in range(1, 32):
                    self.day = str_day
                    self.day_check = True
        except:
            pass

    def special_time_extrator(self, string):
        """特殊时间抽取，即年月日单独出现

        Keyword arguments:
        string              -- 含有时间的文本，str类型
        """

        try:
            if not self.year_check:
                str_year = int(re.search('.*?(\d{4})[-._]', string).group(1))
                check_year = datetime.datetime.now().year
                if str_year in range(1970, check_year + 1):
                    self.year = str_year
                    self.year_check = True
        except:
            pass
        try:
            if not self.month_check and not self.day_check:
                str_month_day = re.search('((\d{1,2})[-._·](\d{1,2}))', string)
                str_month = int(str_month_day.group(2))
                str_day = int(str_month_day.group(3))
                if str_month in range(1, 13) and str_day in range(1, 32):
                    self.month = str_month
                    self.day = str_day
                    self.month_check = True
                    self.day_check = True
        except:
            pass

    def check_time_extrator(self):
        """将抽取得时间转换为date标准时间格式

        Keyword arguments:
        string                  -- 含有时间的文本，str类型
        Return:
        release_time            -- 新闻发布时间
        """

        if self.year_check and self.month_check and self.day_check:
            time = str(self.year) + '-' + str(self.month) + '-' + str(self.day)
            release_time = datetime.datetime.strptime(time, "%Y-%m-%d").date()
            return release_time

    def find(self, *params):
        """按照简单、一般、特殊的顺序寻找新闻发布时间

        Keyword *params:
        params                  -- 可以接收多个含有时间的文本，str类型
        """

        for string in params:
            self.easy_time_extrator(string)
            if self.check_time_extrator():
                log('debug', '通过简单模式找到时间信息')
                return self.check_time_extrator()

        for string in params:
            self.common_time_extrator(string)
            if self.check_time_extrator():
                log('debug', '通过一般模式找到时间信息')
                return self.check_time_extrator()

        for string in params:
            self.special_time_extrator(string)
            if self.check_time_extrator():
                log('debug', '通过特殊模式找到时间信息')
                return self.check_time_extrator()


if __name__ == '__main__':
    pass

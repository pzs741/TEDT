# -*- coding: utf-8 -*-
"""
A simple information_extraction_.py test, have fun!
"""
__title__ = 'pgrsearch'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

from TEDT import fake_title_cut

if __name__ == '__main__':
    text =[
        '各地干部群众热议十九届二中全会公报_新改革时代',
        '各地干部群众热议党的十九届二中全会公报_国内新闻_环球网',
        '北京干渴90天终迎初雪 雪后气温骤跌将遇冰冻周_新闻频道_中华网',
        '又有45所高校要改名，你的母校还是你的母校吗_文化课_澎湃新闻-The Paper',
        '我校举行“书记下午茶——新生专场会”-深圳大学新闻网',
        '中国人民大学召开年度校级领导班子民主生活会 - 中国人民大学新闻网 | NEWS of RUC',
        '中国人民大学召开年度校级领导班子民主生活会 | NEWS of RUC',
        '"天泰优秀人才奖""天泰奖学金"颁发 8名教师20名学子获奖-观海听涛',
        '高校思想政治理论课实地教学观摩在上海交大举行[图]-上海交通大学新闻网',
        '高校思想政治理论课实地教学观摩在上海交大举行[图]',
    ]
    for i in text:
        print(fake_title_cut(i))
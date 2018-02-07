# -*- coding: utf-8 -*-
"""
A simple release_time.py test, have fun!
"""
__title__ = 'pgrsearch'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

from TEDT import TimeExtractor

if __name__ == '__main__':
    text = '[发布时间]:2009年10月09日'
    te = TimeExtractor()
    print(te.find(text))
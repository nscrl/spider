# -*- coding:utf-8 -*-
from AllClass import *

def testSinglePage(url, externalCount=None, key=None):
    obj = BaiduZhidao()
    obj.parsePage(url,  externalCount, key)

# testSinglePage('http://zhidao.baidu.com/question/459929610.html')
testSinglePage('http://zhidao.baidu.com/question/136815046.html', 5,  '安徽工业大学')
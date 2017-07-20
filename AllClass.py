#!/usr/bin/python
#-*- coding:utf-8 -*-

import re, traceback
import urllib2
import cookielib
import lxml.html
from commonFun import *

class BaiduZhidao:
    """docstring for BaiduZhidao"""
    #问题编号
    question_id = ''
    #问题标题
    ask_title   = ''
    #问题内容，可以为空
    qContent    = ''
    #提问时间
    ask_time    = ''
    #回答内容(网友采纳、提问者采纳、专业回答)
    answer      = ''
    #回答赞同的数量
    good        = 0
    #反对该回答的数量
    bad         = 0
    #回答该问题的人在百度知道回答问题的采纳率
    adopt_rate  = ''
    #回答类型(匿名、普通、专业)
    answerType  = ''
    #回答问题的时间
    answer_time = ''
    #其它回答，otherAnswer是一个数组，每个元素是一个字典，
    #每个字典存储了每条回答的内容，时间，点赞和反对的数量
    othAnsArray = []
    # othAnsCount = 0
    ios_header = {
            # "Host":"zhidao.baidu.com",
            "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9B176 MicroMessenger/4.3.2",
            # "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            # "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
            # "Accept-Language":"en-US,en;q=0.5",
            # "Accept-Encoding":"gzip, deflate, sdch"
            # "Cookie":"Hm_lvt_6859ce5aaf00fb00387e6434e4fcc925=1461825930,1461831131,1461831975,1461840024; IK_CID_74=36; IK_CID_83=1; IK_CID_80=1; IK_0=1; BAIDUID=DE5F863065BC57E3651BF35CBDE3A4B6:FG=1; IK_DE5F863065BC57E3651BF35CBDE3A4B6=6; BIDUPSID=82BEB067413E74695911B48EFF793901; Hm_lpvt_6859ce5aaf00fb00387e6434e4fcc925=1461840515",
            # "Connection":"keep-alive",
            # "Cache-Control":"max-age=0"
            }
    wp_header   = {'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 920)'}
    pc_header   = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36'}
    #proxy       = {'http':'205.234.66.201:80'}

    def __init__(self, search_wd=None):
        # print "Construct class..."
        self.SearchREQ = ''
        if search_wd:
            self.SearchREQ = 'http://zhidao.baidu.com/search?word='+search_wd

    #重新设置搜索关键字
    def setSearchKeyWord(self, search_wd):
        self.SearchREQ = 'http://zhidao.baidu.com/search?word='+search_wd

    #解析每个搜索页面中具体的页面信息
    def parsePage(self, url=None, externalCount=None, key=None):
        url       = url.split('?')[0]
        print "Now, the script is parsing the url: ", url
        # print externalCount, "times performances the search mission"
        print "current key word: ", key 
        try:
            # setProxy(self.proxy)
            # cookie           = cookielib.CookieJar()
            # openner          = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            # openner.handle_open["http"][0].set_http_debuglevel(1)#设定开启回显
            # user_agent       ="Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:46.0) Gecko/20100101 Firefox/46.0"

            #wp_req is used to get text and time information
            #pc_req is used to get other information such as the number of people support one question
            wp_req           = urllib2.Request(url=url, headers=self.wp_header)
            pc_req           = urllib2.Request(url=url, headers=self.pc_header)
            # req.add_header("Cookie", cookie)
            # req.add_header("User-Agent",user_agent)
            # htm              = openner.open(req).read()
            try:
                wp_html          = pc_html = ''
                wp_html          = urllib2.urlopen(wp_req, timeout=30).read()
                time.sleep(1)
                pc_html          = urllib2.urlopen(pc_req, timeout=30).read()
            except Exception, e:
                offlinetime = time.time()
                print traceback.format_exc()
                count = 0
                while not len(wp_html): 
                    #if ping success, err will be 0, if not err will be 1
                    err = os.system('ping -c 2 www.qq.com')
                    if err:
                        count += 1
                        if count <= 5:
                            time.sleep(60)
                        elif count <= 10:
                            time.sleep(180)
                        else:
                            time.sleep(300)
                    else:
                        wp_html         = urllib2.urlopen(wp_req, timeout=30).read()
                        time.sleep(1)
                        pc_html         = urllib2.urlopen(pc_req, timeout=30).read()
                    if count:
                        print 'offline time has continued %s seconds\n' % str(time.time() - offlinetime)
                        writeErrorToFile(externalCount, key, url, offlinetime)

            wp_doc           = lxml.html.fromstring(wp_html)
            pc_doc           = lxml.html.fromstring(pc_html)
            self.question_id = re.findall('[0-9]+\.',url)[0].rstrip('.')
            self.ask_title   = wp_doc.xpath('//div[@class="t-txt mag2"]/p/text()')[0].replace("'",'').encode('utf-8')
            self.ask_time    = wp_doc.xpath('//div[@class="t-txt mag2"]/p/span/text()')[0].encode('utf-8')
            self.qContent    = wp_doc.xpath('//div[@class="t-txt mag2"]/p/text()')[1].encode('utf-8')

            if len(pc_doc.xpath('//pre[@class="best-text mb-10"]')):
                self.answer = strcat( wp_doc.xpath('//div[@class="t-txt"]/text()')[0] )
                ############################
                if len(self.answer) > 1000:
                    f = open("text/%s.txt" % self.question_id, "w")
                    f.write(self.answer)
                    f.close()
                self.answer_time = wp_doc.xpath('//div[@class="t-txt"]/span/text()')[0].encode('utf-8')
                self.good = 0
                if(len(pc_doc.xpath('//span[@alog-action="qb-zan-btnbestbox"]/@data-evaluate'))):
                    self.good = int(pc_doc.xpath('//span[@alog-action="qb-zan-btnbestbox"]/@data-evaluate')[0])

                self.bad = 0
                if(len(pc_doc.xpath('//span[@alog-action="qb-evaluate-outer"]/@data-evaluate'))):
                    self.bad  = int(pc_doc.xpath('//span[@alog-action="qb-evaluate-outer"]/@data-evaluate')[0])

                answerType = ''
                if len(pc_doc.xpath('//div[@class="replyer-best-box"]')):
                    #answerType = 0 indicated that this answer was answered by a registered user and with a nickname in the website
                    #answerType = 1 indicated that this answer was answered by a anonymity user
                    answerType='0'
                    # self.adopt_rate = str( int( filter(lambda x:x.isdigit(),
                    #     pc_doc.xpath('//div[@class="grid f-aid ff-arial"]/p/span[@class="mr-15"]/text()')[0] ) )/100.0 )
                    adoptRateIndex = pc_html.find('isMaster:"0",goodRate:')
                    self.adopt_rate = pc_html[adoptRateIndex : adoptRateIndex+26][-3:-1]
                else:
                    answerType='1'
                self.answerType = answerType
            else:
                self.answer      = ''
                self.answer_time = ''
                self.answerType  = ''
                self.adopt_rate  = '0.0'
                self.good        = 0
                self.bad         = 0

            # print "deal with other answers......"
            #处理其它回答
            #选择其它回答的html部分
            othAnsSels     = pc_doc.xpath('//div[@class="bd-wrap"]/div/div/div[@class="line content"]')
            othAnsCount    = len(othAnsSels)
            
            # print ("len:", item['othAnsCount'])
            retOthAnsDict  = {'othNo':0, 'othGood':0, 'othBad':0}
            retOthAnsArray = []

            if othAnsCount:
                for i in range(othAnsCount):
                    #定义字典结构
                    retOthAnsDict              = {'othNo':0, 'othGood':0, 'othBad':0}
                    othAnsDict                 = {'othNo':0, 'answer':'', 'time':'', 'othGood':'', 'othBad':''}
                    
                    retOthAnsDict['othNo']     = othAnsDict['othNo']    = i
                    othAnsDict['answer']       = strcat( othAnsSels[i].xpath('div/span[@class="con"]/text()') )
                    # othAnsDict['time']       = [x for x in othAnsSels[i].xpath('div[1]/span[1]/text()') if x!='\n'][0].encode('utf-8').strip('\n')
                    #[6:]去掉‘发布于’3个汉字
                    othAnsDict['time']         = othAnsSels[i].xpath('div/div/span[@class="pos-time"]/text()')[0][4:14].encode('utf-8')
                    # retOthAnsDict['othGood'] = othAnsDict['good']  = int(othAnsSels[i].xpath('div[2]/div[last()-1]/span[3]/@data-evaluate')[0].encode('utf-8'))
                    # retOthAnsDict['othBad']  = othAnsDict['bad']   = int(othAnsSels[i].xpath('div[2]/div[last()-1]/span[4]/@data-evaluate')[0].encode('utf-8'))
                    goodAndBad                 = othAnsSels[i].xpath('div/div/div[@class="qb-zan-eva"]/span/@data-evaluate')
                    retOthAnsDict['othGood']   = othAnsDict['othGood']  = int(goodAndBad[0])
                    retOthAnsDict['othBad']    = othAnsDict['othBad']   = int(goodAndBad[1])
                    self.othAnsArray.append(othAnsDict)
                    retOthAnsArray.append(retOthAnsDict)
            error = False
            return {'qid':          self.question_id,
                    'good':         self.good,
                    'bad':          self.bad,
                    'othAnsCount':  othAnsCount,
                    'othAnsArray':  retOthAnsArray
            }
            
        except Exception, e:
            print traceback.format_exc()
            # exit()
            error = True
            writeErrorToFile(externalCount, key, url)
            return {}

    def getPageLink(self, url=None, *args):
        externalCount  = args[0]
        currentKeyWord = args[1]
        #读取html源码,转换格式
        try:
            # self.setProxy()
            next_page   = ''
            result_page = ''
            urlArray    = []
            headers     = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36'}
            req         = urllib2.Request(url=url, headers=headers)
            try:
                result_page = urllib2.urlopen(req, timeout=30).read()
            except Exception, e:
                offlinetime = time.time()
                print traceback.format_exc()
                count = 0
                while  not len(result_page):
                    #if ping success, err will be 0, if not err will be 1
                    err = os.system('ping -c 2 www.qq.com')
                    if err:
                        count += 1
                        if count <= 5:
                            time.sleep(60)
                        elif count <= 10:
                            time.sleep(180)
                        else:
                            time.sleep(300)
                    else:
                        result_page = urllib2.urlopen(req, timeout=30).read()
                        if not len(result_page):
                            return next_page, urlArray
                if count:
                    print 'offline time has continued %s seconds\n' % str(time.time() - offlinetime)
                    writeErrorToFile(externalCount, key, url, offlinetime)
            doc         = lxml.html.fromstring(result_page)
            urlArray    = doc.xpath('//div[@class="list"]/dl/dt/a/@href')
            next_page   = doc.xpath('//a[@class="pager-next"]/@href')
            if(len(next_page)):
                next_page = 'http://zhidao.baidu.com' + next_page[0]
            else:
                next_page = ''
                
        except Exception, e:
            # print traceback.format_exc()
            error = True
            #记录错误信息
            writeErrorToFile(externalCount, currentKeyWord, url)
            # exit()
        return next_page, urlArray
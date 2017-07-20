#!/usr/bin/python
#-*- coding:utf-8 -*-

import re,sys,json,codecs,time,os, platform, traceback
import urllib2
import lxml.html
from AllClass import *
from commonFun import *

DAY_SECONDS = 86400


def zhidaoFun(initVarList):
    #问题id数组，存放所有已经遍历的问题的ID
    qidArray            = initVarList[0]
    #每个页面的动态更新属性作为字典存储到数组，与上面的问题id数组一一对应
    qDictArray          = initVarList[1]
    # 动态加载搜索的关键字和别名
    keyWord             = getKeyWordandAliasDict()[0]
    uname_dict          = getKeyWordandAliasDict()[1]
    is_first_run        = False
    m_time1             = os.path.getmtime('AllClass.py')
    m_time2             = os.path.getmtime('commonFun.py')
    if len(initVarList) == 3:
        conn = initVarList[2]
    elif len(initVarList) == 4:
        key = initVarList[2]
        next_page = initVarList[3]
        is_first_run = True
        index = keyWord.index(key)
        tmpKeyWord = []
        for i in range(index, len(keyWord)):
            tmpKeyWord.append(keyWord[i])
        print "next_page get from file is: \n %s\n" % next_page
    obj                 = BaiduZhidao()
    
    # keyWord             = ['安徽工业大学怎么样']
    #睡眠系数，控制程序睡眠的时长
    sleepRatio          = 1
    #外循环搜索计数器，以每次执行完整的搜索直到程序睡眠为一次
    runCount = 0

    try:
        f = open('runCount.txt', 'r')
        runCount = f.readline()
        if  len(runCount) != 0:
            runCount = int(runCount.strip('\n'))
        else:
            runCount = 1
        f.close()

        visitedPageCounts = 0 
        f = open('visitedPageCount.txt', 'r')
        visitedPageCounts = f.readline()
        if len(visitedPageCounts) !=0:
            visitedPageCounts = int(visitedPageCounts.strip('\n'))
        else:
            visitedPageCounts = len(qidArray)
        f.close()
    except Exception, e:
        raise e

    #无限循环，一直从网络抓取数据
    while True:
        if m_time1 != os.path.getmtime('AllClass.py'):
            reload(AllClass)
            from AllClass import *
            m_time1 = os.path.getmtime('AllClass.py')
        if m_time2 != os.path.getmtime('commonFun.py'):
            reload(commonFun)
            m_time2 = os.path.getmtime('commonFun.py')
            from commonFun import *
        runCount += 1
        f = open('runCount.txt','w')
        f.write(str(runCount))
        f.close()
        # print "external while"
        startTime      = time.time()
        addedPageCount = 0
        updateCount    = 0
        # externalCount  = externalCount + 1
        #用来判断每次查询时是否有更新或者增加了信息
        UPDATE_OR_ADD = 0
        
        if is_first_run:
            keyList = tmpKeyWord
        else:
            keyList = keyWord
        #遍历关键字
        for key in keyList:
            uname_abbr = uname_dict[key]
            try:            
                # print "current keyWord is: ", key                
                obj.setSearchKeyWord(key)
                if is_first_run:
                    obj.SearchREQ = next_page
                #获取下一页链接及当前页链接数组
                next_page, urlArray = obj.getPageLink(obj.SearchREQ, runCount, key)
                # print next_page, len(urlArray)
                #遍历所有搜索结果页面并解析每个详细页面，解析的内容在类的成员里面
                # pageCount = 0
                while next_page:
                    # pageCount += 1
                    #遍历当前页面
                    for url in urlArray:
                        visitedPageCounts += 1
                        # print "current url is: ", url
                        #本次查询返回的当前页面属性字典
                        qCurAttrDict = obj.parsePage(url, runCount, key)
                        print "script has visited %d pages\n" % visitedPageCounts
                        if not len(qCurAttrDict):
                            continue
                        #假如该页面已经访问过，判断是否有更新
                        if qCurAttrDict['qid'] in qidArray:
                            #根据ID所在的位置确定该ID对应的字典的索引
                            dictIndex = qidArray.index(qCurAttrDict['qid'])
                            qOldAttrDict = qDictArray[dictIndex]
                            #比较两个字典，如果没有更新，则跳过，如果两个字典相同，cmp返回值为0，否则为-1
                            if not cmp(qOldAttrDict, qCurAttrDict):
                                #没有更新，则结束本次循环
                                obj = resetMemVar(obj)
                                # print 'After reset len of obj.othAnsArray: %d\n'%len(obj.othAnsArray)
                                continue
                            elif qCurAttrDict['qid'] == qOldAttrDict['qid']:
                                updateCount  = updateCount+1
                                #处理新的评论
                                if qOldAttrDict['othAnsCount'] < qCurAttrDict['othAnsCount']:
                                    #先增加新的评论到数组和数据库
                                    for i in range(qOldAttrDict['othAnsCount'], qCurAttrDict['othAnsCount']):
                                        qDictArray[dictIndex]['othAnsArray'].append(qCurAttrDict['othAnsArray'][i])
                                    updateDB(obj, 'add_oths', qOldAttrDict['othAnsCount'], qCurAttrDict['othAnsCount'])
                                    qDictArray[dictIndex]['othAnsCount'] = qCurAttrDict['othAnsCount']
                                #检查已有信息是否有更新
                                ###############################
                                if qOldAttrDict['othAnsCount'] > qCurAttrDict['othAnsCount']:
                                    continue
                                ###############################
                                for i in range(qOldAttrDict['othAnsCount']):
                                    # print len(qOldAttrDict['othAnsArray']), len(qCurAttrDict['othAnsArray'])
                                    if not cmp(qOldAttrDict['othAnsArray'][i], qCurAttrDict['othAnsArray'][i]):
                                        continue
                                    else:
                                        #比较的数据是不是指向同一条
                                        if not cmp(qOldAttrDict['othAnsArray'][i]['othNo'], qCurAttrDict['othAnsArray'][i]['othNo']):
                                            if cmp(qOldAttrDict['othAnsArray'][i]['othGood'], qCurAttrDict['othAnsArray'][i]['othGood']):
                                                updateDB(obj, 'update_oths', i, 'othGood')
                                            if cmp(qOldAttrDict['othAnsArray'][i]['othBad'], qCurAttrDict['othAnsArray'][i]['othBad']):
                                                updateDB(obj, 'update_oths', i, 'othBad')
                                        else:
                                            #序号不一致不予更新
                                            pass
                                if cmp(qOldAttrDict['good'], qCurAttrDict['good']):
                                    #对采纳的回答的更新
                                    updateDB(obj, 'update_master', 'good')
                                if cmp(qOldAttrDict['bad'], qCurAttrDict['bad']):
                                    #对采纳的回答的更新
                                    updateDB(obj, 'update_master', 'bad')
                                obj = resetMemVar(obj)
                        else:
                            addedPageCount += 1
                            if runCount == 1 and len(initVarList) == 3:
                                updateDB(obj, 'add_page', conn, key, uname_abbr)
                            else:
                                updateDB(obj, 'add_page', key, uname_abbr)
                            # print "\n\nbefore append: \n","qidArray length:", len(qidArray),"\n qDictArray length:",len(qDictArray)
                            qidArray.append(qCurAttrDict['qid'])
                            qDictArray.append(qCurAttrDict)
                            # obj.othAnsArray = []
                            obj = resetMemVar(obj)
                            # print 'After reset len of obj.othAnsArray: %d\n'%len(obj.othAnsArray)
                            # print "\nafter append: \n","qidArray length:", len(qidArray),"\n qDictArray length:",len(qDictArray)
                        #每个URL解析完成后程序睡眠10s，百度防爬虫
                        time.sleep(10)
                    next_page, urlArray = obj.getPageLink(next_page, runCount, key)
                    f = open('InterruptStatus.txt', 'w')
                    f.write(key+'\n'+next_page)
                    f.close()
            except KeyboardInterrupt:
                endTime = time.time()
                print traceback.format_exc()
                f = open('InterruptStatus.txt', 'w')
                f.write(key+'\n'+next_page)
                f.close()
                recordRunStatus(runCount, startTime, endTime, addedPageCount, updateCount, len(qidArray), visitedPageCounts)
                sys.exit(0)
            # time.sleep(600)
        obj     = resetMemVar(obj)
        is_first_run = False
        endTime = time.time()
        
        #遍历一遍后，关闭数据库连接，程序开始睡眠
        if runCount == 1 and len(initVarList) == 3:
            conn.close()
        if (addedPageCount+updateCount) > 0 :
            #有更新，睡眠时间以原睡眠时间的1/2速率递减
            sleepRatio = int((sleepRatio+1)/2)
        else:
            #没有更新，睡眠时间就在原有基础上加一天
            sleepRatio += 1
        sleep_seconds = sleepRatio*DAY_SECONDS
        # print("Program will sleep %d days ..." % sleepRatio)
        #把本次运行信息保存到文件
        recordRunStatus(runCount, startTime, endTime, addedPageCount, updateCount, len(qidArray), visitedPageCounts, sleep_seconds)
        # exit()
        f = open('update.log','a')
        f.write('\n')
        f.close()
        print 'the program   end at: %s\n'  % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print 'program will sleep %d days\n\n' % int(sleep_seconds/86400)
        time.sleep(sleep_seconds)
        # time.sleep(60)

def init():
    #记录程序开始时间
    programStartTimeStruct = time.localtime()
    timeStr = time.strftime('%Y-%m-%d %H:%M:%S', programStartTimeStruct)
    f = open('runStatus.log','a')
    f.write( ('The program starts at: ' + timeStr + '\n\n').encode('utf-8') )
    f.close()
    
    if not os.path.exists('text'):
        os.system('mkdir text')

    if os.path.isfile('InterruptStatus.txt'):
        f         = open('InterruptStatus.txt','r')
        key       = f.readline().strip('\n')
        next_page = f.readline().strip('\n')
        f.close()

    #check if these files exist, if not, create them
    for fn in ['error.log', 'runStatus.log', 'db_opt.log', 'runCount.txt', 'InterruptStatus.txt', 'update.log', 'visitedPageCount.txt']:
        isFile(fn)

    #query the database to construct qidArray, qAttributeArray
    conn       = connDB()
    
    qidArray   = []
    qDictArray = []
    try:
        cur1 = conn.cursor()
        cur2 = conn.cursor()

        sql = 'select questionID, good, bad from bdzd_master'
        cur1.execute(sql)
        if cur1.rowcount > 0:           
            for row in cur1:
                othAnsArray                 = []
                qCurAttrDict                = {'qid':'', 'good':0,'bad':0,'othAnsCount':0,'othAnsArray':[]}
                qCurAttrDict['qid']         = row[0]
                qCurAttrDict['good']        = row[1]
                qCurAttrDict['bad']         = row[2]
                # qCurAttrDict['othAnsCount'] = row[3]

                othAttCmpDict = {'othNo':0,'othGood':0,'othBad':0}
                sql           = 'select othNo, othGood, othBad from bdzd_minor where questionID=%s' % row[0]
                cur2.execute(sql)
                if cur2.rowcount > 0:
                    for row2 in cur2:
                        othAttCmpDict['othNo']   = row2[0]
                        othAttCmpDict['othGood'] = row2[1]
                        othAttCmpDict['othBad']  = row2[2]
                        othAnsArray.append(othAttCmpDict)
                    qCurAttrDict['othAnsCount'] = cur2.rowcount
                    qCurAttrDict['othAnsArray'] = othAnsArray

                qidArray.append(row[0])
                qDictArray.append(qCurAttrDict)
            cur1.close()
            cur2.close()
            conn.close()
            #############################################
            print 'After init:\n len(qidArray):%d, len(qDictArray):%d\n'%(len(qidArray), len(qDictArray))
            if len(qidArray) != len(qDictArray):
                exit()
            #############################################
            if len(key) and len(next_page):
                return [qidArray, qDictArray, key, next_page]
            else:
                return [qidArray, qDictArray]
        else:
            return [qidArray, qDictArray, conn]
    except Exception, e:
        dbOptErrLog()
        print traceback.format_exc()
        exit()

if __name__ == '__main__':
    initVarList = init()
    zhidaoFun(initVarList)

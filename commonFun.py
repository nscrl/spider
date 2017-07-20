# -*- coding:utf-8 -*-
import traceback, time, cookielib, os, platform
import MySQLdb, urllib2

def getKeyWordandAliasDict():
    keyWord    = ['安徽工业大学','安工大','华东冶金学院','华冶','安徽大学','安大','安徽理工大学','安理工','安徽财经大学','安财','安财大','安农','安徽农业大学','安农大']
    uname_dict = {'安徽工业大学':'ahut','安工大':'ahut','华东冶金学院':'ahut','华冶':'ahut','安徽大学':'ahu','安大':'ahu','安徽理工大学':'aust','安理工':'aust','安徽财经大学':'aufe','安财':'aufe','安财大':'aufe','安农':'ahau','安徽农业大学':'ahau','安农大':'ahau'}
    return [keyWord, uname_dict]

def strcat(aList):
    result = ''
    for text in aList:
        if len(text) == 0:
            continue
        result = result + text
    result = result.replace("'", '+').replace('"', '+').replace(' ', '').replace('\r','').replace('\n','').replace('\\','')
    return result.encode('utf-8')

def testSinglePage(url, externalCount=None, key=None):
    obj = BaiduZhidao()
    obj.parsePage(url)

def setProxy(proxy):
    #set proxy, proxy is a dict with ip address and port : {ip:port}
    cookies       = urllib2.HTTPCookieProcessor()
    proxy_support = urllib2.ProxyHandler(proxy)
    openner       = urllib2.build_opener(cookies, proxy_support)
    urllib2.install_opener(openner)


def checkProxyAvaliable(proxy):
    timeout  = 10
    testUrl  = "http://www.baidu.com"
    test_str = "030173"
    setProxy(proxy) 
    req      = urllib2.urlopen(testUrl, timeout=timeout)
    # req = urllib2.urlopen(testUrl)
    result = req.read()
    if result.find(test_str) > -1:
        return True
    else:
        return False

def modelBrowser():
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)    
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)  
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [("Host","zhidao.baidu.com"),
        ('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'),
        ("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")] 

    return br

def isFile(filename):
    #假如错误日志文件不存在，则新建
    #使用platform模块判断系统是Linux还是Windows
    system = platform.system()
    if not os.path.isfile(filename):
        if "Linux" == system:
            os.system('touch %s' % filename)
        elif "Windows" == system:
            os.system('echo '' > %s' % filename)
        else:
            print "Maybe you use an apple machine ......"
            exit()

def dbOptErrLog(sql=None, *args):
    curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    f       = open('db_opt.log','a')
    err     = traceback.format_exc()
    f.write( ('Error occurs time: '+curTime + '\n').encode('utf-8') )
    if sql!=None:
        f.write('current sql is:'+sql+'\n')
    f.write(err.encode('utf-8'))
    if len(args) == 0:
        f.write('program will stop immediately ...\n\n')
    f.close()


def connDB():
    try:
        conn    = MySQLdb.connect('localhost','spider','spider','spiderDB', charset='utf8')
        return conn
    except Exception, e:
        dbOptErrLog()

def insert(obj, conn, *args):
    cur = conn.cursor()
    sql = "insert into bdzd_master(questionID, askTitle, qContent, askDate, answer," + \
        "answerDate, good, bad, adoptRate, answerType, crawlDate, cur_key, cur_alias) values"+\
        "('%s', '%s', '%s', '%s', '%s', '%s', %d, %d, '%s', '%s', now(), '%s', '%s')" % \
        (obj.question_id, obj.ask_title, obj.qContent, obj.ask_time, obj.answer, \
        obj.answer_time, obj.good, obj.bad, obj.adopt_rate, obj.answerType, args[0], args[1])
    try:
        cur.execute(sql)

        for dic in obj.othAnsArray:
            sql = "insert into bdzd_minor(questionID, othNo, answer, othGood, othBad, answerDate)"+\
                "values('%s', %d, '%s', %d, %d, '%s')" % (obj.question_id, dic['othNo'], \
                dic['answer'], dic['othGood'], dic['othBad'], dic['time'])
            cur.execute(sql)

    except MySQLdb.Warning, w:
        dbOptErrLog(sql, 'warning')
    except Exception, e:
        dbOptErrLog(sql)
    conn.commit()
    cur.close()

#更新到数据库
def updateDB(obj, flag, *args):
    #增加页面
    if not cmp(flag, 'add_page'):
        if len(args)  == 3 :
            conn = args[0]
            insert(obj, conn, args[1], args[2])
            return conn
        else:
            conn = connDB()
            insert(obj, conn, args[0], args[1])
            conn.close()
    elif not cmp(flag, 'add_oths'):
        if len(args) == 2:
            conn     = connDB()
            cur      = conn.cursor()
            #增加的条数
            oldCount = args[0]
            curCount = args[1]
            for i in range(oldCount, curCount):
                sql = "insert into bdzd_minor(questionID, othNo, answer, othGood, othBad, answerDate) values"+\
                    "('%s', %d, '%s', %d, %d, '%s')" % (obj.question_id, obj.othAnsArray[i]['othNo'], \
                    obj.othAnsArray[i]['answer'], obj.othAnsArray[i]['othGood'], obj.othAnsArray[i]['othBad'], obj.othAnsArray[i]['time'])
                try:
                    cur.execute(sql)
                    conn.commit()
                except Exception, e:
                    dbOptErrLog(sql)
                    cur.close()
                    conn.close()
                    exit()
            conn.commit()
            cur.close()
            conn.close()      
    elif not cmp(flag, 'update_master'):
        key  = args[0]
        conn = connDB()
        cur  = conn.cursor()
        if key == 'good':
            sql = "update bdzd_master set %s = %d, updateDate = now() where questionID='%s'" % (key, obj.good, obj.question_id)
        else:
            sql = "update bdzd_master set %s = %d, updateDate = now() where questionID='%s'" % (key, obj.bad, obj.question_id)
        try:
            cur.execute(sql)
            conn.commit()
        except Exception, e:
            dbOptErrLog(sql)
            cur.close()
            conn.close()
            exit()
        conn.commit()
        cur.close()
        conn.close()
    elif not cmp(flag, 'update_oths'):
        #update others
        if len(args):
            conn  = connDB()
            cur   = conn.cursor()
            no    = args[0]
            field = args[1]
            sql   = "update bdzd_minor set %s = %d where questionID='%s' and othNo = %d" % (field, obj.othAnsArray[no][field], obj.question_id, no)
            try:
                cur.execute(sql)
                conn.commit()
            except Exception, e:
                dbOptErrLog(sql)
                cur.close()
                conn.close()
                exit()
            conn.commit()
            cur.close()
            conn.close()

def resetMemVar(obj):
    obj.question_id = ''
    obj.ask_title   = ''
    obj.qContent    = ''
    obj.ask_time    = ''
    obj.answer      = ''
    obj.good        = 0
    obj.bad         = 0
    obj.adopt_rate  = ''
    obj.answerType  = ''
    obj.answer_time = ''
    obj.othAnsCount = 0
    obj.othAnsArray = []
    return obj

def writeErrorToFile(externalCount, currentKeyWord, url, *args):
    logList   = []
    timeTuple = time.localtime()
    curTime   = time.strftime('%Y-%m-%d %H:%M:%S',timeTuple)
    
    errList   = traceback.format_exc().split('\n')
    err       = errList[1].lstrip('') + ':' + errList[2] + '\n'+errList[3] + '\n'

    logList.append(str(externalCount)+' times perform the search mission ...\n')
    logList.append('Error occurs time: '+ curTime +'\n')
    logList.append('Current search keyword is: ' + currentKeyWord +'\n')
    logList.append('Current url is:'+url +'\n')
    logList.append('The error detail is:\n'+err +'\n')
    if len(args) == 1:
        offlinetime = args[0]
        logList.append('offline time has continued about %s seconds\n' % str(curTime- offlinetime))
    logList.append('\n')


    f = open('error.log', 'a')
    for line in logList:
        f.write(line)
    f.close()

def recordRunStatus(taskCount, startTime, endTime, addedPageCount, updatePageCount, urlCounts, visitedPageCounts, sleepSeconds=None):
    recordList     = []
    startTimeStr   = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
    endTimeStr     = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endTime))
    runTimeSeconds = int(endTime - startTime)
    days           = int(runTimeSeconds/86400)
    hours          = int( (runTimeSeconds%86400)/3600 )
    minutes        = int( ((runTimeSeconds%86400)%3600)/60 )
    seconds        = int( (((runTimeSeconds%86400)%3600)%60) )
   
    recordList.append(str(taskCount)+' times carry out the search mission ...\n')
    recordList.append('the program begin at: ' + startTimeStr +'\n')
    recordList.append('the program   end at: ' + endTimeStr + '\n')
    recordList.append('program has run %d seconds: %d days %d hours %d mins %d seconds\n' % (runTimeSeconds, days, hours, minutes, seconds) )
    recordList.append('addedPageCount: '+str(addedPageCount) +'\n')
    recordList.append('updatePageCount: '+str(updatePageCount)+'\n')
    recordList.append('the program has saved %d pages\n' % urlCounts)
    if sleepSeconds:
        recordList.append('program will sleep %d days\n\n' % int(sleepSeconds/86400))

    f = open('runStatus.log', 'a')
    for line in recordList:
        f.write(line.encode('utf-8'))
    f.close()

    f = open('visitedPageCount.txt', 'w')
    f.write(str(visitedPageCounts))
    f.close()

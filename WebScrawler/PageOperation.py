import htmllib, urllib,urllib2, zlib, time, formatter, os, urlparse, httplib
import StringIO
from HTMLParser import HTMLParser
import socket
import threadpool, threading
urllib2.socket.setdefaulttimeout(30)
#import timeoutsocket 
#timeoutsocket.setDefaultSocketTimeout(120)
mutexUrl = threading.Lock()

#HTMLParser overwrite to read tag <a>, <base> and the content of page
class MyHTMLParser(HTMLParser):
    def __init__(self) :        # class constructor  
        self.__links = []        # create an empty list for storing hyperlinks
        self.reset()
        self.fed = []
        self.__base = ''
        self.__total =0
        
    def setTotal(self,total):
        self.reset()        
        self.__total = total
        self.fed = []
        self.__base = ''
        self.__links = []        # create an empty list for storing hyperlinks

    #get the content of <a> and <base> tag
    def handle_starttag(self, tag, attrs):
        try:
            if self.__base == '':
                if tag == 'base':
                      if len(attrs) > 0 :
                         for attr in attrs:
                            if attr[0] == "href":
                                self.__base = attr[1]
            if self.__total > -1:
                if tag == 'a':
                      if len(attrs) > 0 :
                         for attr in attrs:
                            if attr[0] == "href":
                                hrefStr = attr[1]
                                self.__links.append(hrefStr)
                                self.__total = self.__total - 1
        except Exception, e:
            print "My HTML Parse error: " + e.message

    def GetBase(self):
        return self.__base

    def get_links(self):
      return self.__links
    #get the content of current page
    def handle_data(self, d):
        try:
            self.fed.append(d)
        except Exception,e:
            print "handle_data " + e.message
            


    def get_data(self):
        desUrl = ''
        for i in self.fed:
            desUrl = desUrl + i + ' '
        return desUrl
    
# page related operation
class PageOperation:
    def __init__(self, queryList):
        self.__urlOpener = urllib.URLopener()	# create URLopener
        self.__fullUrl = {}
        self.__basePath = ""
        self.__queryList = queryList
        self.__dic = ['html', 'aspx' , '', 'shtml', 'htm', 'asp', 'htx', 'htmls']
        self.__curProirity = 0
        self.__htmlparser = MyHTMLParser()        # create new parser object\
        
    #download requested page
    def DownloadPage(self, urlStr):
        global mutexUrl
        self.__urlStr = urlStr     
        beginT = time.time()
        
        #time.sleep(3)  
        #response = urllib.urlopen(url)    
       
        outputStr = ""
        #print '\n' + urlStr + '\n'
        response = urllib2.urlopen(urlStr)
         
        endT = time.time()
        self.__PageContent = response.read()   # open file by url
        durT = endT - beginT      
        size = self.__PageContent.__sizeof__()            
        outputStr = (',download time: %.2f, pageSize: %s, return code: %s') % (durT, size, response.code)
        response.close()

        return outputStr
    #compress page content
    def CompressPage(self):
        relStr = zlib.compress(self.__PageContent, zlib.Z_BEST_COMPRESSION)
        return relStr
    #parse page and get urlList in the page content
    #deal with Ambigious url to get full url
    def GetInnerUrl(self, total):     
        #parse content
        self.__fullUrl.clear()
        self.__curProirity = 0
        relatedFlag = 10
        self.__htmlparser.setTotal(total)
        self.__fullUrl = {}
        try:
            self.__htmlparser.feed(self.__PageContent)      # parse the file saving the info about links
        except Exception, e:
            print e.message 
        else:
            urlList = self.__htmlparser.get_links()   # get the hyperlinks list
            basePath = self.__htmlparser.GetBase()        
            (relatedFlag, self.__curProirity) = self.__GetRelatedFlag(self.__htmlparser.get_data())
            
            if basePath == "" :
                url = urlparse.urlparse(self.__urlStr)  
                basePath = url.scheme + '://'+ url.netloc + '/'
            self.__basePath =  basePath
            
            self.__getFullUrl(urlList)
            return (self.__fullUrl, self.__curProirity, relatedFlag)
        (relatedFlag, self.__curProirity) = self.__GetRelatedFlag(self.__PageContent)
        return (None, self.__curProirity, relatedFlag)
    #deal with the Ambigious Url by multithread

    #check the UrlList    
    def __getFullUrl(self, urlList ):
        for urlstr in urlList:
            if urlstr.count('..') != 0:
                continue
            
            url = urlparse.urlparse(urlstr)

            desStr = ""
            if url.netloc == "" :
                if self.__basePath != "":
                    desStr = urlparse.urljoin(self.__basePath, url.path)
                    #desStr = self.__basePath +  url.path
                else:
                    continue
            else:
                desStr = urlstr
      
            #check file type
            if desStr != "":
                #get file type 
                curType = url.path
                dic = curType.split('/')
                curType = dic[len(dic) -1]
                dic = curType.split('?')
                curType = dic[0]
                curType = curType.lower()

     
                # check the suffix
                urlDic = curType.split('.')
                lenDic = len(urlDic)
                fileType = urlDic[lenDic-1]
                # invalid suffix
                if self.__dic.count(fileType) == 0:
                    continue
                else:
                    # ignore the duplication 
                    if curType == 'index.htm' or curType == 'index.html' or curType == 'index.jsp' or curType == 'main.html':
                        desStr = desStr[0:desStr.find(curType)]
            if desStr != "":
                try:
                    ipDre = socket.gethostbyname(url.netloc)
                    if ipDre != '0.0.0.0':
                        desStr = desStr.replace(url.netloc, ipDre)
                except Exception, e:
                    pass
                self.__fullUrl[desStr] = self.__curProirity
           
    #Get Priority and catagory of CurPage
    #catagory 0: full related
    #catagory 1: part related
    def __GetRelatedFlag(self, dataStr):
        try:
            total = 0;        
            flag = len(self.__queryList)
            IncreaseP = True
            if flag == 1:
                IncreaseP = False
            for i in self.__queryList:
                temp = dataStr.count(i)
                if temp > 0:
                    flag = flag - 1
                    total = total + temp

            if flag == 0:
                if len(self.__queryList) > 1 and IncreaseP:
                    return (0, total)
                else:
                    return (0, total)
            elif flag != len(self.__queryList):
                return (1, total)
            return (2, total)
        except Exception, e:
            print "Get Priority and catagory of CurPage error: " + e.message
            
#save data to hard drive
class PageSave(object):

    """description of class"""
    def __init__(self):
        
        self.__dataList = []
        self.__folderPath = os.getcwd() + '\YaoChen'
        if not os.path.exists(self.__folderPath):
            os.mkdir('YaoChen')
        self.__log = []
        file = open(os.path.join(self.__folderPath, 'log.txt'), 'wb')
        file.close()
    #add the downloaded page     
    def Add(self, data):
        if len(data) != 0:
            self.__dataList.append(data)
    #add the information of downloaded page
    def AddLog(self, log):
        self.__log.append(log)
    #save the log file
    def SaveLog(self, log):
        file = open(os.path.join(self.__folderPath, 'log.txt'), 'a+')
        file.write(log)
        file.close()
    def __Clear(self):
        self.__dataList = []
        self.__log = []
        self.__error = 0
        return 0
    #save the data file and log file
    def SaveFile(self, beginT, DownError):
        fileName = time.strftime('%d-%H-%M-%S.txt',time.localtime(time.time()))
        filePath = os.path.join(self.__folderPath, fileName)
        EndT = time.time()
        dur = beginT - EndT 
        strW = "Contain 200 files" + "The size of file %d "% self.__dataList.__sizeof__() +" The total time used: %.2f "% dur +  "The error times : %d \n"% DownError   
        file = open(filePath, 'wb')
  
        file.write(strW)
        if len(self.__dataList) == 0:
            return
        for i in self.__dataList:
            file.write(i + '\n') 
        file.close()
        file = open(os.path.join(self.__folderPath, 'log.txt'), 'a+')
        for i in self.__log:
            file.write(i)
        file.close()
        self.__Clear()
    # get the folder size
    def GetWholeSize(self):
        nTotalSize = 0
        for  strRoot, lsDir, lsFiles in os.walk(self.__folderPath):
            for strFile in lsFiles:
                nTotalSize = nTotalSize + os.path.getsize(os.path.join(self.__folderPath, strFile));
        return nTotalSize

import urlparse, robotparser
import heapq, sys
import httplib
import socket
socket.setdefaulttimeout(30)

#store page url and priority
class PageQueue:
    """description of class"""
    def __init__(self, total):
        self.__Queue = []
        self.__total = total
        self.__minPriority = sys.maxint
        self.__DownloadDic = {}
    #add the url list to queue   

    def Modify(self, newPDic):
        
        #update the old page with high prority
        dicL = len(newPDic)
        
        #insert new page:
        while dicL != 0:
            (url,priority) = newPDic.popitem()
            dicL = dicL - 1
            if not self.__DownloadDic.has_key(url):
                heapq.heappush(self.__Queue, (-priority, url))
        #Maitain  the length of queue list  as the total of required page
        #Limiting the length of queue can reduce the time to deal with queue structure
        #To remove the last part of the queue can also maintain the url with maximum proirity
        lenQ = len(self.__Queue)
        if lenQ > self.__total:            
            self.__Queue = self.__Queue[0:self.__total]
          
                              
        # the url with max priority         
    def GetMax(self):
        curUrl = ''
        while curUrl == ''and len(self.__Queue) > 0:
            (i,curUrl) = heapq.heappop(self.__Queue)
            if self.__RobotCheck(curUrl) and not self.__DownloadDic.has_key(curUrl):
                self.__DownloadDic[curUrl] = -i
                return curUrl
    
    def GetPriority(self,url):
        return self.__DownloadDic[url]
        #check the robot.txt file
    def __RobotCheck(self, url):
        try:
            urlS = urlparse.urlparse(url)  
            urlMain = urlS.scheme + '//'+ urlS.netloc + '/'
            urlStr = urlparse.urljoin( urlMain,'robots.txt')
            self.__RobotParser.set_url(urlStr)
            self.__RobotParser.read()
            if self.__RobotParser.errcode == 200:
                if self.__RobotParser.can_fetch(url):
                    return True
            return False        
        except Exception, e:
            return True

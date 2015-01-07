import urllib
import simplejson
class GoogleSearch(object):
    
    """description of class"""
    def __init__(self):
        self.__resultAccount = 10
        self.__googleAccount = 'https://www.googleapis.com/customsearch/v1?' + 'key=AIzaSyD4LJqWeAbn5DJBYTp92VRCW-Pweci_xRw' + '&cx=006477744714351800842:mb_g5cf-e80&alt=json'

    def GetResult(self,quiryList):
        quiryStr = ""
        for i in quiryList:
            quiryStr = quiryStr + i + " "
        urlStr = ('&q=%s&num=%s')%(urllib.quote(quiryStr), self.__resultAccount)
        urlStr = self.__googleAccount + urlStr

        response = urllib.urlopen(urlStr)
        # Process the JSON string.
        results = simplejson.load(response)
                            
        info = results['items'] 
        resList = []           
        for minfo in info:
            resList.append(minfo['link']) 
        return resList

# output and input related function
class FrontEnd(object):
    """description of class"""
    def __init__(self):
        self.__totalAmount = 0
    def GetQuiryInfo(self):
        quiryStr = raw_input('Please input a set of query words:\n')
        while quiryStr == '':
            quiryStr = raw_input('The query work is empty, please input them again:\n')
        quiryList = quiryStr.split(' ')

        while self.__totalAmount < 1:
            totalStr = raw_input('Please input the total account of pages to download. The number should be larger than 0:\n')
            while totalStr.isdigit() == False:
                totalStr = raw_input('You should input a number, please input it again:\n')
            self.__totalAmount = int(totalStr)        
        totalAccount = self.__totalAmount
        return (quiryList, totalAccount)

    def PrintUrlPriority(self, urlStr, priority):
        print "The url is: " + urlStr
        print "The priority is: %d" % priority

 

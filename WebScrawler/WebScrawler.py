import threadpool, threading
import time, sys
import DataStructure,PageOperation, AidOperation

class WebScrawler:
    def __init__(self, queryList, total):
        self.__queryList = queryList
        self.__downloadList = []
        self.__download = []
        
        
        #self.__FilePath = os.getcwd()
         
        
        self.__mutexSave = threading.Lock()
        self.__mutexCount = threading.Lock()
        self.__mutexQueue = threading.Lock()
        self.__selfError = 0
        self.__count = 0
        self.__total = total
        self.__allInclude = 0
        self.__partInclude = 0
        self.__begin = 0.0
        
        self.__pageQ = DataStructure.PageQueue(total)
        
        self.__PageSave = PageOperation.PageSave()
        #self.__PageDic = DataStructure.PageDic()
        outputStr = "The query string is:"
        for i in queryList:
            outputStr  = outputStr + i + ' '
        outputStr = outputStr + '\n The total page is: %d'%total + '\n'
        self.__PageSave.AddLog(outputStr)
    # the main process of crawler
    def ScrawlAll(self):
        try:#get source page from google search engine
            self._GetSource_()
        except Exception, e :
            print "googleSource Failure " + e.message
        else:#use multithread to deal with web page
            self.ScrawlThread()
            if self.__count >= self.__total:#finished scrawler, save file
                self.__finalLog()
                self.__PageSave.SaveFile(self.__begin, self.__selfError)
            else:
                print "Scrawler failed! \n"
            
    def _GetSource_(self):
            googleRes = AidOperation.GoogleSearch()
            urlListOrg = googleRes.GetResult(self.__queryList)
            
            #urlListOrg = [u'http://www.klinzmann.name/licensecrawler.htm', u'http://download.cnet.com/License-Crawler/3000-2094_4-75322092.html', u'http://www.taiwantrade.com.tw/EP/amres/products-detail/en_US/559875/OX-EYED_BUILDING_BLOCK_--_SCRAWLER/', u'http://www.academia.edu/643755/A_Novel_Architecture_for_Domain_Specific_Parallel_Crawler', u'http://www.technibble.com/license-crawler-find-product-keys-in-the-registry/', u'http://screensavers.funutilities.com/ssavers/010808/Crawler.html', u'http://www.linotype.com/511960/ScrawlerRegular-product.html', u'http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.29.9279&rep=rep1&type=pdf', u'http://www.linotype.com/432483/CCWallScrawlerItalic-product.html', u'http://dblab.soongsil.ac.kr/publication/LeLe07.pdf']
            #urlListOrg =[u'http://www.youtube.com/watch?v=D85yrIgA4Nk', u'http://www.dogcatbird.net/', u'http://www.youtube.com/watch?v=GbycvPwr1Wg', u'http://en.wikipedia.org/wiki/Dog%E2%80%93cat_relationship', u'http://www.youtube.com/watch?v=TLa1jmD0S18', u'http://www.dogdogcat.com/', u'http://www.animalplanet.com/tv-shows/bad-dog/videos/the-cat-who-bitch-slaps-gators.htm', u'https://www.lostdogrescue.org/', u'http://www.dogcatradio.com/', u'http://www.wimp.com/dogcat/']
            
            urlDic = {}
            for i in urlListOrg:
                urlDic[i] = sys.maxint          
            self.__pageQ.Modify(urlDic)
            
    def ScrawlThread(self):
        self.__begin = time.time()
        thread_list = list();
        strTemp = ''
        for i in range(0, 10):
            thread_name = "thread_%s" %i
            thread_list.append(threading.Thread(target = self.__Scrawl, name = thread_name))
     
        
        for thread in thread_list:
            thread.start()
     
        
        for thread in thread_list:
            thread.join()
        return

    #each thread to deal with one url        
    def __Scrawl(self):
        urlStr = ''
        while self.__count < self.__total:
            #print 'self.__cout: ' + str(self.__count) + 'self.__total: ' + str(self.__total) + '\n'
            begin1 =time.time()
            if self.__count > 0 and self.__count % 200 == 0 :
                self.__PageSave.SaveFile(self.__begin, self.__selfError)
                self.__begin = time.time()
                
            if self.__mutexQueue.acquire(1):
                urlStr = self.__pageQ.GetMax()
                self.__mutexQueue.release()
                
            if urlStr == '' or urlStr == None:
                continue
            pageOp= PageOperation.PageOperation(self.__queryList)
                    # save file when we get 100 files

                
            downloadError = False
            output = ''
            DicError = False
            queryWordCount = ''
            maxPage = []
            #download page
            try:                       
                curPageInfo = pageOp.DownloadPage(urlStr)
                #print curPageInfo + '\n'
                #download page error
            except Exception, e:
                downloadError = True
                
            
   
            if downloadError:
                self.__selfError = self.__selfError + downloadError         
                #print "DownLoad E\n"
            else:
                if self.__mutexCount.acquire(1):
                    self.__count = self.__count + 1
                    output = str(self.__count) + ': '
                    self.__mutexCount.release()
                    
                if self.__count <= self.__total:     
                    #compress page data and save to file
                    pageCompress = pageOp.CompressPage()
                    self.__PageSave.Add(pageCompress)
                    
                    try:#parse the webpage and check the url validation
                        (urlDicOrg,curPriority, curRelatedFlag) = pageOp.GetInnerUrl((self.__total)*5)
                        
                    except Exception, e:
                        print "Parse File Failue " + e.message
                    else:
                        if urlDicOrg != None:
                            if curRelatedFlag == 0:
                                self.__allInclude = self.__allInclude + 1
                            elif curRelatedFlag == 1:
                                self.__partInclude = self.__partInclude + 1
                                
                            queryWordCount = "query words count: " + str(curPriority) + ' '

                            
                            if not DicError:
                                if self.__mutexQueue.acquire(1):
                                    try:#insert the url into queue
                                        self.__pageQ.Modify(urlDicOrg)
                                    except Exception, e:
                                        print "Queue update Failure: " + e.message                          
                                    self.__mutexQueue.release()
                    # print the current page information and add it into log file               
                    output = output + ' Priority: ' + str(self.__pageQ.GetPriority(urlStr)) + ' ' + queryWordCount + curPageInfo + "\n Url:" + urlStr + '\n'
                    self.__PageSave.AddLog(output)
                    print output
          
                end1 = time.time()
    # print the analysis result of the scralwer            
    def __finalLog(self):
        outputStr = ""
        temp = self.__allInclude * 1.0/self.__total * 100 
        outputStr =  "The persentage of page containing all search words: %.2f" % temp + '%' + '\n'
        temp = self.__partInclude * 1.0/self.__total * 100 * 1.0
        outputStr = outputStr + "The persentage of page containing part search words: %.2f" % temp  + '%' + '\n'
        temp = (self.__total - self.__partInclude - self.__allInclude) * 1.0 /self.__total * 100 * 1.0  
        outputStr = outputStr +  "The persentage of page containing no search words: %.2f" % temp  + '%' + '\n'       
        print outputStr
        self.__PageSave.AddLog(outputStr)
        
    #print the folder size and time was used    
    def PrintFinal(self, usedTime):
        outputStr = "The size of download pages: %d Byte \n" % (self.__PageSave.GetWholeSize())
        outputStr = outputStr + "The time used: %.2f \n" % (usedTime)
        print outputStr
        self.__PageSave.SaveLog(outputStr)
        
Printer = AidOperation.FrontEnd()    
(queryList, total) = Printer.GetQuiryInfo()
begin = time.time()
scrawler = WebScrawler(queryList, total)
#scrawler = WebScrawler("dog cat", total)
scrawler.ScrawlAll()
end = time.time()
scrawler.PrintFinal(end - begin)

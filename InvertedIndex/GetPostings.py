__author__ = 'minzhu'


import gzip
import os
import ctypes

import threading
lock = threading.RLock()

dataIndex = 0
docId = 0

class PostingOneDataFile():
    def __init__(self, index, dataPath, indexPath):
        self.index = index
        self.dataPath = dataPath
        self.indexPath = indexPath
        self.postingFile = '%s/posting/posting_%d.txt' % (os.getcwd(),self.index)
        self.uncompressDataFile = '%s/data/%d_data_uncompress' % (os.getcwd(), self.index)

    def __initData__(self):
        '''
        uncompress a data file, write the uncompressed data into another file
        '''
        try:
            with gzip.open(self.dataPath, 'rb') as f_in1:
                data = f_in1.read()
                f_out1 = open(self.uncompressDataFile, 'wb')
                f_out1.write(data)
                f_out1.close()
                del data

                pfile = open(self.postingFile, 'wb')
                pfile.close()

        except ValueError as err:
            print("------read error:",err)

        except IOError as ioerr:
            print('------IO error:', ioerr)

    def uncompressAndParser(self):
        self.__initData__()

        global docId
        try:
            startpos = 0
            length = 0
            with gzip.open(self.indexPath, 'rb') as f_in2:
                f = open(self.uncompressDataFile, 'rb')

                #init thread_pool
                thread_pool = []
                '''parse each page'''
                for eachline in f_in2:
                    eachline = eachline.decode()
                    list = eachline.split(' ')
                    url = list[0]
                    length += int(list[3])
                    contentlen = int(list[3])

                    if contentlen == 0:
                        break

                    '''get every page's data according to startpos and contentlen'''
                    f.seek(startpos)
                    content = f.read(contentlen)
                    startpos += contentlen

                    self.__parseOnePage__(url, content, docId)
                    del content
                    docId += 1
                    '''# init thread items
                    th = threading.Thread(target=self.__parseOnePage__, args=(url,content,docId))
                    thread_pool.append(th)
                    docId += 1'''

                '''# start threads one by one
                threadNum = len(thread_pool)
                for i in range(threadNum):
                    thread_pool[i].start()

                #collect all threads
                for i in range(threadNum):
                    threading.Thread.join(thread_pool[i])'''

                f.close()
                os.remove(self.uncompressDataFile)

        except ValueError as err:
            print("------read error:",err)

        except IOError as ioerr:
            print('------IO error:', ioerr)

        #os.remove(self.uncompressDataFile)

    def __parseOnePage__(self, url, content, docId):
        '''get the response code and Content-Length from the header'''
        contentlist = content.split(b'\r\n')
        responseCode = int(contentlist[0].split(b' ')[1])
        del contentlist

        '''add a posting in the docID-URL table'''
        #lock.acquire()
        docIdURL = open('%s/docID-URL' % os.getcwd(), 'a')
        docIdURL.write('%s,%d,%d\n' % (url, docId, responseCode))
        docIdURL.close()
        #lock.release()

        '''start parsing'''
        #if realLen > 0 :
        pdll = ctypes.CDLL('%s/HTMLParser/myparser.so' % os.getcwd())
        pool = content + '1'
        parserlen = pdll.parser(url, content, pool, len(content)+1)

        wordlist = pool[0:parserlen].split('\n')
        del pool
        posting = '%d;' % docId
        for word in wordlist:
            if len(word) > 0 and word.split(' ')[0] != 'nbsp':
                wordstr = '%s,' % word.split(' ')[0]
                posting += wordstr
        del wordlist

        posting += '\n'

        #lock.acquire()
        postFile = open(self.postingFile, 'a')
        postFile.write(posting)
        postFile.close()

        del posting
        #lock.release()




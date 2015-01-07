__author__ = 'yaochen'
import os
import heapq
import threading
import tarfile
import time
from vbyte import vbyteCompress
from operator import itemgetter
class GetSourceIndex:
   
    def __init__(self, dicPath):
        self.__path = dicPath
        self.__curParseFile = 0
        count = 0
        # get the parsed file account
        for item in os.listdir(dicPath):
            abs_item=os.path.join(dicPath,item)
            if os.path.isfile(abs_item) and item.find('.txt') != -1:
                count = count + 1
        self.__totalParseFile = count

        self.__curResCount = 0
        #create new folder for the parsed Files

        self.__ParsedFolder = self.__path + "/parsedFiles"
        folderExists = os.path.exists(self.__path + "/parsedFiles")
        
        if not folderExists:
            os.makedirs(self.__ParsedFolder)
        print "Parse source file:"
    # parse all file
    def ParseAll(self):
            #open ( "D:\posting/posting_20.txt", 'r' )  
            while self.__curParseFile < self.__totalParseFile:
                filePath = self.__path + '/posting_' + str(self.__curParseFile) +'.txt'                
                desPath = self.__ParsedFolder+"/" + str(self.__curParseFile) + ".txt"
                print "parse file:" + str(self.__curParseFile) + '/' + str(self.__totalParseFile)
                # parse one file
                self.__ParseOne(filePath,desPath)
                self.__curParseFile = self.__curParseFile + 1     

                thread_list = []
                upperBound = self.__totalParseFile - self.__curParseFile
                if upperBound > 9:
                    upperBound = 10

                
    def __ParseOne(self,filePath,desFile):
        #get the source file


        fileHandle = open ( filePath )  
        fileList = fileHandle.readlines()
        fileHandle.close()

        parseLines = []
        wordHash = {}
        wordList = []
        #parse each line
        for line in fileList:
            self.__Parse(line,wordList)

        # sort all word in order
        wordList.sort(key=itemgetter(0,1))
        # save the result into hard drive
        self.__saveFile(desFile, wordList)


    def __saveFile(self,desFile, wordList):
        lenList = len(wordList)
        if(lenList == 0):
            return
        file = open(desFile, 'w')

        
        (preWord, preId) = wordList[0]
        count = 1;
        rel = []
        relStr = ""
        
        for i in range(1,lenList):  
            (word,wordId) = wordList[i]
            #rel.append(word+ str(wordId))
            
            if(word == preWord):#same word 
                if wordId == preId:#in same document
                    count = count + 1
                else:#in different document
                    relStr = relStr + str(preId) + '-' + str(count) +',' 
                    preId = wordId
                    count = 1;
            else:# different word in different document
                relStr = relStr + str(preId) + '-' + str(count) +','
                rel.append(preWord + ":"+ relStr + '\n')
                preWord = word
                preId = wordId
                relStr = ""
                count = 1
               
        (word, wordId) = wordList[lenList-1]
        rel.append(word + ":"+ relStr + str(wordId) + '-' + str(count) +','  + '\n')
        file.writelines(rel);       
        file.close()

    def __Parse(self,line,wordList):
        part = line.split(';')
        wordId = int(part[0])
        words = part[1].split(',')
        tempDic = {}
        for word in words:
            #if there is same word appeared in other doc
            word = word.replace('\n','')
            word = word.replace('\r','')
            word = word.replace('\t','')
            if word =='':
                continue
            wordList.append((word,wordId));


class merge():
    def __init__(self):
        self.__sizeHint = 1024*1024  # 1M
        self.__desFile = ""
    # use 10M to load the source file, use 10M to buffer the result. 
    # save the result file in folderPath+'\result'+ index.txt
    def __clear(self):
        self.__sourceBuffer = []
        self.__desBuffer= []
        self.__fileHandle = [] 
        self.time = 0.0
    #set the merge parameter
    def setPare(self, beginFile, count, folderPath, sourceFile, disFile):
        
        self.__desFolder = folderPath
        self.__count = count
        self.__sourceFile = sourceFile
        self.__finishFile = beginFile
        self.__end = self.__count + beginFile
        self.__desFile = disFile

        
    def mergeFile(self):
        self.__clear()   
        #open the source file and read part of the file             
        sourceFileCatch = self.__fileopenFile()

        self.temp = 0
        flag = False
        if self.__desFile == "":
            flag = True

        # sourceFileCatch is a list which contain 10 elements
        # each element is a list which store the lines from sourcfile.

        heapWord = []
        dicLis = ""
        #initial the merge heap
        i = 0
        for dicLis in self.__sourceBuffer:
            wordKey = dicLis[0].split(':')
            heapq.heappush(heapWord, (wordKey[0]+ str(i),wordKey[0]))
            i = i + 1
        preWord = ""


        flagSave = False
        while self.__finishFile < self.__end and len(heapWord) > 0:
            #get the minimum word in alphabitcal order
            (sourceW, key) = heapq.heappop(heapWord)
            index = int(sourceW[sourceW.find(key) + len(key): len(sourceW)])
           
            dicStr = self.__sourceBuffer[index].pop(0)                   
            wordKey = dicStr.split(':')
            wordList = wordKey[1].replace('\n','')
            #put the word into the result buffer

            if flag:
                if preWord == key:
                    lenBuf = len(self.__desBuffer)                
                    (key, wordList) = self.__desBuffer[lenBuf - 1]
                    self.__desBuffer[lenBuf - 1] = (key, wordList + ',' + wordKey[1])

                else:
                    if flagSave:
                        self.__saveFile()
                        flagSave = False
                    self.__desBuffer.append((key, wordList))
            else:
                if preWord == key:
                    lenBuf = len(self.__desBuffer)                
                    self.__desBuffer[lenBuf - 1] = self.__desBuffer[lenBuf - 1]  + ',' + wordList
                else:
                    if flagSave:
                        self.__saveFile()
                        flagSave = False
                    self.__desBuffer.append(key + ':' + wordList)

            preWord = key
            #get the new word
            (checkFlag, flagSave) = self.__checkBuffer(index)
            if checkFlag:
                dicLis = self.__sourceBuffer[index]
                wordKey = dicLis[0].split(':')
                heapq.heappush(heapWord, (wordKey[0]+ str(index),wordKey[0]))
        self.__saveFile()
    def __saveFile(self):
        if len(self.__desBuffer) != 0:     
                #send the result to the next phase "the compression phase"  in the last step
                #the last step is to get the final inverted index   
                if self.__desFile == "":
                    """
                    print "Merge file to get file: " + str(self.temp) + '\n'
                    file = open ( self.__desFolder + '/' + str(self.temp) + '.txt','w+' )
                    self.temp = self.temp + 1
                    file.write('\n'.join(self.__desBuffer) + '\n')
                    file.close()   
                    """
                    begin = time.time()
                    vbyteCompress(self.__desBuffer)
                    self.time = self.time + time.time() - begin
                # get the partial inverted index and save them into hard drive
                else:
                    file = open ( self.__desFile,'a+' )
                    file.write('\n'.join(self.__desBuffer) + '\n')
                    file.close()              
                 
              
                self.__desBuffer= []
    #check the source list, if the source list is empty, read the data from file 
    def __checkBuffer(self,index):
        if(len(self.__sourceBuffer[index]) == 0):

            temList = self.__fileHandle[index].readlines(self.__sizeHint)
            if len(temList) == 0:
                self.__fileHandle[index].close()
                self.__finishFile = self.__finishFile + 1
                return (False, True)

            else:
                self.__sourceBuffer[index] = temList
            return (True, True)    
        else:
            return (True, False)
    #open the source file, and load part data into memory(list)               
    def __fileopenFile(self):
        
        for i in range(self.__count):            
            self.__fileHandle.append(open(self.__sourceFile  + '/' + str(self.__finishFile + i) + '.txt', 'r'))
        tempDic = []
        tList = []
        for i in range(self.__count):
            tempDic = self.__fileHandle[i].readlines(self.__sizeHint)
            if len(tempDic) == 0:
                tList.append(i)
            else:
                self.__sourceBuffer.append(tempDic)
        for i in tList:
            self.__fileHandle.pop(i)
#get the final inverted index
class finalInvertedIndex():
    def __init__(self, dicPath,count):
        self.__Merge = merge()
        path = dicPath + "/FinalInvertedIndex"
        sourceFile = dicPath + "/InvertedIndex" + str(count)
        # get the account of file in the source folder
        folderExists = os.path.exists(path)
        if not folderExists:
            os.makedirs(path)
        print "Get Final Inverted Index:" + '\n'
        tarFolder = tarFile()
        #tarFolder.unTar(sourceFile)
        #merge source file
        self.__Merge.setPare(0, len(os.listdir(sourceFile)) ,path,sourceFile,"")
        self.__Merge.mergeFile();
        tarFolder.Tar(sourceFile)
        self.time = self.__Merge.time
        

# get partial inverted index
class interInvertedIndex():
    def __init__(self, dicPath):
        self.__Merge = merge()

        print "Inter Inverted Index" + '\n'

        count = 20
        folder = 0
        tarFolder = tarFile()
        sourceFile = dicPath + "/parsedFiles"
        while count > 10:
        # get the account of file in the source folder            
            path = dicPath + "/InvertedIndex" + str(folder)            
            folderExists = os.path.exists(path)
            if not folderExists:
                os.makedirs(path)
            #merge source file                            
            self.__invertPart(sourceFile,path,len(os.listdir(sourceFile)))
            folder = folder + 1
            count = len(os.listdir(path))
            #tarFolder.Tar(sourceFile)
            sourceFile = path         

        self.__folder = folder - 1

    def getCount(self):
        return self.__folder
    #merge source file
    def __invertPart(self, sourceFile, path, count):
        rangeCount = count/10 - 1
        #merge 10 file into one result file
        for i in range(rangeCount):
            print "Merge files:" + str(i*10) +"~" + str((i+1)*10) + '\n'
            disFile = path + '/' + str(i) + '.txt'
            self.__Merge.setPare(0 + i*10, 10,path,sourceFile,disFile)
            self.__Merge.mergeFile();
        if rangeCount < 0:
            rangeCount = 0
        # merge rest file 
        print "Merge rest files"  + '\n'
        disFile = path + '/' + str(rangeCount) + '.txt' 
        self.__Merge.setPare(rangeCount * 10, count - rangeCount * 10, path,sourceFile,disFile)
        self.__Merge.mergeFile();
#compress the intermedia data and uncompress them
class tarFile():
    def Tar(self, folder):        
        fileCount = 1
        tar = tarfile.open(folder + "/" + str(fileCount/10) + ".tar.gz","w:gz")
        for root,dir,files in os.walk(folder):                
                for file in files:
                    if file.find(".tar.gz") == -1:
                        if fileCount%10 == 0:
                            print "Make tar files:" + str(fileCount/10) + ".tar.gz"
                            if tar != None:
                                tar.close()
                            tar = tarfile.open(folder + "/" + str(fileCount/10) + ".tar.gz","w:gz")
                        fullpath = os.path.join(root,file) 
                        print fullpath                  
                        tar.add(fullpath)                            
                        fileCount = fileCount + 1

                tar.close()  
                for file in files:  
                    if file.find(".tar.gz") == -1:
                        os.remove(os.path.join(root,file))              

        
    def unTar(self,folder):
        for item in os.listdir(folder):
            if item.find(".tar.gz") != -1:
                abs_item=os.path.join(folder,item)
                
                tar = tarfile.open(abs_item)
                names = tar.getnames()
                for name in names:
                    tar.extract(name,'/')
                tar.close()
                os.remove(abs_item)    
  
#dicPath = "E:\hw2\posting"
dicPath = "D:\posting"


begin = time.time()

#dicPath = "E:\hw2\posting"

temp = GetSourceIndex(dicPath)
temp.ParseAll()

end = time.time()
file = open("D:\\posting\\FinalInvertedIndex\\1.txt", 'w')
file.write( "ParseAll: " + str(end - begin) + '\n')
file.close()
begin = time.time()
temp = interInvertedIndex(dicPath)
end = time.time()
file = open("D:\\posting\\FinalInvertedIndex\\1.txt", 'a')
file.write( "interInvertedIndex: " + str(end - begin) + '\n')
file.close()

begin = time.time()

a = finalInvertedIndex(dicPath, temp.getCount())


#a = finalInvertedIndex(dicPath, 1)
end = time.time()
file = open("D:\\posting\\FinalInvertedIndex\\1.txt", 'a')
file.write("vbyte: " + str(a.time) + '\n')
file.write( "finalInvertedIndex: " + str(end - begin) + '\n')

file.close()


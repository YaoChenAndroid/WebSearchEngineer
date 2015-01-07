__author__ = 'minzhu'

import os

indexFileNum = 0

def vbyteCompress(orgList):
    '''
    orglist form : [('word','docID-frequence,docID-frequence,...'),(...),...]
            eg. [('cat', '0-3,135-278,140-3,145-12,146-45,646-62,721-35'),
               ('dog', '40-45,216-677,237-23,238-1,239-4,671-4,679-5'),
               ('apple', '137-56,139-345,140-45,143-23,148-45,723-12,725-456')]
    Convert the posting list to a integer list, call vbyteAndIntstr.compress() to write a inverted index
    into the target file and add a pointer in the lexicon file.
    '''

    lexiconFile = open('%s/result/lexicon.txt' % os.getcwd(), 'a')
    for item in orgList:
        #print(item)
        word = item[0]
        docIds = item[1].split(',')
        newDocID = []
        sum = 0
        for docID in docIds:
            if docID == "":
                continue
            ID,frequence = docID.split('-')
            newDocID.append(int(ID)-sum)
            newDocID.append(int(frequence))
            sum = int(ID)
        #print(newDocID)

        global indexFileNum
        fileName = '%s/result/index_%d' % (os.getcwd(), indexFileNum)
        if not os.path.exists(fileName):
            f = open(fileName, 'w')
            f.close()
        filesize = os.path.getsize(fileName)
        if filesize >= (10*1024*1024):
            indexFileNum += 1
            filesize = 0
            fileName = '%s/result/index_%d' % (os.getcwd(), indexFileNum)
            f = open(fileName, 'w')
            f.close()

        vbyteCompress = vbyteAndIntstr('',newDocID,fileName,filesize,0)
        vbyteCompress.compress()
        compressedSize = vbyteCompress.compressedSize()

        lexicon = '%s,%s,%d,%d;' % (word, fileName, filesize, compressedSize)
        lexiconFile.write(lexicon)

    lexiconFile.close()

def searchWord(word):
    '''
    Get the pointer of word in the lexicon file, call vbyteAndIntstr.decompress() to read the data
    the pointer points, convert the binary data to document ids' list.
    '''
    file = open('%s/result/lexicon.txt' % os.getcwd(), 'r')
    data = file.read()
    docIDs = []
    for line in data.split(';'):
        #print(line)
        list = line.split(',')
        if word == list[0]:
            vbyteDecompress = vbyteAndIntstr('',[],list[1],int(list[2]),int(list[3]))
            vbyteDecompress.decompress()
            #print(vbyteDecompress.intstr)

            sum = 0
            isOdd = 1
            docID = 0
            for docid in vbyteDecompress.intstr:
                if isOdd == 1:
                    docID = int(docid)+sum
                    sum += int(docid)
                    isOdd = 0
                else:
                    frequence = docid
                    tuple = '%s,%s' % (docID,frequence)
                    docIDs.append(tuple)
                    isOdd = 1

    del data

    file.close()
    return docIDs



class vbyteAndIntstr:
    '''
    Provides function for convert an integer list to a binary string and write the string
    to the target file, and function for read a part of data from a binary file and convert it
    to an integer list.
    '''
    def __init__(self, vbyte='', intstr=[], filepath='', startpos=0, size = 0):
        self.vbyte = vbyte
        self.intstr = intstr
        self.filepath = filepath
        self.startpos = startpos
        self.size = size

    def compress(self):
        '''
        Convert a integer list to a vay-byte string, then convert the var-byte string to a binary
        string and write it to the target file
        '''
        for number in self.intstr:
            self.vbyte += self.__vbyte__(number)
        self.__convertOneAndZeroToFile__()

    def compressedSize(self):
        return self.size

    def decompress(self):
        '''
        Read specified data from the target file and convert the binary string to a integer list
        '''
        self.__convertFileToOneAndZero__()
        oneZeroList = []
        numberStr = ''
        for i in range(0, len(self.vbyte), 8):
            temp = self.vbyte[i:i+8]
            numberStr += temp
            if temp[0] == '0':
                oneZeroList.append(numberStr)
                numberStr = ''

        for number in oneZeroList:
            count = len(number)/8
            part = 0
            numberStr = ''
            while count > 0:
                numberStr += number[(part*8+1):(part+1)*8]
                count -= 1
                part += 1
            self.intstr.append(int(numberStr,2))

    def __vbyte__(self,number):
        '''
        Convert a number to a var-byte string
        '''
        str = bin(number)
        str = str[2:]
        zeros = '000000'
        if len(str)%7 > 0:
            zlen = (7-len(str)%7)
            prefix = zeros[:zlen]
            str = prefix + str
        newstr = ''
        count = len(str) / 7
        part = 0
        while count > 0:
            if count > 1:
                prefix = '1'
            else:
                prefix = '0'
            newstr += (prefix + str[part*7:(part+1)*7])
            count -= 1
            part += 1

        return newstr


    def __convertFileToOneAndZero__(self):
        '''
        Read a binary string from the target file and convert it into a var-byte string.
        '''
        f = open(self.filepath,'rb')
        f.seek(self.startpos)
        src = f.read(self.size)

        result = []
        for i in src:
            temp = bin(ord(i))[2:]
            temp = '0' * (8-len(temp)) + temp
            result.append(temp)

        self.vbyte = ''.join(result)


    def __convertOneAndZeroToFile__(self):
        '''
        convert the var-byte string using vbyte compress method into a binary string,
        and write it into the target file.
        '''
        result = []
        for i in range(0, len(self.vbyte), 8):
            result.append(chr(int(self.vbyte[i:i+8], 2)))
        data = ''.join(result)
        self.size = len(data)

        f = open(self.filepath, 'a')
        f.seek(self.startpos)
        f.write(data)
        f.close()
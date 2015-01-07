__author__ = 'minzhu'

import os
from GetPostings import PostingOneDataFile
#import webIndex
import tarfile
import gzip

dataIndex = 0

def uncompressData():
    '''
    extract files from archives
    '''
    path = '%s/data' % os.getcwd()
    for root,dirs,files in os.walk('%s/orgdata' % os.getcwd()):
        for file in files:
            print root
            print file
            tar = tarfile.open('%s/%s' % (root,file))
            tar.extractall(path)
            tar.close()
        del root,dirs,files

def main():
    uncompressData()

    docurlfile = open('%s/docID-URL' % os.getcwd(), 'w')
    docurlfile.close()

    postingPath = '%s/posting' % os.getcwd()
    if not os.path.exists(postingPath):
        os.mkdir(postingPath)
    resultPath = '%s/result' % os.getcwd()
    if not os.path.exists(resultPath):
        os.mkdir(resultPath)

    for root,dirs,files in os.walk('%s/data/data' % os.getcwd()):
        print(root)
        print(dirs)
        print(files)
        for file in files:
            pos = file.find('_data')
            if pos > 0:
                dataIndex = file[:pos]
                posting = PostingOneDataFile(int(dataIndex),'%s/%s_data' % (root,dataIndex),
                                             '%s/%s_index' % (root,dataIndex))
                posting.uncompressAndParser()
                del posting

    '''root = '/Users/minzhu/python/WebSearchEngine/InvertedIndex/data/data/4c/tux-4/polybot/gzipped_sorted_nz/vol_2400_2499'
    dataIndex = 2406
    posting = PostingOneDataFile(int(dataIndex),'%s/%s_data' % (root,dataIndex),
                                             '%s/%s_index' % (root,dataIndex))
    posting.uncompressAndParser()'''

    '''with gzip.open('/Users/minzhu/python/WebSearchEngine/InvertedIndex/data'
                   '/data/4c/tux-4/polybot/gzipped_sorted_nz/vol_2400_2499/2406_data'
                           , 'rb') as f_in1:
        data = f_in1.read()'''

    '''dicPath = '%s/posting' % os.getcwd()

    temp = webIndex.GetSourceIndex(dicPath)
    temp.ParseAll()
    temp = webIndex.interInvertedIndex(dicPath)
    temp = webIndex.finalInvertedIndex(dicPath)'''




if __name__ == '__main__':
    main()
    #vbyte(234)
    #print(decompress("1000000101101010100000010110101010000001011010101000000101101010"))
    '''intstr = [40,216,237,238,239]
    vbyteCompress = vbyteAndIntstr('',intstr,'vbyte',0,0)
    vbyteCompress.compress()

    vbyteDecompress = vbyteAndIntstr('',[],'vbyte',0,vbyteCompress.size)
    vbyteDecompress.decompress()
    print(vbyteDecompress.intstr)'''

Document breakdowns:
YaoChen: The document of merge and sort phase part
Min Zhu: The document of rest
Project Breakdowns:
YaoChen: The implement of merge and sort phase 
Min Zhu: The implement of the rest

1)what your program can do? 
1.Unarchive the tar files provided.
2.Uncompress gzip files.
3.Parse every html page, create a posting for every page and write it to a relevant posting file.
4.Create a (document id, url, response code) table.
5.Compress the internal inverted index
6.Use differences and vbyte to compress the inverted index files.Create a few inverted index files which record (document id,frequence)(document id,frequence)... for every word, but not record the word.The size of every file would be 10M.
7.Create a lexicon file which contains pointers for words which point the inverted index of a word in the
  inverted index files.
8.When search a word, the program will return a list in the form of ['document id,frequence','document id,frequence',...].


2) how to run the program? 
OS: Mac OS X 10.9.2
Language: python 2.7
The project directory contains these folders and files:
1.HTMLParser: myparser.c, myparser.h, setup.py
2.orgdata: vol_0_99.tar, vol_100_199.tar, vol_200_299.tar, ...
3.GetPostings.py, webIndex.py, vbyte.py, InvertIndex.py

3)How to run?
Firstly, put the tar files into the folder of orgdata.
Secondly, in the terminal, go to the HTMLParser directory, running:
        python setup.py build will compile myparser.c, and produce an extension module named in the build directory. Copy the module file (named myparser.so) to the HTMLParser folder.
Thirdly, running the python file - InvertIndex.py.
We'll get result files (include inverted index files, docID-URL file and lexicon file) in the result folder.


4) how it works internally
1.Unarchive the tar files provided as the origin data (eg. unarchive vol_0_99.tar and extract files into
  the folder '../data/data/4c/tux-4/polybot/gzipped_sorted_nz/vol_0_99').
2.Scan the extracted gzip file in the folder '../data' iterately and uncompress every gzip file (eg. 23_data)
  and write the data into a temporary file (eg. ../data/23_data_uncompress)
--- Read a line from the index file (eg. 23_index) and parse relevant html page in uncompressed data file (eg. 23_index and 23_data_uncompress)
--- Assign a document ID for every parsed html page according to the parsed sequence
--- Record every parsed html page as a posting with the format of (document ID;word1,word2,word3,...,)
--- Add the posting into a file (eg. postings for pages in 23_data are written into posting_23.txt)
--- Add a record with the format of (url, document ID, response code) into the file '../result/docID-URL'
--- Delete the temporary files (eg. ../data/23_data_uncompress)

3.Add a list into a inverted index file.
--- The merge and sort phase. The detial will be describe following(The merge and sort phase major functions)
	the list with the form [('word','docID-frequence,docID-frequence,...'),(...),...]
            eg. [('cat', '0-3,135-278,140-3,145-12,146-45,646-62,721-35'),
               ('dog', '40-45,216-677,237-23,238-1,239-4,671-4,679-5'),
               ('apple', '137-56,139-345,140-45,143-23,148-45,723-12,725-456')]
--- get the size of the current inverted index file (eg. ../result/index_15), if is larger than 10M, create a new file.
--- convert the list to a integer list ([docID1,frequence,docID2-docID1,frequence,.....])
--- convert the integer list to a var-byte string, then convert the string to a binary string
    and write it to the inverted index file.
--- add a recording (word, inverted index file name, start position, data size) to the lexicon file.

5) how long it takes on the provided data set and how large the resulting index files are
The size of result:2501.28MB(Windows8)
The total time: 225523s
1.unarchive tar files: 249s. (OS: Mac OS X 10.9.2)
2.uncompress and parse data: 5406.59s. (OS: Mac OS X 10.9.2)
3.Get the source index from the parsed files. The time is 47889 s(Windows8)
4.partially merge the source index. The time is 5749.47s(Windows8)
5.get the final inverted index. The time is 868.5s(Windows8)
6.compress the inverted index by vbyte. The time is 165362.4s(Windows8)
 

6) what limitations it has
When read some gzip files, some UnicodeDecodeError would happen which causes uncompress and parse relevant index files failed. 
There is no other files in the '\posting' folders besides the output file of current program.

7) what the major function and modules are
The module done by Min Zhu:
1.uncompressData() in InvertedIndex.py: 
    This function implements unarchive the tar files in the orgdata folder and extract files in every archive to the data folder.
2.class PostingOneDataFile in GetPostings.py: 
    This class can uncompress gzip files, parse html pages in a data file, assign a document ID to a html page
    and record information.
  Functions in PostingOneDataFile:
  __initData__():
        Uncompress a data file, write the uncompressed data into another file
  uncompressAndParser(self):
        Call __initData__() to do some initial jobs.
        Read each line from the index file to get each html page's start position and size,
        then read the html page's content from the uncompressed file and parse it by calling __parseOnePage__(self, url, content, docId)
        in a for loop.
        Final, delete the uncompressed file.
        This function should be called after create a instance.
  __parseOnePage__(url, content, docId):
        This function mainly uses the extension module - myparser.so to parse the html page and
        write postings into the posting_index.txt file, add a record to the docID-URL table.
3.class vbyteAndIntstr in vbyte.py: 
    This class provides function for convert an integer list to a binary string and write the string
    to the target file, and function for read a part of data from a binary file and convert it
    to an integer list.
  Functions in vbyteAndIntstr:
  compress():
        Convert a integer list to a vay-byte string, then convert the var-byte string to a binary
        string and write it to the target file.
  decompress():
        Read specified data from the target file and convert the binary string to a integer list.
  __vbyte__(self,number):
        Convert a number to a var-byte string.
  __convertFileToOneAndZero__(self):
        Read a binary string from the target file and convert it into a var-byte string.
  __convertOneAndZeroToFile__(self):
        Convert the var-byte string using vbyte compress method into a binary string,
        and write it into the target file.
4.vbyteCompress(orgList) in vbyte.py: 
    Convert the posting list to a integer list, call vbyteAndIntstr.compress() to write a inverted index
    into the target file and add a pointer in the lexicon file.
5.searchWord(word) in vbyte.py: 
    Get the pointer of word in the lexicon file, call vbyteAndIntstr.decompress() to read the data
    the pointer points, convert the binary data to document ids' list and return a list in the form
of ['document id,frequence','document id,frequence',...].

The module done by Yao Chen:
The merge and sort phase major functions:
1. make the inverted index file in the alphabetical order of each word
2. get the document ID and frequence of each word
3. compress the intermediate results into 'tar' files
how works
There are 3 step in this phase:
	step 1:Get the source index from the parsed files. The time is 47889s
	step 2: partially merge the source index. The time is 5749.47
	step 3: merge the intermediate inverted index and get the final inverted index. The time is 868.5
Major modules:
step 1:Get the source index from the parsed files
	The formate of data in the parsed files as following:
	"DocID 0: apple, cat, dog, cat"
	"DocID 1: apple, cat, dog"
	After this step, the result format of source index is as following:
	"apple: 0-1,1-1"
	"cat:0-2,1-1"
	"dog:0-1,1-1"
	The source index contain the document ID and word frequence in each document.
	I use the GetSourceIndex class to implement this part. I use the ParseAll(), ParseOne(), saveFile() function in this part.
	ParseAll(): Iterate all the parsed files and call the ParseOne() function to get one source index of pre parsed file.
	ParseOne(): This function will read lines from one parsed file and generate the source index. Then can the saveFile() function
	saveFile(): It will save the source index into the hard drive as txt file.
step 2: partially merge the source index
	In this step, it will merge all the source index into partial inverted index. For example, there are 10 source index file, which will be merge into one partial inverted index in alphabetical order.
	In this part, I use two class "interInvertedIndex" and "merge".
	"interInvertedIndex" class have 3 functions:
		1.loop all the source index files and use the 'merge' class to merge 10 source index files into 1 partial inverted index file.
		2.check the account of the partial inverted index file. If the account of the result file is larger than 10, then use the "merge" class to merge the result files, until the account of the partial inverted index file is smaller than 10 files. Then the program will go to the third step.
		3. compress the source index file into "tar" file.
	"merge" class: I use the fileOpen(),mergeFile(), saveFile(), checkBuffer() function to implement this part.
		fileOpen(): I read 1M data of 10 source index files and put it into a list. Then I put this list into a source list. The source list have 10 element and each of them is a sub list.
		mergeFile(): In this function, I get the top element of each element in the source list. Then put the top element into a heap.
				top element of each element in the source list is as: ("apple": "0-1,1-1")
				The element in the heap is as: ("apple1": "1"). The '1' will indicate the index of the sub list in the source list. The "apple1" means word + index. It used to differentiate the same word in different file. Then we can merge the same word one by one so the document ID of the same word will be increaded in the result file.
		checkBuffer(): When we get a new element from the source list, we wil check the sub list length. If the the sub list is empty, we will read the source file to get new chuck of data. If all data in the source file had been readed, this function will set the "save file" flag to generate the result file.
		saveFile(): save the data in the destined list into one partial inverted index. Then clear the destined list.
step 3: merge the intermediate inverted index and get the final
	In this part, I use two class "finalInverteIndex" and "merge"
	"finalInverteIndex" class have 2 functions:
		1.loop all the source index files and use the 'merge' class to merge all partial inverted index files.
		2.send the result to the next phase: "compress phase".
		3. compress the partial inverted index files into "tar" file.
	"merge" class: I use the fileOpen(),mergeFile(), saveFile(), checkBuffer() function to implement this part.
		fileOpen(), mergeFile(), checkBuffer(): is same as the before.
		saveFile(): send the data in the destined list to the "compress phase". Then clear the destined list.

readme.txt
1.Install simplejson-3.3.3. use command to install setup.py
2. run 'WebScrawler.py' in YaoChen/Project folder

limitations on parameters:
1. only english characters


bugList:
1.may not Parse some url
unimplement function:
1.can not Parse Javascript
	
A list of any special features beyond the basic requirements:
1.used Mutithread to speed up the scrawler
2.deal with the duplicate url by maping the url to Ip address, also remove useless file/path name
3.zip the data of the web page to save space. so it can not be readable by open files directly. The file need to decompress to read

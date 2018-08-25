#readme
    It's a simple scrapy project containing youtube-dl library and flvmerge tool so that you can crawl videos easily.
    
    If you know how to use scrapy,then you can easily use this project and easily improve the code.
    
    If not,look at the [documentation](https://doc.scrapy.org/)
    
    Any questions about scrapy please look at https://github.com/scrapy/scrapy

##Tips:
    in the 'setting.py'  , you can change the 'TEMP_PATH' which stores temporary files , and 'OUTPUT_PATH'  which stores  the final output files.

the spider name is 'youtube_dl' , so you need use 
"scrapy crawl youtube_dl" 
-------------
to start spider.
                                                  
Because of the large video files which need lots of time to download , so you will see the process seems to be stuck. If you want to know if the program is running for downloading , you can run perfmon.exe in Windows to check the python.exe 's traffic.

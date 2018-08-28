readme
=======
It's a **Python 3** project,I don't know if it can run in Python 2.
It's a simple **scrapy** project containing ffmpeg tool , youtube-dl  and you-get libraries so that you can crawl videos easily.

If you know how to use scrapy,then you can easily use this project and easily improve the code.

If not,look at the [documentation](https://doc.scrapy.org/).
    
Any questions about scrapy please look at https://github.com/scrapy/scrapy.

Prerequisites
======
The following dependencies are required and must be installed separately, unless you are using a pre-built package or chocolatey on Windows:

* **[Python 3](https://www.python.org/downloads/)**
* **[Scrapy](https://github.com/scrapy/scrapy)**

Tips:
======

in the **setting.py**  , you can change the **TEMP_PATH** which stores temporary files , and **OUTPUT_PATH**  which stores  the final output files.And **my_defined_urls** is a global dict object which is shared between youtube_dl and you_get libraries,so you don't need to change it.

the spider name is **video** , so you need use "**scrapy crawl video**" to start the spider.

Remember to change the **start_urls** in **video_spider.py** so you crawl what you want.
                                                  
Because of the large video files which need lots of time to download , so you will see the process seems to be stuck. If you want to know if the program is running for downloading , you can run **perfmon.exe** in Windows to check the **python.exe** 's traffic.

@echo off
choice /c:YN  /M:"�Ƿ�����ϴμ�����ȡ��"
if %errorlevel%==2 goto no
if %errorlevel%==1 goto yes
:yes
scrapy crawl video -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:no
choice /c:YN  /M:"��Ҫɾ��ԭ�ȵ���Ϣ�ļ����Ƿ�ȷ�ϣ�"
if %errorlevel%==2 goto end
if %errorlevel%==1 goto ok
:ok
del /f /s /q /a ".\crawls\video_spider_temp\*"
DEL "scrapy.log"
set /p url=������url��ַ:
choice /c:YN  /M:"�Ƿ���ȡͬһ��ϵ��������Ƶ��"
if %errorlevel%==2 goto myno
if %errorlevel%==1 goto myyes
:myyes
scrapy crawl video -a my_url=%url% -a my_playlist=True -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:myno
scrapy crawl video -a my_url=%url% -a my_playlist=False -s JOBDIR=crawls/video_spider_temp -s LOG_FILE=scrapy.log
goto end
:end
echo good bye
pause
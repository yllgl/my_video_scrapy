# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from video_scrapy.items import *
from video_scrapy.flvcopycat import process_flv
from video_scrapy.you_get.processor.join_mp4 import concat_mp4
from video_scrapy.settings import TEMP_PATH,OUTPUT_PATH
import subprocess
from subprocess import DEVNULL
import sys
import os
def get_usable_ffmpeg(cmd):
    cmd=os.path.dirname(__file__)+"/"+cmd
    try:
        p = subprocess.Popen([cmd, '-version'], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        vers = str(out, 'utf-8').split('\n')[0].split()
        assert (vers[0] == 'ffmpeg' and vers[2][0] > '0') or (vers[0] == 'avconv')
        try:
            v = vers[2][1:] if vers[2][0] == 'n' else vers[2]
            version = [int(i) for i in v.split('.')]
        except:
            version = [1, 0]
        return cmd, 'ffprobe', version
    except:
        return None
FFMPEG, FFPROBE, FFMPEG_VERSION = get_usable_ffmpeg('ffmpeg') or get_usable_ffmpeg('avconv') or (None, None, None)
LOGLEVEL = ['-loglevel', 'info']
STDIN = None
class MyFilePipeline(object):
    namedict={}
    enddict={}
    def __init__(self):
        if TEMP_PATH[-1]=="/" or TEMP_PATH[-1]=="\\":
            self.temp=TEMP_PATH
        else:
            self.temp=TEMP_PATH+"/"
        if OUTPUT_PATH[-1]=="/" or OUTPUT_PATH[-1]=="\\":
            self.root=OUTPUT_PATH
        else:
            self.root=OUTPUT_PATH+"/"
        if os.path.exists(self.root):
            pass
        else:
            os.mkdir(self.root)
        if os.path.exists(self.temp):
            pass
        else:
            os.mkdir(self.temp)
    def process_item(self, item, spider):
        if isinstance(item,FileItem):
            name=item['name']
            if item["end"] is True:
                self.enddict.setdefault(name, int(item['fileid']) + 1)
            if item['fileid'] is None and item['end'] is None:
                if item["id"] is None:
                    src=self.root+ item["name"]+"."+item["filetype"]
                    with open(src,"wb") as f:
                        f.write(item["content"])
                else:
                    id=item["id"]
                    src=self.root+"%03d" % int(id) +"_"+item["name"]+"."+item["filetype"]
                    with open(src,"wb") as f:
                        f.write(item["content"])
            else:
                self.combine(item)
    def combine(self,item):
        filetype=item['filetype']
        if filetype=="m3u8" or filetype=="ts":
            self.m3u8_combine(item)
        elif filetype=="flv":
            self.flv_combine(item)
        elif filetype=="mp4":
            self.mp4_combine(item)
    def ffmpeg_concat_ts_to_mkv(self,files, output='output.mkv'):
        print('Merging video parts... ', end="", flush=True)
        params = [FFMPEG] + LOGLEVEL + ['-isync', '-y', '-i']
        params.append('concat:')
        for file in files:
            if os.path.isfile(file):
                params[-1] += file + '|'
        params += ['-c', 'copy', output]

        try:
            if subprocess.call(params, stdin=STDIN) == 0:
                return True
            else:
                return False
        except:
            return False
    def m3u8_combine(self,item):
        name = item['name']
        if item["id"] is None:
            src = self.root+ name + "." + "ts"
        else:
            src = self.root + "%03d" % int(item["id"]) + "_" + name + "." + "ts"
        now_id = self.namedict.setdefault(name, 1)
        temp_path = self.temp + name + str(item['fileid'])
        with open(temp_path, 'wb') as f:
            f.write(item['content'])
        while True:
            temp_path= self.temp + name +"%d"%(now_id)
            if not os.path.exists(temp_path):
                break
            else:
                now_id=now_id+1
        if name in self.enddict:
            if self.enddict[name] == now_id:
                self.enddict.pop(name)
                self.namedict.pop(name)
                temp_path = self.temp + name + "%d"
                mylist = [temp_path % (x) for x in range(1, now_id)]
                if self.ffmpeg_concat_ts_to_mkv(mylist,src) is True:
                    for i in mylist:
                        os.remove(i)
                    print(name+" success")
                else:
                    print(name+" fail")
        if name in self.namedict:
            self.namedict[name]=now_id

    def flv_combine(self,item):
        name = item['name']
        if item["id"] is None:
            src = self.root+ name + "." + "flv"
        else:
            src = self.root + "%03d" % int(item["id"]) + "_" + name + "." + "flv"
        now_id = self.namedict.setdefault(name, 1)
        temp_path = self.temp + name + str(item['fileid'])
        with open(temp_path, 'wb') as f:
            f.write(item['content'])
        while True:
            temp_path= self.temp + name +"%d"%(now_id)
            if not os.path.exists(temp_path):
                break
            else:
                now_id=now_id+1
        if name in self.enddict:
            if self.enddict[name] == now_id:
                self.enddict.pop(name)
                self.namedict.pop(name)
                temp_path = self.temp + name + "%d"
                mylist = [temp_path % (x) for x in range(1, now_id)]
                process_flv(src,mylist)
                for i in mylist:
                    os.remove(i)
                print(name+" success")
        if name in self.namedict:
            self.namedict[name]=now_id
    def mp4_combine(self,item):
        name = item['name']
        if item["id"] is None:
            src = self.root+ name + "." + "mp4"
        else:
            src = self.root + "%03d" % int(item["id"]) + "_" + name + "." + "mp4"
        now_id = self.namedict.setdefault(name, 1)   
        temp_path = self.temp + name + str(item['fileid'])
        with open(temp_path, 'wb') as f:
            f.write(item['content'])
        while True:
            temp_path= self.temp + name +"%d"%(now_id)
            if not os.path.exists(temp_path):
                break
            else:
                now_id=now_id+1
        if name in self.enddict:
            if self.enddict[name] == now_id:
                self.enddict.pop(name)
                self.namedict.pop(name)
                temp_path = self.temp + name + "%d"
                mylist = [temp_path % (x) for x in range(1, now_id)]
                concat_mp4(mylist,src)
                for i in mylist:
                    os.remove(i)
                print(name+" success")
        if name in self.namedict:
            self.namedict[name]=now_id


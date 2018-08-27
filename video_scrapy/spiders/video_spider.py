# -*- coding: utf-8 -*-
import scrapy
import re
import json
from video_scrapy.items import *
import hashlib
from video_scrapy.settings import my_defined_urls


class YoutubeDlSpider(scrapy.Spider):
    name = 'video'
    start_urls = ['http://www.iqiyi.com/v_19rqyrk8ic.html']
    youtube_dl_not_you_get = False
    get_playlist = False
    handle_httpstatus_list = [404]
    iqiyi_id = {}

    def start_requests(self):
        if self.youtube_dl_not_you_get:
            parameter = ['-g', "--rm-cache-dir"]
            for i in self.start_urls:
                if "bilibili" in i:
                    yield scrapy.Request(url=i, callback=self.bili_parse)
                else:
                    parameter.append(i)
            if len(parameter) == 2:
                pass
            else:
                # from video_scrapy.youtube_dl.YoutubeDL import my_defined_urls
                from video_scrapy.youtube_dl import main
                print("waiting for youtube_dl get urls")
                main(parameter)
                print("get youtube_dl urls")
                for i in my_defined_urls:
                    my_url_dict = my_defined_urls[i]
                    for j in my_url_dict:
                        name = str(j).rsplit(".", 1)[0]
                        filetype = str(j).rsplit(".", 1)[-1]
                        yield scrapy.Request(url=my_url_dict[j], callback=self.savefile, meta={"name": name, "filetype": filetype, "fileid": None, "id": None, "end": None})
        else:
            iqiyi_url = []
            for i in self.start_urls:
                if "bilibili" in i:
                    yield scrapy.Request(url=i, callback=self.bili_parse)
                    self.start_urls.remove(i)
                elif "iqiyi.com" in i:
                    iqiyi_url.append(i)
                    self.start_urls.remove(i)
            if len(iqiyi_url) == 0:
                pass
            else:
                for i in self.iqiyi_url_process(iqiyi_url):
                    yield i
            if len(self.start_urls) == 0:
                pass
            else:
                from video_scrapy.you_get.common import main
                # from video_scrapy.you_get import common
                print("waiting for you_get get urls")
                main(my_own_urls=self.start_urls,
                     my_own_playlist=self.get_playlist)
                print("get you_get urls finish")
                if "error" in my_defined_urls:
                    print(
                        "can't get urls for some videos,please look at error.txt for more information!")
                    error = my_defined_urls.pop("error")
                    import datetime
                    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    with open("error.txt", "a") as f:
                        f.write('\n')
                        f.write(nowTime)
                        f.write('\n')
                        f.write("\n".join(error))
                for i in my_defined_urls:
                    my_url_dict = my_defined_urls[i]
                    name = i
                    filetype = my_url_dict.pop("filetype")
                    end_id = len(my_url_dict)
                    if end_id == 1:
                        url = my_url_dict.popitem()[1]
                        filetype = re.search(r"\.(\w+?)\?", url).group(1)
                        if filetype == "m3u8":
                            yield scrapy.Request(url=url, callback=self.parse_m3u8, meta={"name": name})
                    else:
                        for j in my_url_dict:
                            if int(j) == int(end_id):
                                end = True
                            else:
                                end = False
                            yield scrapy.Request(url=my_url_dict[j], callback=self.savefile, meta={"name": name, "filetype": filetype, "fileid": j, "id": None, "end": end})

    def check_iqiyi_finish(self, name):
        self.iqiyi_id[name].setdefault("get_num", 0)
        if "send_num" in self.iqiyi_id[name]:
            if int(self.iqiyi_id[name]["send_num"]) == int(self.iqiyi_id[name]["get_num"]):
                if len(self.iqiyi_id[name].setdefault("error", [])) == 0:
                    pass
                else:
                    self.iqiyi_id[name]["get_num"] = 0
                    self.iqiyi_id[name]["error_num"] = len(
                        self.iqiyi_id[name]["error"])
                    self.iqiyi_id[name].pop("send_num")
                    return True
        return False

    def iqiyi_url_process(self, my_iqiyi_url):
        print("waiting for you_get get iqiyi_urls")
        from video_scrapy.you_get.common import main
        for iqiyi_url in my_iqiyi_url:
            iqiyi_url = [iqiyi_url]
            main(my_own_urls=iqiyi_url,
                 my_own_playlist=self.get_playlist)
            print("get iqiyi_urls finish")
            if "error" in my_defined_urls:
                print(
                    "can't get urls for some videos,please look at error.txt for more information!")
                error = my_defined_urls.pop("error")
                import datetime
                nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open("error.txt", "a") as f:
                    f.write('\n')
                    f.write(nowTime)
                    f.write('\n')
                    f.write("\n".join(error))
            my_temp = list(my_defined_urls.keys())
            for i in my_temp:
                my_url_dict = my_defined_urls[i]
                name = str(i)
                self.iqiyi_id.setdefault(name, {}).setdefault("url", iqiyi_url)
                filetype = my_url_dict.pop("filetype")
                end_id = len(my_url_dict)
                if end_id == 1:
                    url = my_url_dict.popitem()[1]
                    filetype = re.search(r"\.(\w+?)\?", url).group(1)
                    if filetype == "m3u8":
                        yield scrapy.Request(url=url, callback=self.parse_m3u8, meta={"name": name, "iqiyi": None})
                else:
                    for j in my_url_dict:
                        if int(j) == int(end_id):
                            end = True
                        else:
                            end = False
                        yield scrapy.Request(url=my_url_dict[j], callback=self.savefile, meta={"name": name, "filetype": filetype, "fileid": j, "id": None, "end": end})
                my_defined_urls.pop(i)

    def parse_m3u8(self, response):
        url = response.url
        name = response.meta['name']
        if isinstance(response.body, bytes):
            page = response.body.decode('ascii')
        else:
            page = str(response.body)
        file_line = page.split("\n")
        if file_line[0] != "#EXTM3U":
            raise BaseException("非M3U8的链接")
        else:
            unknow = True  # 用来判断是否找到了下载的地址
            i = 1
            for index, line in enumerate(file_line):
                if "EXTINF" in line:
                    unknow = False
                    if file_line[index + 1][0:4] == "http":
                        pd_url = file_line[index + 1]
                    else:
                        if file_line[index + 1][0] != '/':
                            pd_url = url.rsplit(
                                "/", 1)[0] + "/" + file_line[index + 1]
                        else:
                            pd_url = url.rsplit(
                                "/", 1)[0] + file_line[index + 1]
                    if "iqiyi" in response.meta:
                        if len(self.iqiyi_id.setdefault(name, {}).setdefault("error", [])) == 0:
                            if self.iqiyi_id.setdefault(name, {}).setdefault("error_num", 0) == 0:
                                yield scrapy.Request(pd_url, callback=self.savefile,
                                                     meta={'fileid': int(i), 'name': name, 'end': False, "id": None, "filetype": "ts", "iqiyi": None})
                            else:
                                pass
                        else:
                            if int(i) in self.iqiyi_id.setdefault(name, {}).setdefault("error", []):
                                yield scrapy.Request(pd_url, callback=self.savefile,
                                                     meta={'fileid': int(i), 'name': name, 'end': False, "id": None, "filetype": "ts", "iqiyi": None})
                            else:
                                pass
                    else:
                        yield scrapy.Request(pd_url, callback=self.savefile,
                                             meta={'fileid': int(i), 'name': name, 'end': False, "id": None, "filetype": "ts"})
                    i = i + 1
                if "ENDLIST" in line:
                    if "iqiyi" in response.meta:
                        if self.iqiyi_id.setdefault(name, {}).setdefault("error_num", 0) != 0:
                            self.iqiyi_id[name]["send_num"] = self.iqiyi_id[
                                name]["error_num"]
                        else:
                            self.iqiyi_id[name]["send_num"] = i - 1
                        if self.check_iqiyi_finish(name):
                            for k in self.iqiyi_url_process(self.iqiyi_id[name]["url"]):
                                yield k
                    item = FileItem()
                    item["id"] = None
                    item['fileid'] = i
                    item['name'] = name
                    item['end'] = True
                    item['content'] = b''
                    item['filetype'] = 'ts'
                    yield item
            if unknow:
                raise BaseException("未找到对应的下载链接")
            else:
                print("下载请求完成 m3u8 %s" % name)

    def parse(self, response):
        pass

    def bili_parse(self, response):
        if isinstance(response.body, bytes):
            file = str(response.body.decode("utf8"))
        else:
            file = str(response.body)
        temp = re.search(r"__INITIAL_STATE__=(\{.*\});\(fun", file, re.S)
        temp = str(temp.group(1))
        temp = json.loads(temp)
        url = "https://www.kanbilibili.com/api/video/%d/download?cid=%d&quality=64&page=%d"
        if "videoData" in temp:
            videodata = temp['videoData']
            pagelist = videodata['pages']
            aid = videodata["aid"]
            for item in pagelist:
                page = item['page']
                cid = item['cid']
                name = item['part']
                new_url = url % (int(aid), int(cid), int(page))
                yield scrapy.Request(url=new_url, callback=self.bili_get_json, meta={"name": name, "id": page, "Referer": response.url})
        else:
            title = temp["mediaInfo"]["title"]
            pagelist = temp["epList"]
            name = str(title) + "%03d"
            for item in pagelist:
                aid = item["aid"]
                cid = str(item["cid"])
                page = item["index"]
                access_id = int(item["episode_status"])
                if access_id == 2:
                    if len(item["index_title"]) == 0:
                        new_name = name % (int(page))
                    else:
                        new_name = title + "_" + item["index_title"]
                    if "bangumi" in response.url:
                        secretkey = "9b288147e5474dd2aa67085f716c560d"
                        temp = "cid=%s&module=bangumi&otype=json&player=1&qn=112&quality=4" % (
                            str(cid))
                        sign_this = hashlib.md5(
                            bytes(temp + secretkey, 'utf-8')).hexdigest()
                        new_url = "https://bangumi.bilibili.com/player/web_api/playurl?" + \
                            temp + '&sign=' + sign_this
                    else:
                        new_url = url % (int(aid), int(cid), int(page))
                    yield scrapy.Request(url=new_url, callback=self.bili_get_json, meta={"name": new_name, "id": page, "Referer": response.url})
                else:
                    pass

    def bili_get_json(self, response):
        if isinstance(response.body, bytes):
            temp_dict = json.loads(response.body.decode("utf8"))
        else:
            temp_dict = json.loads(str(response.body))
        if "err" in temp_dict:
            if temp_dict['err'] is None:
                my_url_list = temp_dict["data"]["durl"]
                filetype = temp_dict["data"]["format"][0:3]
                end_id = len(my_url_list)
                for i in my_url_list:
                    fileid = i["order"]
                    link_url = i["url"]
                    if int(fileid) == int(end_id):
                        end = True
                    else:
                        end = False
                    yield scrapy.Request(url=link_url, callback=self.savefile, headers={"Origin": "https://www.bilibili.com", "Referer": response.meta["Referer"]},
                                         meta={"name": response.meta["name"], "id": response.meta["id"], "filetype": filetype, "fileid": fileid, "end": end})
        else:
            my_url_list = temp_dict["durl"]
            filetype = temp_dict["format"][0:3]
            end_id = len(my_url_list)
            for i in my_url_list:
                fileid = i["order"]
                link_url = i["url"]
                if int(fileid) == int(end_id):
                    end = True
                else:
                    end = False
                yield scrapy.Request(url=link_url, callback=self.savefile, headers={"Origin": "https://www.bilibili.com", "Referer": response.meta["Referer"]},
                                     meta={"name": response.meta["name"], "id": response.meta["id"], "filetype": filetype, "fileid": fileid, "end": end})

    def savefile(self, response):
        item = FileItem()
        if response.meta['fileid'] is None and response.meta['end'] is None:
            print("get %s" % (response.meta['name']))
            item['fileid'] = None
            item['end'] = None

        else:
            print("get %s__%d" %
                  (response.meta['name'], int(response.meta['fileid'])))
            item['fileid'] = int(response.meta['fileid'])
            item['end'] = response.meta['end']
            if response.meta['id'] is None:
                item['id'] = None
            else:
                item['id'] = int(response.meta['id'])
        item['name'] = str(response.meta['name']).encode(
        ).translate(None, b'\\/:*?"<>|').decode()
        item['filetype'] = response.meta['filetype']
        if "iqiyi" in response.meta:
            self.iqiyi_id[response.meta["name"]]["get_num"] = self.iqiyi_id[
                response.meta["name"]].setdefault("get_num", 0) + 1
            if int(response.status) == 404:
                if int(response.meta['fileid']) in self.iqiyi_id[response.meta["name"]].setdefault("error", []):
                    pass
                else:
                    self.iqiyi_id[response.meta["name"]].setdefault(
                        "error", []).append(int(response.meta["fileid"]))
            else:
                if int(response.meta["fileid"]) in self.iqiyi_id[response.meta["name"]].setdefault("error", []):
                    self.iqiyi_id[response.meta["name"]][
                        "error"].remove(int(response.meta["fileid"]))
                item['content'] = response.body
                yield item
            if self.check_iqiyi_finish(response.meta["name"]):
                for i in self.iqiyi_url_process(self.iqiyi_id[response.meta["name"]]["url"]):
                    yield i
        else:
            item['content'] = response.body
            yield item

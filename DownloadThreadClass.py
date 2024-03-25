# -*- coding: utf-8 -*-

# 爬取B站的视频 Bilibili
# B站的视频地址是直接存储在源网页中的，因此只需要从源网页中解析即可
 
import requests
import json
import re
import os
import time
from LogUtilClass import LogUtilClass, QMessageLogUtilClass
from ProgressUtil import get_trans_size
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
abspath_dir = os.path.dirname(os.path.abspath(__file__))

class DownloadUtilClass(QObject):
    FAILED = -1
    SUCCESS = 0
    update_progressbar_signal = pyqtSignal(dict, int) #发送prgress更新信号

    def __init__(self, url='', collection_url=''):
        super(DownloadUtilClass, self).__init__()
        self.url = url   #视频地址
        self.collection_url =  collection_url  #合集地址,合集中的任意一个地址就可以
        self.log = LogUtilClass()
        self.proxy = {
            'http': 'http://127.0.0.1:33210', 
            'https': 'http://127.0.0.1:33210'
        }
        self.get_id_url_headers = {
            "Host": "www.bilibili.com",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Microsoft Edge\";v=\"122\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "buvid3=A963B183-1CDC-4267-89A8-943EE1C563A913417infoc; LIVE_BUVID=AUTO7016295186861829; buvid_fp_plain=undefined; CURRENT_BLACKGAP=0; DedeUserID=1456109627; DedeUserID__ckMd5=2b9888620b82036a; i-wanna-go-back=-1; buvid4=E398B347-560E-43F3-C364-7D675043163A68822-022012621-S5bJTbM22vkErl%2Btoffbt56MnbDIQJjftMKfb8q5IsMj%2FMngNAYATA%3D%3D; CURRENT_PID=54aba910-cd2a-11ed-a81c-87570bffc288; b_ut=5; hit-new-style-dyn=1; FEED_LIVE_VERSION=V8; _uuid=B5B75B76-F18D-5CCB-5549-B924659E45B349238infoc; is-2022-channel=1; b_nut=100; iflogin_when_web_push=1; enable_web_push=ENABLE; header_theme_version=CLOSE; rpdid=|(k|)uJ~k|lu0J'u~|JYY)lYu; home_feed_column=5; hit-dyn-v2=1; fingerprint=a01161d78032379bdd899ec4c3882415; CURRENT_FNVAL=4048; browser_resolution=1706-861; SESSDATA=9ca2f88c%2C1726634372%2C26657%2A32CjDOVyBDXdF57SsHM_cgm6IeCe2F-rVdlR0CSOV1c2U7l0Q-6MwXfc3rW9XZTq6p7cQSVngyU0JZVkxaM2p5NGM1YTI1THhCLVhWRUNrMDlRMXBaRmdJb2hDYkRNU1VlNEdkUVpYLVA4NUNqWFZ4bGd4Z3FhRndvcnN6Vm5CazFKbDBlSDlCZFlnIIEC; bili_jct=e9870049c21d07b73cccbe6764b05b44; PVID=1; CURRENT_QUALITY=80; buvid_fp=a01161d78032379bdd899ec4c3882415; bsource=search_baidu; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; sid=4xdzrhmx; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTE1MTc1NTYsImlhdCI6MTcxMTI1ODI5NiwicGx0IjotMX0.zncf_qHGM0ypftH-JibsyfB4_Gjeizn9PbcbNNLP5ts; bili_ticket_expires=1711517496; bp_video_offset_1456109627=912510521260900357; b_lsid=B51047EB8_18E71D7DE77"
        }
        self.headers = {
            'Origin' : 'https://www.bilibili.com',
            "Referer": "https://www.bilibili.com/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win32; x32)'
        }
        self.collection_info_list = []  #输入url所属的合集所有视频信息
        self.input_url_info_dict = {}  #输入的url对应的信息
        # self.video_dw_url = ''  #视频下载链接
        # self.audio_dw_url = ''  #音频下载链接
        self.download_url_dict = {}
        self.download_url_list = []
        
        self.video_total_size = 0
        self.audio_total_size = 0

        

        self.is_pause_download = False
        self.is_pause_download_list = []

        self.current_download_size_list = []
        self.video_total_size_list = []
        self.audio_total_size_list = []

    
    def dowload_all_collection(self, collection_url=''):
        if collection_url == '' and self.collection_url != '':
            collection_url = self.collection_url
        if collection_url == '':
            self.log.error('合集地址不能为空,请设置合集地址')
            return DownloadUtilClass.FAILED
        #尝试获取合集地址
        if not self.collection_info_list:
            self.log.warning('当前为获取合集信息,请尝试输入合集地址')
            return DownloadUtilClass.FAILED
        for per_url_info in self.collection_info_list:
            video_url = per_url_info['video_url']
        

    
    def get_collection_info(self, collection_url=''):
        if collection_url == '' and self.collection_url != '':
            collection_url = self.collection_url
        if collection_url == '':
            self.log.error('合集地址不能为空,请设置合集地址')
            return DownloadUtilClass.FAILED
        if collection_url.isspace():
            self.log.error('合集地址不能全为空格,请重新设置合集地址')
            return DownloadUtilClass.FAILED
        #尝试获取合集地址
        #尝试不用代理
        try:
            response =requests.get(collection_url, headers=self.get_id_url_headers)
        except Exception as e:
            self.log.warning('请求失败,尝试设置代理进行请求')
            # self.log.warning(e)
            response =requests.get(collection_url, headers=self.get_id_url_headers, proxies=self.proxy)
        finally:
            pass
        if response.status_code != 200:
            #获取到合集地址
            self.log.error('请求合集信息失败')
            return DownloadUtilClass.FAILED
        #如果为200,表示请求成功。
        #开始解析html
        pattern = r'window.__INITIAL_STATE__=(.*?)</script>'
        collection_info_html = response.text
        try:
            match = re.search(pattern, collection_info_html, re.S)
        except Exception as e:
            self.log.warning(f"解析html失败,{e}")
            return DownloadUtilClass.FAILED
        finally:
            pass
        if match:
            collection_info = match.group(1)
            self.log.info('获取到合集信息')
            # with open(os.path.join(abspath_dir, 'collection_info.json'), 'w', encoding='utf-8') as f:
            #     f.write(collection_info)
        else:
            self.log.error('获取合集信息失败')
            return DownloadUtilClass.FAILED
        if not ";(function" in collection_info:
            self.log.error('网页内容匹配失败,可能是网页内容发生了改变')
            return DownloadUtilClass.FAILED
        collection_info = collection_info.split(";(function")[0]
        #开始解析json
        try:
            collection_info = json.loads(collection_info)
        except Exception as e:
            self.log.error(f"解析json失败,{e}")
            return DownloadUtilClass.FAILED  
        # collection_info_dict = {}
        videoData = collection_info['videoData']
        #判断是按page分的合集还是不是，如果没有ugc_season，则按page分
        if 'ugc_season' not in videoData:
            self.log.info('当前为按page分的合集')
            listData = videoData['pages']
            for i in listData:
                per_url_info_dict = {}
                bvid = videoData['bvid']
                title = i['part']
                page = i['page']
                per_url_info_dict["bvid"] = bvid
                per_url_info_dict["title"] = title
                per_url_info_dict["page"] = page
                self.collection_info_list.append(per_url_info_dict)
            #获取当前输入url对应的视频信息
            input_url_title = listData[int(collection_info['p'])]['part']
            input_url_bvid = videoData['bvid']
            input_url_page = collection_info['p']
            self.input_url_info_dict["bvid"] = input_url_bvid
            self.input_url_info_dict["title"] = input_url_title
            self.input_url_info_dict["page"] = input_url_page
        else:
            self.log.info('当前为按ugc_season分的合集')
            listData = videoData['ugc_season']['sections'][0]['episodes']
            for i in listData:
                per_url_info_dict = {}
                title = i['title']
                bvid = i['bvid']
                per_url_info_dict["bvid"] = bvid
                per_url_info_dict["title"] = title
                per_url_info_dict["page"] = ""
                self.collection_info_list.append(per_url_info_dict)
            #获取当前输入url对应的视频信息
            input_url_title = videoData['title']
            input_url_bvid = videoData['bvid']
            self.input_url_info_dict["bvid"] = input_url_bvid
            self.input_url_info_dict["title"] = input_url_title
            self.input_url_info_dict["page"] = ""
        return DownloadUtilClass.SUCCESS


    def get_single_url_info(self, url=''):
        if url == '' and self.url != '':
            url = self.url
        if url == '':
            self.log.error('视频地址不能为空,请设置视频地址')
            return DownloadUtilClass.FAILED
        if url.isspace():
            self.log.error('视频地址不能全为空格,请重新设置视频地址')
        try:
            response =requests.get(url, headers=self.get_id_url_headers)
        except Exception as e:
            self.log.warning('请求失败,尝试设置代理进行请求')
            # self.log.warning(e)
            response =requests.get(url, headers=self.get_id_url_headers, proxies=self.proxy)
        finally:
            pass
        if response.status_code != 200:
            #获取到合集地址
            self.log.error('请求视频信息失败')
            return DownloadUtilClass.FAILED
        #开始解析html
        pattern = r'window.__INITIAL_STATE__=(.*?)</script>'
        collection_info_html = response.text
        try:
            match = re.search(pattern, collection_info_html, re.S)
        except Exception as e:
            self.log.warning(f"解析html失败,{e}")
            return DownloadUtilClass.FAILED
        finally:
            pass
        if match:
            collection_info = match.group(1)
            self.log.info('获取到合集信息')
            # with open(os.path.join(abspath_dir, 'collection_info.json'), 'w', encoding='utf-8') as f:
            #     f.write(collection_info)
        else:
            self.log.error('获取合集信息失败')
            return DownloadUtilClass.FAILED
        if not ";(function" in collection_info:
            self.log.error('网页内容匹配失败,可能是网页内容发生了改变')
            return DownloadUtilClass.FAILED
        collection_info = collection_info.split(";(function")[0]
        #开始解析json
        try:
            collection_info = json.loads(collection_info)
        except Exception as e:
            self.log.error(f"解析json失败,{e}")
            return DownloadUtilClass.FAILED  
        # collection_info_dict = {}
        
        videoData = collection_info['videoData']
        bvid = videoData['bvid']
        title = videoData['title']
        page = ""
        self.input_url_info_dict["bvid"] = bvid
        self.input_url_info_dict["title"] = title
        self.input_url_info_dict["page"] = page
        videoData = collection_info['videoData']
        #判断是按page分的合集还是不是，如果没有ugc_season，则按page分
        self.log.debug(f"videodata: {videoData}")
        if 'ugc_season' not in videoData:
            self.log.info('当前为按page分的合集')
            listData = videoData['pages']
            self.log.warning(f"listData:{listData}")
            for i in listData:
                per_url_info_dict = {}
                bvid = videoData['bvid']
                title = i['part']
                page = i['page']
                per_url_info_dict["bvid"] = bvid
                per_url_info_dict["title"] = title
                per_url_info_dict["page"] = page
                self.collection_info_list.append(per_url_info_dict)
            #获取当前输入url对应的视频信息
            # input_url_title = listData[int(collection_info['p'])]['part']  #注意这里索引-1
            input_url_title = listData[int(collection_info['p'])-1]['part']
            input_url_bvid = videoData['bvid']
            input_url_page = collection_info['p']
            self.input_url_info_dict["bvid"] = input_url_bvid
            self.input_url_info_dict["title"] = input_url_title
            self.input_url_info_dict["page"] = input_url_page
        return DownloadUtilClass.SUCCESS

    def get_download_url(self, url='', bvid=''):
        if url == '' and self.url != '':
            url = self.url
        if url == '':
            self.log.error('视频地址不能为空,请设置视频地址')
            return DownloadUtilClass.FAILED
        if url.isspace() and bvid.isspace():
            self.log.error('视频地址或bvid不能全为空格,请重新设置视频地址')
            return DownloadUtilClass.FAILED
        #设置防盗链referer
        self.headers['Referer'] = url
        try:
            response =requests.get(url, headers=self.get_id_url_headers)
        except Exception as e:
            self.log.warning('请求失败,尝试设置代理进行请求')
            # self.log.warning(e)
            response =requests.get(url, headers=self.get_id_url_headers, proxies=self.proxy)
        finally:
            pass
        if response.status_code != 200:
            #获取到合集地址
            self.log.error('请求视频信息失败')
            return DownloadUtilClass.FAILED
        #开始解析html
        pattern = r'window.__playinfo__=(.*?)</script>'
        # pattern = r'window\.__(\w+)=(.*?)</script>'

        try:
            match = re.search(pattern, response.text, re.S)
        except Exception as e:
            self.log.warning(f"解析html失败,{e}")
            return DownloadUtilClass.FAILED
        finally:
            pass
        if match:
            url_info = match.group(1)
            self.log.info(f'获取到视频{url}的信息')
        else:
            self.log.error(f'获取视频{url}信息失败')
            # with open(os.path.join(abspath_dir, 'll.html'), 'w') as f:
            #     f.write(response.text)
            return DownloadUtilClass.FAILED
        #开始解析json
        try:
            url_info = json.loads(url_info)
        except Exception as e:
            self.log.error(f"解析json失败,{e}")
            return DownloadUtilClass.FAILED
        if url_info['code'] != 0:
            self.log.warning(f'响应json[\'code\']!=0,获取视频{url}信息失败')
        video_dw_url_list = url_info['data']['dash']['video']
        audio_dw_url_list = url_info['data']['dash']['audio']
        self.download_url_dict['video_dw_url_list'] = video_dw_url_list
        self.download_url_dict['audio_dw_url_list'] = audio_dw_url_list
        self.download_url_list.append(self.download_url_dict)
        # print('end')
        return DownloadUtilClass.SUCCESS
        

    def download_single_url(self, click_index, save_path, dw_video_url='',dw_audio_url='', bvid=''):
        if dw_video_url == '':
            dw_video_url = self.download_url_dict['video_dw_url_list'][0]['baseUrl']
        if dw_audio_url == '':
            dw_audio_url = self.download_url_dict['audio_dw_url_list'][0]['baseUrl']
        
        video_total_size = self.get_single_file_total_size(dw_video_url)
        audioi_total_size = self.get_single_file_total_size(dw_audio_url)
        self.video_total_size_list.append({str(click_index) : video_total_size})
        self.audio_total_size_list.append({str(click_index) : audioi_total_size})
        
        save_video_path = save_path
        save_audio_path = save_path.strip('mp4')+'.mp3'

        self.is_pause_download_list.append(self.is_pause_download)
        self.download_single_video(click_index, save_video_path, dw_video_url)
        self.download_single_audio(click_index, save_audio_path, dw_audio_url)
        return DownloadUtilClass.SUCCESS


    def download_single_video(self, click_index, save_path, video_url='', bvid=''):
        pass
        if video_url == '':
            video_url = self.download_url_dict['video_dw_url_list'][0]['baseUrl']
            bvid = self.download_url_dict['video_dw_url_list'][0]['bvid']

        headers = self.headers
        video_total_size = self.get_single_file_total_size(video_url)
        self.download_single_file(video_url, save_path, "video", video_total_size, click_index)
        

    def download_single_audio(self, click_index, save_path, audio_url='', bvid=''):
        pass
        if audio_url == '':
            audio_url = self.download_url_dict['audio_dw_url_list'][0]['baseUrl']
            bvid = self.download_url_dict['audio_dw_url_list'][0]['bvid']

        headers = self.headers
        audio_total_size = self.get_single_file_total_size(audio_url)
        self.download_single_file(audio_url, save_path, "audio", audio_total_size, click_index)


    def get_single_file_total_size(self, dw_url):
        #这里需要视频和音频加在一起
        headers = self.headers
        proxy = self.proxy
        try:
            res_length = requests.get(dw_url, headers=headers, stream=True)
        except requests.exceptions.ConnectionError:
            res_length = requests.get(dw_url, headers=headers, stream=True, proxies=proxy)
        total_size = int(res_length.headers['Content-Length'])
        return total_size
    
    def get_single_file_current_dw_size(self, save_path):
        #这里需要视频和音频加在一起
        current_dw_size = os.path.getsize(save_path)
        return current_dw_size
    
    def detect_file_is_exit(self, save_path):
        if os.path.exists(save_path) or False:
            user_choice = QMessageLogUtilClass().show("提示", f"文件{save_path.split('/')[-1]}已存在,是否覆盖？", set_cancel_button=True)
            if user_choice == QMessageBox.Ok:
                os.remove(save_path)
                return False
            else:
                return True
        else:
            return False
    
    def download_single_file(self, dw_url, save_path, download_file_type, total_size, click_index):
        headers = self.headers
        proxy = self.proxy
        if download_file_type == 'video':
            temp_save_path = save_path.strip('mp4')+'temp'
        if download_file_type == 'audio':
            temp_save_path = save_path.strip('mp3')+'temp'
        else:
            self.log.warning("不符合要求的下载格式")
        # print(temp_save_path)
        self.log.info(f"当前下载文件暂存在: {temp_save_path}")
        if os.path.exists(save_path) or False: 
            # print("文件已存在,是否覆盖？")
            user_choice = QMessageLogUtilClass().show(f"文件{save_path.split('/')[-1]}已存在,是否覆盖？", "文件已存在,是否覆盖？", set_cancel_button=True)
            self.log.info(f"用户选择: {user_choice}")
            # return 
            if user_choice == QMessageBox.Ok:
                os.remove(save_path)
            elif user_choice == QMessageBox.Cancel:
                return
            # os.remove(self.file_path)
        if os.path.exists(temp_save_path): 
            temp_size = os.path.getsize(temp_save_path)
            if temp_size == total_size:
                # print("文件已下载完成，无需重复下载！")
                LogUtilClass().info(f"文件{save_path.split('/')[-1]}已下载完成，无需重复下载！")
                os.rename(temp_save_path, save_path)
                return
            # print("当前：%d 字节， 总：%d 字节， 已下载：%2.2f%% " % (temp_size, total_size, 100 * temp_size / total_size))
            LogUtilClass().info("当前：%d 字节， 总：%d 字节， 已下载：%2.2f%% " % (temp_size, total_size, 100 * temp_size / total_size))
        else:
            temp_size = 0
            # print("总：%d 字节，开始下载..." % (total_size,))
            LogUtilClass().info("总：%d 字节，开始下载..." % (total_size,))

        headers['Range'] = 'bytes=%d-' % temp_size
                   
        try:
            res_left = requests.get(dw_url, stream=True, headers=headers)
        except Exception as e:
            res_left = requests.get(dw_url, stream=True, headers=headers, proxies=proxy)
        
        # return
        with open(temp_save_path, "ab") as f:
            for chunk in res_left.iter_content(chunk_size=1024):
                #判断是否暂停下载
                if self.is_pause_download_list[click_index] == True:
                    self.log.info(f"索引: {click_index} 暂停下载")
                    break
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()

                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
                # print(self.video_total_size_list[click_index][str(click_index)])
                # print(self.video_total_size_list[click_index])
                # print(type(click_index))
                # print(click_index)
                # return
                now_dw_percent = temp_size / (int(self.video_total_size_list[click_index][str(click_index)])+\
                                              self.audio_total_size_list[click_index][str(click_index)]) * 100
                trans_total_size = get_trans_size((int(self.video_total_size_list[click_index][str(click_index)])+\
                                              self.audio_total_size_list[click_index][str(click_index)]))
                trans_now_dw_size = get_trans_size(temp_size)
                progress_label_value = str(trans_now_dw_size) + ' / ' + str(trans_total_size)
                value_msg = {
                    "progress_label_value" : progress_label_value,
                    "progressBar_value" : now_dw_percent
                }
                # self.log.debug("发送信号了")
                # DownloadUtilClass().update_progressbar_signal.emit(value_msg) #这样写不对
                self.update_progressbar_signal.emit(value_msg, click_index) #
            
        os.rename(temp_save_path, save_path)
        # print('end')
        self.log.info(f"文件: {save_path.split('/')[-1]} 下载结束")


class DownloadThread(QThread):
    progressChanged_signal = pyqtSignal(dict,int) #发送下载进度更新信号
    finished = pyqtSignal(int)  #发送下载结束信号
    # parse_collection_finish_signal = pyqtSignal(list) #解析合集成功信号
    get_single_url_info_finish_signal = pyqtSignal(dict, int) #获取单个url的信息完成信号
    send_sequence_thread_end_signal = pyqtSignal(str)  #顺序执行线程结束信号
    # send_single_url_info_in_collection_finish_signal = pyqtSignal(dict, int)

    '''===================================='''
    send_single_url_info_finish_signal = pyqtSignal(dict, int) #获取单个url的信息完成信号
    parse_collection_finish_signal = pyqtSignal(int, list) #解析合集成功信号
    send_single_url_info_in_collection_finish_signal = pyqtSignal(dict, int, float)

    def __init__(self,click_index, get_per_collection_url_info_thread_list=[],  url='', collection_url='', video_url='',audio_url='', save_path='', save_video_path = '', save_audio_path = '',\
                   is_pause = False, total_size = None, download_file_type = "video_and_audio", is_cover_old_file=False, options=None,\
                    collection_info_list=[], index_in_collection=None, float_time_stamp=None):
        super().__init__()
        self.options = options
        self.get_per_collection_url_info_thread_list = get_per_collection_url_info_thread_list
        self.url = url
        self.log = LogUtilClass()
        self.save_path = save_path.replace(' ','_')
        if save_video_path == '' :
            self.log.error("视频保存路径不能为空")
            self.save_video_path = self.save_path
        if save_audio_path == '' :
            self.log.error("音频保存路径不能为空")
            self.save_audio_path = self.save_path
        self.save_video_path = self.save_video_path.replace(' ','_')
        self.save_audio_path = self.save_audio_path.replace(' ','_')
        self.click_index = click_index
        self.is_pasue = is_pause
        self.total_size = total_size
        self.download_file_type = download_file_type
        self.current_downloaded_size = 0
        self.save_video_temp_path = ''
        self.save_audio_temp_path = ''
        self.download_video_url = video_url
        self.download_audio_url = audio_url
        self.collection_url = collection_url
        self.collection_info_list = collection_info_list
        self.index_in_collection = index_in_collection
        self.float_time_stamp = float_time_stamp

        self.proxy = {
            'http': 'http://127.0.0.1:33210', 
            'https': 'http://127.0.0.1:33210'
        }
        self.headers = {
            'Origin' : 'https://www.bilibili.com',
            "Referer": "https://www.bilibili.com/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win32; x32)'
        }

        self.log.error(f"我{self}被创建了")

    
    # 信号与槽函数
    # @pyqtSlot()
    def get_pause_download_signal(self, value_dict):
        print(f"wobeidianjile{self.click_index}")
        LogUtilClass().debug(f"我{self}的get_pause_download_signal被点击了，获取暂停下载的信号")
        if value_dict['click_index'] == self.click_index:
            print(value_dict)
            self.is_pasue = value_dict['is_pause']

    def send_update_progressbar_signal(self):
        # LogUtilClass().debug("发送更新进度的信号")
        progress = int((self.current_downloaded_size / self.total_size) * 100)
        trans_total_size = get_trans_size(self.total_size)
        trans_now_dw_size = get_trans_size(self.current_downloaded_size)
        progress_label_value = str(trans_now_dw_size) + ' / ' + str(trans_total_size)
        value_msg = {}
        value_msg['progressBar_value'] = progress
        value_msg['progress_label_value'] = progress_label_value
        self.progressChanged_signal.emit(value_msg, self.click_index)

    def download_video(self):
        LogUtilClass().info(f"开始下载视频")
        LogUtilClass().info(f"下载连接: {self.download_video_url}")
        LogUtilClass().info(f"当前下载进度: {self.current_downloaded_size}")
        #首先检查当前的现在进度,来判断是否需要续传
        if os.path.exists(self.save_video_path): #说明audio已经下载成功了
            current_video_size = os.path.getsize(self.save_video_path)
            self.current_downloaded_size += current_video_size
            self.send_update_progressbar_signal()
            # QMessageLogUtilClass().show("1","视频已经存在")
            # self.finished.emit(self.click_index) 
            #==================
            #由于再主界面进行了决定这里直接移除
            os.remove(self.save_video_path)
            return
        headers = self.headers
        #如果没下载完，就进行续传
        if not os.path.exists(self.save_video_temp_path): 
            current_video_size = 0
        else: #说明存在temp文件，需要续传
            current_video_size = os.path.getsize(self.save_video_temp_path)
        self.current_downloaded_size += current_video_size
        headers['Range'] = 'bytes=%d-' % current_video_size
        try:
            response = requests.get(self.download_video_url,headers=headers, stream=True)
        except Exception as e:
            response = requests.get(self.download_video_url,headers=headers, proxies=self.proxy, stream=True)
        if self.total_size == None:
            self.total_size = int(response.headers.get('Content-Length', 0))
        with open(self.save_video_temp_path, 'ab') as f:
            self.log.warning(f"保存视频的暂存地址为: {self.save_video_temp_path}")
            self.log.warning(f"当前是否暂停{self.is_pasue}")
            for chunk in response.iter_content(chunk_size=8192): #不能更新太快
            # for chunk in response.iter_content(chunk_size=1024):
                # self.log.warning(f"当前是否暂停{self.is_pasue}")
                if self.is_pasue:
                    LogUtilClass().warning("暂停下载")
                    break
                if chunk:
                    f.write(chunk)
                    self.current_downloaded_size += len(chunk)
                    progress = int((self.current_downloaded_size / self.total_size) * 100)
                    trans_total_size = get_trans_size(self.total_size)
                    trans_now_dw_size = get_trans_size(self.current_downloaded_size)
                    progress_label_value = str(trans_now_dw_size) + ' / ' + str(trans_total_size)
                    value_msg = {}
                    value_msg['progressBar_value'] = progress
                    value_msg['progress_label_value'] = progress_label_value
                    self.progressChanged_signal.emit(value_msg, self.click_index)
            f.close()
        
        LogUtilClass().debug(f"下载视频结束")
        # self.finished.emit(self.click_index) #不能在这发射，因为还有audio没下载

    def download_audio(self):
        LogUtilClass().info(f"开始下载视音频")
        LogUtilClass().info(f"下载连接: {self.download_audio_url}")
        LogUtilClass().info(f"当前下载进度: {self.current_downloaded_size}")
        #首先检查当前的现在进度,来判断是否需要续传
        if os.path.exists(self.save_audio_path): #说明audio已经下载成功了
            current_audio_size = os.path.getsize(self.save_audio_path)
            self.current_downloaded_size += current_audio_size
            self.send_update_progressbar_signal()
            
            # self.finished.emit(self.click_index) #不能在这发射，因为还有audio没下载
            #由于再主界面进行了决定这里直接移除
            os.remove(self.save_audio_path)
            return
        headers = self.headers
        #如果没下载完，就进行续传
        if not os.path.exists(self.save_audio_temp_path): #说明存在temp文件，需要续传
            current_audio_size = 0
        else:
            current_audio_size = os.path.getsize(self.save_audio_temp_path)
        self.current_downloaded_size += current_audio_size
        headers['Range'] = 'bytes=%d-' % current_audio_size
        try:
            response = requests.get(self.download_audio_url,headers=headers, stream=True)
        except Exception as e:
            response = requests.get(self.download_audio_url,headers=headers, proxies=self.proxy, stream=True)
        if self.total_size == None:
            self.total_size = int(response.headers.get('Content-Length', 0))
        with open(self.save_audio_temp_path, 'ab') as f:
            for chunk in response.iter_content(chunk_size=8192): #不能更新太快
            # for chunk in response.iter_content(chunk_size=1024):
                if self.is_pasue:
                    LogUtilClass().warning("暂停下载")
                    break
                if chunk:
                    f.write(chunk)
                    self.current_downloaded_size += len(chunk)
                    self.send_update_progressbar_signal()
            f.close()
        
        LogUtilClass().debug(f"下载音频结束")
        # self.finished.emit(self.click_index)
    def combine_video_and_audio(self):
        if self.download_file_type == "video_and_audio":
            command=r'ffmpeg -i {} -i {} -acodec copy -vcodec copy -y {}'\
                .format(self.save_video_temp_path, self.save_audio_temp_path,self.save_video_path) #由于主线程已经选择覆盖了，所以这里-y
            # print(command)
            # command = command.replace(' ','_')
            LogUtilClass().info(command)
            os.system(command=command)
            #合并之后将两个文件删除
            time.sleep(0.5)
            # os.remove(self.save_video_temp_path)
            # os.remove(self.save_audio_temp_path)
        else:
            pass

    def parse_collection(self):
        #然后开始解析
        LogUtilClass().info(f"开始解析合集!!!")
        collection_url = self.collection_url
        download_util = DownloadUtilClass()
        download_util.get_collection_info(self.collection_url)
        collection_info_list = download_util.collection_info_list
        # return collection_info_list
        if collection_info_list:
            pass
            # print(collection_info_list)
        self.parse_collection_finish_signal.emit(self.click_index, collection_info_list)

    def get_single_url_info(self,url, index):
        try:
            this_url_info_dict = {}
            this_url_info_dict['url'] = url
            this_url_info_dict['parse_single_url'] = url
            this_url_info_dict['parse_collection_url'] = url
            download_util = DownloadUtilClass()
            download_util.get_single_url_info(url)
            LogUtilClass().info(download_util.input_url_info_dict)
            # this_url_info_dict = {}
            for kk in [' ', '%', '!', '@', '#', '$', '%', '^' ,'&', '*','(', ')', '+', '=', '~', '`', '|', '\\', '/', '"', "'",".","?"]:
                download_util.input_url_info_dict['title'] = download_util.input_url_info_dict['title'].replace(kk , '_')
            this_url_info_dict['title'] = download_util.input_url_info_dict['title']
            this_url_info_dict['bvid'] = download_util.input_url_info_dict['bvid']
            this_url_info_dict['page'] = download_util.input_url_info_dict['page']
            download_util.get_download_url(url)
            download_url_list = download_util.download_url_list
            download_url_dict = download_url_list[0]
            # print(download_url_dict)
            this_url_info_dict['download_url_dict'] = download_url_dict
            can_download_quality_list = []
            for i in download_url_dict['video_dw_url_list']:
                per_quality_dict = {}
                per_quality_dict['id'] = str(i['id'])
                per_quality_dict['codecs'] = i['codecs']
                per_quality_dict['baseUrl'] = i['baseUrl']
                can_download_quality_list.append(per_quality_dict)
            this_url_info_dict['can_download_quality_list'] = can_download_quality_list
            this_url_info_dict['err_dict'] = {}
            self.send_single_url_info_finish_signal.emit(this_url_info_dict, index)
        except Exception as e:
            self.log.error(e)
            this_url_info_dict['err_dict'] = {}
            this_url_info_dict['err_dict'] = {'parse_single_url_err':e}
            # print(this_url_info_dict['err_dict'])
            self.send_single_url_info_finish_signal.emit(this_url_info_dict, index)
        return
    
    def get_single_url_info_in_collection(self):
        try:
            this_url_info_dict = {}
            this_url_info_dict['url'] = self.url
            this_url_info_dict['parse_single_url'] = self.url
            this_url_info_dict['parse_collection_url'] = self.url
            download_util = DownloadUtilClass()
            download_util.get_single_url_info(self.url)
            print("hello")
            print(download_util.input_url_info_dict)
            LogUtilClass().info(download_util.input_url_info_dict)
            # this_url_info_dict = {}
            for kk in [' ', '%', '!', '@', '#', '$', '%', '^' ,'&', '*','(', ')', '+', '=', '~', '`', '|', '\\', '/', '"', "'",".","?"]:
                download_util.input_url_info_dict['title'] = download_util.input_url_info_dict['title'].replace(kk , '_')
            this_url_info_dict['title'] = download_util.input_url_info_dict['title']
            this_url_info_dict['bvid'] = download_util.input_url_info_dict['bvid']
            this_url_info_dict['page'] = download_util.input_url_info_dict['page']
            download_util.get_download_url(self.url)
            download_url_list = download_util.download_url_list
            download_url_dict = download_url_list[0]
            # print(download_url_dict)
            this_url_info_dict['download_url_dict'] = download_url_dict
            can_download_quality_list = []
            for i in download_url_dict['video_dw_url_list']:
                per_quality_dict = {}
                per_quality_dict['id'] = str(i['id'])
                per_quality_dict['codecs'] = i['codecs']
                per_quality_dict['baseUrl'] = i['baseUrl']
                can_download_quality_list.append(per_quality_dict)
            this_url_info_dict['can_download_quality_list'] = can_download_quality_list
            this_url_info_dict['err_dict'] = {}
            self.log.info(f"没有错误.collection{self.index_in_collection}执行完毕，发送信号")
            self.send_single_url_info_in_collection_finish_signal.emit(this_url_info_dict, self.index_in_collection,\
                                                                        self.float_time_stamp)
        except Exception as e:
            self.log.error(e)
            this_url_info_dict['err_dict'] = {}
            this_url_info_dict['err_dict'] = {'parse_single_url_in_collection_err':e}
            # print(this_url_info_dict['err_dict'])
            self.log.error(f"发送错误.collection{self.index_in_collection}执行完毕，发送信号")
            self.send_single_url_info_in_collection_finish_signal.emit(this_url_info_dict, self.index_in_collection,\
                                                                        self.float_time_stamp)
        return
        
    def run(self):
        self.log.error(f"我{self}开始run了")
        #先休眠一下
        time.sleep(0.5) #因为主界面如果选择删除文件,删除文件也需要时间
        if self.options == "get_single_url_info":
            self.log.error(f"我{self}我执行的任务: get_single_url_info")
            self.get_single_url_info(self.url, self.click_index)
        elif self.options == "download_single":
            if self.download_file_type == "video_and_audio":
                self.save_video_temp_path = self.save_video_path.strip('mp4')+'tempmp4'
                self.save_audio_temp_path = self.save_audio_path.strip('mp3')+'tempmp3'
            elif self.download_file_type == "video":
                self.save_video_temp_path = self.save_video_path.strip('mp4')+'tempmp4'
            elif self.download_file_type == "audio":
                self.save_audio_temp_path = self.save_audio_path.strip('mp3')+'tempmp3'
            else:
                self.log.warning("不符合要求的下载格式")
                return
            #然后设置暂存地址
            if self.download_file_type == "video_and_audio":
                self.save_video_temp_path = self.save_video_path.strip('mp4')+'tempmp4'
                self.save_audio_temp_path = self.save_audio_path.strip('mp3')+'tempmp3'
            elif self.download_file_type == "video":
                self.save_video_temp_path = self.save_video_path.strip('mp4')+'tempmp4'
            elif self.download_file_type == "audio":
                self.save_audio_temp_path = self.save_audio_path.strip('mp3')+'tempmp3'
            else:
                self.log.warning("不符合要求的下载格式")
                return
            if self.download_file_type == "video_and_audio":
                self.download_video()
                print(self.current_downloaded_size)
                print(self.save_path)
                self.download_audio()
                print(self.current_downloaded_size)
                self.send_update_progressbar_signal()
                #这里判断是否音视频都下载成功了
                if self.current_downloaded_size == self.total_size: #说明下载完成
                    #开始合并, 不用改后缀就可以合并
                    self.combine_video_and_audio()
                    #结束后发送一次信号，进行线程销毁
                    value_msg = {}
                    value_msg['end'] = True
            #         os.remove(self.save_video_temp_path)
            # os.remove(self.save_audio_temp_path)
                    value_msg['save_video_temp_path'] = self.save_video_temp_path
                    value_msg['save_audio_temp_path'] = self.save_audio_temp_path
                    self.progressChanged_signal.emit(value_msg,self.click_index)
                    # self.terminate()
                    # if self.isFinished():
                    #     self.deleteLater() #直接线程自毁得了 好型不太行，好像不能在线程内部自毁
        elif self.download_file_type == "collection_parse": #直接启动合集解析线程
            LogUtilClass().debug("开始解析合集")
            self.parse_collection()
        elif self.options == "get_single_url_info_in_collection":
            self.get_single_url_info_in_collection()
            


        '''
        print("satar_run")
        if self.download_file_type == "start_sequence":
            print("get_per_collection_url_info_thread_list")
            for i in self.get_per_collection_url_info_thread_list:
                LogUtilClass().debug(i)
                i.start()
                i.wait() #等待线程结束
            self.send_sequence_thread_end_signal.emit('end')
            # return
        
        #检查文件是否已经存在
        if self.download_file_type == "video_and_audio":
            # is_file_exist = DownloadUtilClass().detect_file_is_exit(self.save_video_path)  #在线程中调用Qmessage好像很卡,直接再主线程中阻断这种情况
            # if is_file_exist:
            if os.path.exists(self.save_video_path):
                LogUtilClass().warning("文件已经存在，无需下载")
                return
        elif self.download_file_type == "collection_parse": #直接启动合集解析线程
            LogUtilClass().debug("开始解析合集")
            self.parse_collection()
            return
        elif self.download_file_type == "get_single_url_info": #直接启动合集解析线程
            LogUtilClass().debug(f"开始获取{self.url}信息")
            self.get_single_url_info(self.url, self.click_index)
            return
        else:
            return
        #然后设置暂存地址
        if self.download_file_type == "video_and_audio":
            self.save_video_temp_path = self.save_video_path.strip('mp4')+'tempmp4'
            self.save_audio_temp_path = self.save_audio_path.strip('mp3')+'tempmp3'
        elif self.download_file_type == "video":
            self.save_video_temp_path = self.save_video_path.strip('mp4')+'tempmp4'
        elif self.download_file_type == "audio":
            self.save_audio_temp_path = self.save_audio_path.strip('mp3')+'tempmp3'
        else:
            self.log.warning("不符合要求的下载格式")
            return
        if self.download_file_type == "video_and_audio":
            self.download_video()
            print(self.current_downloaded_size)
            self.download_audio()
            print(self.current_downloaded_size)
            self.send_update_progressbar_signal()
            #这里判断是否音视频都下载成功了
            if self.current_downloaded_size == self.total_size: #说明下载完成
                #将temp文件改为正常后缀
                # if os.path.exists(self.save_video_temp_path):
                #     os.rename(self.save_video_temp_path, self.save_video_path)
                # if os.path.exists(self.save_audio_temp_path):
                #     os.rename(self.save_audio_temp_path, self.save_audio_path)
                #开始合并
                self.combine_video_and_audio()

            
        elif self.download_file_type == "video":
            self.download_video()
        elif self.download_file_type == "audio":
            self.download_audio()

    
        
        self.finished.emit(self.click_index)
    '''

        

class TestClass:
    def __init__(self) -> None:
        pass

    def test_get_collection_info(self, collection_url):
        downloadutil = DownloadUtilClass()
        downloadutil.get_collection_info(collection_url)     
        collection_info = downloadutil.collection_info_list 
        print(collection_info)
        input_url_info = downloadutil.input_url_info_dict
        print(input_url_info)

    def test_get_single_url_info(self, url):
        downloadutil = DownloadUtilClass()
        downloadutil.get_single_url_info(url)
        single_url_info = downloadutil.input_url_info_dict
        print(single_url_info)
        

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class MyObject(QThread):
    mySignal = pyqtSignal(int)

    # @pyqtSlot(int)
    def mySlot(self, value):
        print("Received value:", value)
    
    def run(self):
        print('ok')

if __name__ == '__main__':

    threads_1 = {}
    threads_2 = {}
    threads_1[1] = MyObject()
    threads_2[1] = DownloadThread(-1)
    print(threads_2[1].click_index)
    threads_1[1].mySignal.connect(threads_2[1].get_pause_download_signal)
    threads_1[1].mySignal.emit({
        "click_index":-1,
        "is_pause":True,
    })
# print(type(threads[1]))
# obj = MyObject().start()
# obj.mySignal.connect(obj.mySlot)
# obj.mySignal.emit(10)
# print(obj.mySignal.isSignalConnected(obj.mySlot)) # 输出False

# obj.mySignal.connect(obj.mySlot)
# print(obj.mySignal.isSignalConnected(obj.mySlot)) # 输出True

# obj.mySignal.disconnect(obj.mySlot)
# print(obj.mySignal.isSignalConnected(obj.mySlot)) # 输出False




 
# if __name__ == '__main__':
#     # test = TestClass()
#     # single_url = "https://www.bilibili.com/video/BV1cx4y1D7Vb/"
#     # test.test_get_single_url_info(single_url)
#     from PyQt5.QtCore import QObject, pyqtSignal




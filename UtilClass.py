# -*- coding: utf-8 -*-

from LogUtilClass import LogUtilClass, QMessageLogUtilClass
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from DownloadThreadClass import *
import os
import time
abs_dir = os.path.dirname(os.path.abspath(__file__))

class UtilClass(QThread):
    REFRESH_DOWNLOAD_LIST_FINISH_SIGNAL = pyqtSignal(int, list)
    SET_HORIZONTALLAYOUT_FINISH_SIGNAL = pyqtSignal(int, dict)
    ARRANGE_HORIZONTALLAYOUT_IN_DOWNLOADLIST = pyqtSignal(int, dict, list)
    REFRESH_SAVE_PATH_FINISH_SIGNAL = pyqtSignal(int,dict)
    send_temp_pause_download_signal = pyqtSignal(dict)  #通过将信号作为返回值传回主函数不知道行不行
    def __init__(self, index=None, options=None, horizontaldict=None, \
                download_list = None, thread_manager_dict = None, pause_download_signal=None,\
                save_dir = None):
        super(UtilClass, self).__init__()
        self.log = LogUtilClass()
        self.options = options
        self.index = index
        self.download_list = download_list
        self.horizontaldict = horizontaldict
        self.thread_manager_dict = thread_manager_dict
        self.pause_download_signal = pause_download_signal
        self.save_dir = save_dir
        self.quality_table_dict = {
            "16" : "360P",
            "32" : "480P",
            "64" : "720P",
            "80" : "1080P",
            "112" : "?",
            "120" : "?",
        }
        self.err_dict = {}
        # self.pause_download_signal = horizontaldict['send_signal_dict']['pause_download_signal']
        self.log.error(f"当前发射暂停信号为{self.send_temp_pause_download_signal}")
        
    
    def run(self):
        time.sleep(1)
        if self.options == "refresh_download_list":
            self.log.info("refresh_download_list开始")
            self.refresh_download_list(self.download_list)
        elif self.options == "arrange_horizontallayout_in_downloadlist":
            # self.log.info("arrange_horizontallayout_in_downloadlist开始")
            self.arrange_horizontallayout_in_downloadlist()
        elif self.options == "refresh_save_path":
            # time.sleep(5) 
            self.refresh_save_path(self.save_dir)
        elif self.options == "refresh_download_list":
            self.refresh_download_list(self.download_list)


    def set_horizontalLayout_child_objectname(self, horizontalDict):
        # self.log.debug("开始设置子控件objectname")
        this_layout_create_time = horizontalDict['this_horizontalLayout_create_time']
        index_in_download_list = horizontalDict['index_in_download_list']
        horizontalLayout = horizontalDict['this_horizontalLayout_layout_dict']['horizontalLayout']
        for index in range(horizontalLayout.count()):
            item = horizontalLayout.itemAt(index)
            widget_item = item.widget()
            old_object_name = widget_item.objectName().split('-')[0]
            widget_item.setObjectName(old_object_name + '-' + str(int(this_layout_create_time)) + '-' + str(index_in_download_list))
        return horizontalDict
    
    def refresh_download_list(self, download_list):
        self.log.debug("开始刷新download_list")
        index_in_download_list_arr = []
        for index, horizontalLayout in enumerate(download_list):
            pass #这里直接冒泡排序一下，根据['index_in_download_list']字段蓝排序，将download_list重新排序
            index_in_download_list_arr.append(horizontalLayout['index_in_download_list'])
        self.bubble_sort(index_in_download_list_arr, download_list)
        #然后按照从0到1从新编号
        for i in range(len(download_list)):
            download_list[i]['index_in_download_list'] = i
        #然后重新设置对象名
        for index, horizontalLayoutdict in enumerate(download_list):
            self.set_horizontalLayout_child_objectname(horizontalLayoutdict)
        #结束就发送结束信号
        self.REFRESH_DOWNLOAD_LIST_FINISH_SIGNAL.emit(self.index, download_list)
    
    #冒泡排序
    def bubble_sort(self, arr, download_list=[]):
        n = len(arr)
        # 遍历数组元素
        if download_list==[]:
            for i in range(n - 1):
                # 每次遍历将最大的元素移动到末尾
                for j in range(0, n - i - 1):
                    if arr[j] > arr[j + 1]:
                        # 交换元素
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
            return arr
        else:
            for i in range(n - 1):
                # 每次遍历将最大的元素移动到末尾
                for j in range(0, n - i - 1):
                    if download_list[j]['index_in_download_list'] > download_list[j + 1]['index_in_download_list']:
                        # 交换元素
                        download_list[j], download_list[j + 1] = download_list[j + 1], download_list[j]
            return download_list

    def arrange_horizontallayout_in_downloadlist(self, horizontaldict=None, download_list=None):
        #对horizontalLayout进行整理，包括提取关键信息
        pass
        self.log.info("arrange_horizontallayout_in_downloadlist开始")
        try:
            detail_download_info = self.horizontaldict['download_info_dict']
            # print(detail_download_info)
            title = detail_download_info['title']
            # self.log.warning(title)
            # self.log.warning(type(title))
            #进行一些去除不合法字符
            #忘了这里其实再DownloadThreadClass中已经做过了。
            bvid = detail_download_info['bvid']
            page = detail_download_info['page']
            download_video_url_list = detail_download_info['download_url_dict']['video_dw_url_list']
            download_audio_url_list = detail_download_info['download_url_dict']['audio_dw_url_list']
            #获取视频质量
            id_arr = []
            id_baseUrl_dict = {}
            for vdw in download_video_url_list:
                key_list = list(vdw.keys())
                if not 'id' in key_list:
                    return
                id_arr.append(int(vdw['id']))
                id_baseUrl_dict[str((vdw['id']))] = (vdw['baseUrl'])
            max_id = max(id_arr)
            best_id = max_id #最好的质量
            best_quality = self.quality_table_dict[str(best_id)]
            download_video_url = download_video_url_list[0]['baseUrl']
            download_audio_url = download_audio_url_list[0]['baseUrl']
            # print(download_audio_url_list)
            total_video_size = DownloadUtilClass().get_single_file_total_size(download_video_url)
            total_audio_size = DownloadUtilClass().get_single_file_total_size(download_audio_url)
            self.log.warning(f"需要下载的视频大小为{total_video_size}")
            self.log.warning(f"需要下载的音频大小为{total_audio_size}")
            total_size = total_video_size + total_audio_size
            # print(horizontaldict['save_dir'])
            # save_dir = horizontaldict['save_dir']
            save_dir = self.save_dir
            # save_path = os.path.join(abs_dir, title+'.mp4')
            save_path = os.path.join(save_dir, title+'.mp4')
            prime_download_info_dict = {
                "title":title,
                "bvid":bvid,
                "page":page,
                "best_quality":best_quality,
                "id_baseUrl_dict":id_baseUrl_dict,
                "download_video_url":download_video_url,
                "download_audio_url":download_audio_url,
                "total_video_size":total_video_size,
                "total_audio_size":total_audio_size,
                "total_size":total_size,
                "save_path":save_path,
            }
            self.horizontaldict['prime_download_info_dict'] = prime_download_info_dict
            #设置下载状态
            download_status_info_dict ={
                "is_Start" : False, #一旦is_Start为True,按钮就只会再pause and continue 之间切换
                "is_End":False,
                # "is_Paused":False,
                "is_Paused":True,
            }
            # self.log.warning(title)
            # self.log.warning(type(title))
            self.horizontaldict['download_status_info_dict'] = download_status_info_dict
            #设置再download_list中的index
            index_in_download_list = self.download_list.index(self.horizontaldict)
            self.horizontaldict['index_in_download_list'] = index_in_download_list
            #给horizonlayout设置下载线程。
            receive_signal_handler_func_dict = self.horizontaldict['receive_signal_handler_func_dict']
            # send_signal_dict = self.horizontaldict['send_signal_dict']
            # self.horizontaldict['send_signal_dict'] = self.pause_download_signal #将信号换一下，不知道行不行
            #链接进度条更新信号
            # time_stamp = time.time() #获取线程唯一标识
            #这里应该用horizontallayout的唯一标识才能对应上，注意这两个标识是不一样的，一个是用来标识线程，一个是用来对应horizonal和thread
            #好吧，好像用一个也可以
            horizontaldict_time_stamp= self.horizontaldict['this_horizontalLayout_create_time']

            #========================之前设置下载线程的信号和槽=======================
            # download_thread = DownloadThread(video_url=download_video_url, save_path=save_path,\
            #                                  click_index= horizontaldict_time_stamp, total_size=total_size)
            # download_thread.progressChanged.connect(receive_signal_handler_func_dict['get_update_progressbar_signal'])
            # #这里同样将download_thread放入thread_manager_dict
            # download_thread_dict = {}
            # download_thread_dict['options'] = "download_thread"
            # download_thread_dict['index'] = len(self.download_list)
            # download_thread_dict['thread'] = download_thread
            # download_thread_dict['url'] = download_video_url
            # download_thread_dict['timestamp'] = horizontaldict_time_stamp #唯一标识
            # self.thread_manager_dict[str(horizontaldict_time_stamp)+'-'+"download_thread"] = download_thread_dict
            # #链接自己的暂停和下载信号
            # self.log.info(f"开始绑定pause_download_signal")
            # # self.pause_download_signal = send_signal_dict['pause_download_signal']
            # self.send_temp_pause_download_signal.connect(download_thread.get_pause_download_signal)
            # # self.pause_download_signal.connect(download_thread.get_pause_download_signal)
            # self.log.info(f"绑定pause_download_signal成功")
            # self.horizontaldict['download_thread'] = download_thread
            #===================================================================

            #然后设置一下title_label和comboBox
            this_horizontalLayout_layout_dict = self.horizontaldict['this_horizontalLayout_layout_dict']
            title_label = this_horizontalLayout_layout_dict['title_label']
            comboBox = this_horizontalLayout_layout_dict['comboBox']
            title_label.setText(title)
            for key in id_baseUrl_dict.keys():
                # comboBox.addItem(id_baseUrl_dict[key]) 
                comboBox.addItem(self.quality_table_dict[str(key)])
            #同时设置最好质量为默认currentTexxt
            comboBox.setCurrentText(self.quality_table_dict[str(best_id)]) 
            #这里当前horizontal设置好了,接下来设置horizontal的子控件的objectname
            self.set_horizontalLayout_child_objectname(self.horizontaldict)
            #然后对download_list进行refresh一下
            self.refresh_download_list(self.download_list)
            #发送结束信号
            self.log.info("开始发送整理结束信号了")
            self.log.debug(f"当前传入thread_manager_dict中线程数量为: {len(self.thread_manager_dict)}")
            # self.log.info(f"当前传入thread_manager_dict: {self.thread_manager_dict}")
            self.ARRANGE_HORIZONTALLAYOUT_IN_DOWNLOADLIST.emit(self.index, self.horizontaldict, self.download_list)
            return
        except Exception as e:
            self.err_dict = {
                "arrange_info_err":e
            }
            self.horizontaldict['err_dict'] = self.err_dict
            self.log.warning("出现异常了, 开始发送整理结束信号了")
            self.log.warning(e)
            
            self.ARRANGE_HORIZONTALLAYOUT_IN_DOWNLOADLIST.emit(self.index, self.horizontaldict, self.download_list)
    
    #中转开始暂停下载信号
    def temp_pause_download_signal(self, pause_dict):
        # time.sleep(5)
        self.log.debug(f"我temp_pause_download_signal被点击了，获取暂停下载的信号, time_stamp:{self.index},点击按钮time_stamp:{pause_dict['click_index']}")
        if pause_dict['click_index'] == self.index:
            self.is_pasue = pause_dict['is_pause']
            self.log.info(f"匹配成功: time_stamp{self.index}")
            self.horizontaldict['download_thread'].start()
            #开始发送中转消息
            self.send_temp_pause_download_signal.emit(pause_dict)
            print(self.horizontaldict['download_thread'])
            print(self.pause_download_signal)

    #更新horizoongtallayout的save_dir
    def refresh_save_path(self, save_dir):
        try:
            for horizontallayout_dict in self.download_list:
                prime_download_info_dict = horizontallayout_dict['prime_download_info_dict']
                save_path = prime_download_info_dict['save_path']
                save_file_name = prime_download_info_dict['title'] + '.mp4'
                new_save_path = os.path.join(save_dir, save_file_name)
                prime_download_info_dict['save_path'] = new_save_path
            self.REFRESH_SAVE_PATH_FINISH_SIGNAL.emit(self.index, {}) #这里用index代表time_stamp
        except Exception as e:
            self.log.warning(f"刷新save_path失败, 原因: {e}")
            self.REFRESH_SAVE_PATH_FINISH_SIGNAL.emit(self.index, {"err_msg":e})
        return


if __name__ == '__main__':

    threads_1 = {}
    threads_2 = {}
    threads_1[1] = UtilClass()
    threads_2[1] = DownloadThread(-1)
    print(threads_2[1].click_index)
    threads_1[1].send_temp_pause_download_signal.connect(threads_2[1].get_pause_download_signal)
    threads_1[1].send_temp_pause_download_signal.emit({
        "click_index":-1,
        "is_pause":True,
    })

# if __name__ == '__main__':
#     # 测试排序算法
#     array = [64, 34, 25, 12, 22, 11, 90]
#     UtilClass().bubble_sort(array)
#     print("排序后的数组:", array)
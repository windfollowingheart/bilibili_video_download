from LogUtilClass import LogUtilClass
import os
from LogUtilClass import LogUtilClass, QMessageLogUtilClass
from PyQt5.QtCore import  pyqtSignal, QThread
from PyQt5.QtWidgets import *
# from DownloadUtilClass import DownloadThread, DownloadUtilClass


def get_trans_size(byte_size):
    """获取字节大小对应的中文描述信息"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']:
        if abs(byte_size) < 1024.0:
            return "%3.1f%s" % (byte_size, unit)
        byte_size /= 1024.0
        # return "%3.1f%s" % (byte_size, unit)
    LogUtilClass().warning("文件太大了!!!")
    return None

class ZhengliClass(QThread):
    finished = pyqtSignal(list)  #发送整理结束信号,返回下载线程List
    
    def __init__(self,get_update_progressbar_signal=None, pause_download_signal=None, get_download_finished_signal=None,\
                   save_dir="", is_pause_signal_list=[], title_label_list=[], combobox_list=[], download_thread_list=[],\
                      download_horizontalLayout_list=[], download_info_list=[]):
        super().__init__()
        self.get_update_progressbar_signal = get_update_progressbar_signal
        self.pause_download_signal = pause_download_signal
        self.get_download_finished_signal = get_download_finished_signal
        self.download_info_list = download_info_list
        self.download_thread_list = download_thread_list
        self.download_horizontalLayout_list = download_horizontalLayout_list
        self.combobox_list = combobox_list
        self.title_label_list = title_label_list
        self.is_pause_signal_list = is_pause_signal_list
        self.save_dir = save_dir
        self.DOWNLOADENCODE = "hev1.1.6.L120.90"  #确定下载视频编码
        # self.download_util = DownloadUtilClass()

    def zhengli(self):
        for index, per_thread in enumerate(self.download_thread_list):
            if per_thread == None:
                select_video_quality = ''
                title_label_text = ''
                #这里直接用数组索引找对应子控件
                title_label_text = self.title_label_list[index].text()
                select_video_quality = self.combobox_list[index].currentText()
                # 首先检查是否选择了保存路径
                self.log.info(f"{title_label_text}的保存路径:{self.save_dir}")
                if self.save_dir=='':
                    QMessageLogUtilClass().show("提示", "请选择保存路径")
                    return
                if select_video_quality == "360P":
                    download_video_quality = '16'
                elif select_video_quality == "480P":
                    download_video_quality = '32'
                elif select_video_quality == "720P":
                    download_video_quality = '64'
                elif select_video_quality == "1080P":
                    download_video_quality = '80'
                else:
                    pass
                #找视频下载url
                for i in self.download_horizontalLayout_list[index]['can_download_quality_list']:
                    if i['id'] == download_video_quality and i['codecs'] == self.DOWNLOADENCODE:
                        download_video_url = i['baseUrl']
                        break
                    else:
                        continue
                if not download_video_quality:
                    self.log.error("未找到下载视频的url")
                    return
                #找音频下载url
                download_audio_url = self.download_horizontalLayout_list[index]\
                    ['download_url_dict']['audio_dw_url_list'][0]['baseUrl']
                
                #确认保存文件路径
                save_path = os.path.join(self.save_dir,  title_label_text+'.mp4')
                
                #开始下载
                # self.start_or_pause_button_lsit[index].setText(new_button_text) #直接索引设置开始暂停按钮的文本
                #还要改一下self.is_pause_download_list 中的值
                self.is_pause_signal_list[index] = not self.is_pause_signal_list[index]
                #获取total_size
                download_file_type="video_and_audio"
                if download_file_type == "video_and_audio":
                    total_size = self.download_util.get_single_file_total_size(download_video_url) + \
                        self.download_util.get_single_file_total_size(download_audio_url)
                elif download_file_type == "video":
                    total_size = self.download_util.get_single_file_total_size(download_video_url)
                elif download_file_type == "audio":
                    total_size = self.download_util.get_single_file_total_size(download_audio_url)
                else:
                    pass
                #然后设置progress_label
                #暂时先不设置
                
                #判断是否有同名文件，以及是否选择覆盖
                if os.path.exists(save_path):
                    # user_choice = QMessageLogUtilClass().show("提示", "文件已存在，是否覆盖？", set_cancel_button=True)
                    # if user_choice==QMessageBox.Cancel:
                    #     #设置按钮内容
                    #     # self.start_or_pause_button_lsit[index].setText("开始下载")
                    #     return
                    # else:
                    #     #移除文件
                    os.remove(save_path)

        #         thread = DownloadThread(index, video_url=download_video_url, audio_url=download_audio_url,\
        #                                 save_video_path=save_path, save_audio_path=save_path.strip('mp4')+'mp3',\
        #                                 total_size=total_size, download_file_type="video_and_audio")
                
        #         thread.progressChanged.connect(self.get_update_progressbar_signal)

        #         #链接自己的暂停和下载信号
        #         self.pause_download_signal.connect(thread.get_pause_download_signal)
        #         #链接下载线程的结束信号到本函数中
        #         thread.finished.connect(self.get_download_finished_signal)
        #         print(len(self.download_thread_list))
        #         print(index)
        #         if len(self.download_thread_list) >= index+1:
        #             self.download_thread_list[index] = thread
        #         else:
        #             self.download_thread_list.append(thread)

        # self.finished.emit(self.download_thread_list)

    def ren(self):
        self.zhengli()




import logging
import os
import inspect
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets

# 设置根日志记录器的配置
logging.basicConfig(level=logging.INFO) #这个只能设置一次后续设置不生效了
#如果要保存到文件，可以使用以下方式
# test_save_util = TestLogUtilClass()
# test_save_utilt.test_save_log()
# save_path = 'example.log'
# logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s', \
#                     level=logging.DEBUG,\
#                     filename=save_path,\
#                     filemode='a')

abs_path = os.path.dirname(os.path.abspath(__file__))

class LogUtilClass():

    def __init__(self, log=None, *args):
        # logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO) #你们有定义方法啊
        self.log = log
        self.caller_frame = inspect.currentframe().f_back
        caller_filename = inspect.getframeinfo(self.caller_frame).filename
        self.caller_filename = os.path.basename(caller_filename)
        self.caller_lineno = inspect.getframeinfo(self.caller_frame).lineno



    '''
        这里，我们添加了一个新的log方法，它接受日志级别和消息作为参数。
        在该方法内部，我们使用inspect模块的currentframe函数获取调用者的帧对象，
        然后使用getframeinfo函数来获取调用者的文件名和行号。
    
    '''
    def log(self, level, msg):
        caller_frame = inspect.currentframe().f_back
        caller_filename = inspect.getframeinfo(caller_frame).filename
        caller_lineno = inspect.getframeinfo(caller_frame).lineno
        logging.log(level, f"{msg} ,在{caller_filename}中第{caller_lineno}行")

    def warning(self, msg):
        # print(msg)
        # print()
        current_line = inspect.currentframe().f_lineno
        # 获取当前 Python 文件的文件名
        current_py_file_name = os.path.basename(__file__)
        self.caller_frame = inspect.currentframe().f_back
        # self.caller_filename = inspect.getframeinfo(self.caller_frame).filename
        self.caller_lineno = inspect.getframeinfo(self.caller_frame).lineno
        # logging.warning(f"{msg} ,在{self.caller_filename}中第{self.caller_lineno}行")
        warn_msg = f"{msg} ,在{self.caller_filename}中第{self.caller_lineno}行"
        warn_msg = ColorAndStyleUtilClass.print_yellow_color_and_italic_style(warn_msg)
        logging.info(warn_msg)

    def error(self, msg):
        # print(msg)
        # print()
        current_line = inspect.currentframe().f_lineno
        # 获取当前 Python 文件的文件名
        self.current_py_file_name = os.path.basename(__file__)
        self.caller_frame = inspect.currentframe().f_back
        # self.caller_filename = inspect.getframeinfo(self.caller_frame).filename
        self.caller_lineno = inspect.getframeinfo(self.caller_frame).lineno
        # logging.error(f"{msg} ,在{self.caller_filename}中第{self.caller_lineno}行")
        error_msg = f"{msg} ,在{self.caller_filename}中第{self.caller_lineno}行"
        error_msg = ColorAndStyleUtilClass.print_red_color_and_italic_style(error_msg)
        logging.info(error_msg)

    def info(self, msg):
        # print(msg)
        # print()
        current_line = inspect.currentframe().f_lineno
        # 获取当前 Python 文件的文件名
        current_py_file_name = os.path.basename(__file__)
        self.caller_frame = inspect.currentframe().f_back
        # caller_filename = inspect.getframeinfo(caller_frame).filename
        self.caller_lineno = inspect.getframeinfo(self.caller_frame).lineno
        # logging.info(f"{msg} ,在{self.caller_filename}中第{self.caller_lineno}行")
        info_msg = f"{msg} ,在{self.caller_filename}中第{self.caller_lineno}行"
        info_msg = ColorAndStyleUtilClass.print_green_color_and_italic_style(info_msg)
        logging.info(info_msg)

    def debug(self, msg):
        # print(msg)
        # print()
        current_line = inspect.currentframe().f_lineno
        # 获取当前 Python 文件的文件名
        current_py_file_name = os.path.basename(__file__)
        self.caller_frame = inspect.currentframe().f_back
        # caller_filename = inspect.getframeinfo(caller_frame).filename
        self.caller_lineno = inspect.getframeinfo(self.caller_frame).lineno
        debug_msg = f"{msg} ,在{self.caller_filename}中第{self.caller_lineno}行"
        debug_msg = ColorAndStyleUtilClass.print_blue_color_and_italic_style(debug_msg)
        logging.info(debug_msg)


class QMessageLogUtilClass():
    pass
    def __init__(self, set_cancel_button=None) -> None:
        self.set_cancel_button = set_cancel_button
        pass
        
    def show(self, title, msg, set_cancel_button=False, size=[]):
        if not self.set_cancel_button or self.set_cancel_button !=None:
            set_cancel_button = self.set_cancel_button
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QtGui.QIcon(os.path.join(abs_path, "icon.png")))
        msg_box.setWindowTitle(str(title))
        msg_box.setText(str(msg))
        msg_box.setIcon(QMessageBox.Information)
        # msg_box.setIcon(QtGui.QIcon(os.path.join(abs_path, "icon.png")))
        # 添加按钮
        if size != []:
            LogUtilClass().debug("重设大小")
            msg_box.setFixedSize(size[0], size[1])
        if set_cancel_button:
            msg_box.addButton(QMessageBox.Cancel)
            msg_box.addButton(QMessageBox.Ok)
        # msg_box.addButton(QMessageBox.Ok)
        # msg_box.addButton(QMessageBox.Cancel)
        # 执行消息框，并获取用户的选择
        user_choice = msg_box.exec_()

        # 根据用户选择进行相应的操作
        if user_choice == QMessageBox.Ok:
            # print("用户点击了确定按钮")
            LogUtilClass().info("用户点击了确定按钮")
        else:
            # print("用户点击了取消按钮")
            LogUtilClass().info("用户点击了取消按钮")
        return user_choice

class ConsoleColors:
    # ANSI转义序列，用于设置文本颜色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET_COLOR = '\033[0m'  # 重置文本颜色

class ConsoleStyles:
    # ANSI转义序列，用于设置文本样式
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    RESET_STYLE = '\033[0m'  # 重置文本样式


class ColorAndStyleUtilClass:
    # ANSI转义序列，用于设置文本颜色和样式
    def print_red_color_and_italic_style(msg):
        return (ConsoleColors.RED + ConsoleStyles.ITALIC + msg + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)
    def print_yellow_color_and_italic_style(msg):
        return (ConsoleColors.YELLOW + ConsoleStyles.ITALIC + msg + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)
    def print_green_color_and_italic_style(msg):
        return (ConsoleColors.GREEN + ConsoleStyles.ITALIC + msg + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)
    def print_blue_color_and_italic_style(msg):
        return (ConsoleColors.BLUE + ConsoleStyles.ITALIC + msg + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)
    

    # def print_red_color_and_bold_style(color, style, msg):
    #     print(color + style + msg + ColorAndStyleUtilClass.RESET_COLOR)
    # def print_red_color_and_bold_style(color, style, msg):
    #     print(color + style + msg + ColorAndStyleUtilClass.RESET_COLOR)
    # def print_red_color_and_bold_style(color, style, msg):
    #     print(color + style + msg + ColorAndStyleUtilClass.RESET_COLOR)
    # def print_red_color_and_bold_style(color, style, msg):
    #     print(color + style + msg + ColorAndStyleUtilClass.RESET_COLOR)
    # def print_color(color, msg):
    #     print(color + msg + ColorAndStyleUtilClass.RESET_COLOR)
    # def print_style(style, msg):
    #     print(style + msg + ColorAndStyleUtilClass.RESET_COLOR)
    # def print_color_and_style_and_reset(color, style, msg):

class TestLogUtilClass:
    def __init__(self):
        self.log = LogUtilClass()
    def test_print_style(self):
        # 示例用法
        self.log.print_style(ColorAndStyleUtilClass.BOLD_STYLE, "bold")
        self.log.print_style(ColorAndStyleUtilClass.UNDERLINE_STYLE, "underline")
        self.log.print_style(ColorAndStyleUtilClass.REVERSE_STYLE, "reverse")
        
    
    def test_set_form(self):
        # 配置日志输出的格式和级别
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        # 记录日志
        logging.debug("这是一个调试信息")
        logging.info("这是一个信息日志")
        logging.warning("这是一个警告日志")
        logging.error("这是一个错误日志")
        logging.critical("这是一个严重错误日志")
    def test_save_log(self, save_path = 'test.log'):
        # # 配置日志输出的格式和级别
        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     format='%(asctime)s - %(levelname)s - %(message)s',
        #     filename='logfile.log',  # 指定日志文件路径
        #     filemode='a'  # 使用追加模式写入日志文件，默认是覆盖模式
        # )
        logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s', \
                    level=logging.DEBUG,\
                    filename=save_path,\
                    filemode='a')


        # 记录日志
        logging.debug("这是一个调试信息")
        logging.info("这是一个信息日志")
        logging.warning("这是一个警告日志")
        logging.error("这是一个错误日志")
        logging.critical("这是一个严重错误日志")

def test_style():
    # 示例用法
    print(ConsoleStyles.BOLD + "加粗文本" + ConsoleStyles.RESET_STYLE)
    print(ConsoleStyles.ITALIC + "斜体文本" + ConsoleStyles.RESET_STYLE)
    print(ConsoleStyles.UNDERLINE + "下划线文本" + ConsoleStyles.RESET_STYLE)

def test_color():
    # 示例用法
    print(ConsoleColors.RED + "红色文本" + ConsoleColors.RESET_COLOR)
    print(ConsoleColors.GREEN + "绿色文本" + ConsoleColors.RESET_COLOR)
    print(ConsoleColors.BLUE + "蓝色文本" + ConsoleColors.RESET_COLOR)

def test_color_and_style():
    # 示例用法
    print(ConsoleColors.RED + ConsoleStyles.BOLD + "红色加粗文本" + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)
    print(ConsoleColors.YELLOW + ConsoleStyles.BOLD + "黄色加粗文本" + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)
    print(ConsoleColors.YELLOW + ConsoleStyles.ITALIC + "绿色斜体文本" + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)
    print(ConsoleColors.BLUE + ConsoleStyles.UNDERLINE + "蓝色下划线文本" + ConsoleStyles.RESET_STYLE + ConsoleColors.RESET_COLOR)

def test_save_log_1():
    pass
    testuitl = TestLogUtilClass()
    testuitl.test_save_log()

if __name__ == '__main__':
    test_save_log_1()

import re
import time
import difflib
import win32gui
import win32api
import win32con


def replace_chinese(file):
    """去除字符串中的中文"""
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    chinese = re.sub(pattern, '', file)
    return chinese


def stri_similar(s1, s2):
    """比较两个字符串的相似度"""
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def left_click_position(hwd, x_position, y_position, sleep_time):
    """鼠标左点击"""
    # 将两个16位的值连接成一个32位的地址坐标
    long_position = win32api.MAKELONG(x_position, y_position)
    # 点击左键
    win32api.SendMessage(hwd, win32con.WM_LBUTTONDOWN,
                         win32con.MK_LBUTTON, long_position)
    win32api.SendMessage(hwd, win32con.WM_LBUTTONUP,
                         win32con.MK_LBUTTON, long_position)
    time.sleep(sleep_time)


def get_mouse_position():
    """获取鼠标位置"""
    return win32api.GetCursorPos()

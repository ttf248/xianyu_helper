# https://github.com/xzkzdx/WeChatPC/blob/cde6285798fc0e0b424808308f2655db6bd9cfe1/examples/wechat_windows.py

import cv2
import win32gui
import win32api
import win32con
import time
import win32clipboard
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
import numpy as np


def find_hwd(class_name, window_name):
    """获取句柄"""
    return win32gui.FindWindow(class_name, window_name)


def get_window_pos(hwnd):
    """获取窗口位置"""
    return win32gui.GetWindowRect(hwnd)


def right_click_position(hwd, x_position, y_position, sleep_time):
    """鼠标右点击"""
    # 将两个16位的值连接成一个32位的地址坐标
    long_position = win32api.MAKELONG(x_position, y_position)
    # 点击左键
    win32api.SendMessage(hwd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, long_position)
    win32api.SendMessage(hwd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, long_position)
    time.sleep(int(sleep_time))


def left_click_position(hwd, x_position, y_position, sleep_time):
    """鼠标左点击"""
    # 将两个16位的值连接成一个32位的地址坐标
    long_position = win32api.MAKELONG(x_position, y_position)
    # 点击左键
    win32api.SendMessage(hwd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
    win32api.SendMessage(hwd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)
    time.sleep(sleep_time)


def get_text_from_clipboard():
    """读取剪切板"""
    win32clipboard.OpenClipboard()
    d = win32clipboard.GetClipboardData(win32con.CF_TEXT)
    win32clipboard.CloseClipboard()
    return d.decode('gbk')


def set_text_to_clipboard(string):
    """写入剪切板"""
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_TEXT, string.encode(encoding='gbk'))
    win32clipboard.CloseClipboard()


def get_mouse_position():
    """获取鼠标位置"""
    return win32api.GetCursorPos()


def set_mouse_position(x_position, y_position):
    """设置鼠标位置"""
    return win32api.SetCursorPos((x_position, y_position))


def input_content(hwd, content, sleep_second):
    """粘贴到消息发送框"""
    # 存入粘贴板
    set_text_to_clipboard(content)
    # 鼠标右键调 WeChatMainWndForPC 的 CMenuWnd 粘贴板
    right_click_position(hwd, 400, 500, 0.1)
    time.sleep(sleep_second)
    # 获取 CMenuWnd 粘贴板句柄
    CMenuWnd = win32gui.FindWindow("CMenuWnd", "CMenuWnd")
    # 鼠标左击粘贴
    left_click_position(CMenuWnd, 20, 10, 0.1)
    # click_combination_keys(hwd, win32con.VK_CONTROL, win32con.VK_RETURN)


def click_single_key(hwd, key):
    """模拟键盘独立按键"""
    win32api.SendMessage(hwd, win32con.WM_KEYDOWN, key, 0)
    win32api.SendMessage(hwd, win32con.WM_KEYUP, key, 0)


def click_multi_keys(hwd, *key):
    """模拟键盘多个独立按键"""
    for k in key:
        click_single_key(hwd, k)


def click_combination_keys(hwd, *args):
    """模拟键盘组合按键"""
    for arg in args:
        win32api.SendMessage(hwd, win32con.WM_SYSKEYDOWN, arg, 0)
    for arg in args:
        win32api.SendMessage(hwd, win32con.WM_SYSKEYUP, arg, 0)


def capture(handle: HWND):
    """窗口客户区截图

    Args:
        handle (HWND): 要截图的窗口句柄

    Returns:
        numpy.ndarray: 截图数据
    """

    GetDC = windll.user32.GetDC
    CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
    GetClientRect = windll.user32.GetClientRect
    CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
    SelectObject = windll.gdi32.SelectObject
    BitBlt = windll.gdi32.BitBlt
    SRCCOPY = 0x00CC0020
    GetBitmapBits = windll.gdi32.GetBitmapBits
    DeleteObject = windll.gdi32.DeleteObject
    ReleaseDC = windll.user32.ReleaseDC

    # 排除缩放干扰
    windll.user32.SetProcessDPIAware()

    # 获取窗口客户区的大小
    r = RECT()
    GetClientRect(handle, byref(r))
    width, height = r.right, r.bottom
    # 开始截图
    dc = GetDC(handle)
    cdc = CreateCompatibleDC(dc)
    bitmap = CreateCompatibleBitmap(dc, width, height)
    SelectObject(cdc, bitmap)
    BitBlt(cdc, 0, 0, width, height, dc, 0, 0, SRCCOPY)
    # 截图是BGRA排列，因此总元素个数需要乘以4
    total_bytes = width*height*4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte*total_bytes
    GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
    DeleteObject(bitmap)
    DeleteObject(cdc)
    ReleaseDC(handle, dc)
    # 返回截图数据为numpy.ndarray
    return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)


if __name__ == "__main__":
    
    handle = find_hwd("HLBRMainUI", "火绒安全软件")
    image = capture(handle)
    cv2.imshow("Capture Test", image)
    cv2.waitKey()
from PIL import ImageGrab, Image
import easyocr
import re
import os
import json
import difflib
import time
import win32gui
import win32api
import win32con
import cv2
import numpy as nm
from datetime import datetime


def stri_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def find_chinese(file):
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    chinese = re.sub(pattern, '', file)
    return chinese


def read_ans(file_name):

    with open('data/' + file_name, 'r', encoding="utf-8") as f:
        ans = []
        content = f.read()
        content = content.split("\n")

        for item in content:
            try:
                js = json.loads(item)

                if js['ans'] == 'A':
                    js['ans'] = js['a'][0]
                if js['ans'] == 'B':
                    js['ans'] = js['a'][1]

                ans.append(js)
            except Exception as e:
                print(e)
        return ans

def left_click_position(hwd, x_position, y_position, sleep_time):
    """鼠标左点击"""
    # 将两个16位的值连接成一个32位的地址坐标
    long_position = win32api.MAKELONG(x_position, y_position)
    # 点击左键
    win32api.SendMessage(hwd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
    win32api.SendMessage(hwd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)
    time.sleep(sleep_time)

def get_mouse_position():
    """获取鼠标位置"""
    return win32api.GetCursorPos()

if __name__ == '__main__':

    #time.sleep(5)
    #print(get_mouse_position())

    classname = "Chrome_WidgetWin_0"
    titlename = "咸鱼之王"
    # 获取句柄
    hwnd = win32gui.FindWindow(classname, titlename)

    ans = read_ans('ans.txt')

    reader = easyocr.Reader(['ch_sim', 'en'])

    img_old = ImageGrab.Image
    question_str_old = ""

    while True:
         # 获取窗口左上角和右下角坐标
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        print("识别到小程序位置：", left, top, right, bottom)
        # 截取题目
        img = ImageGrab.grab(
            bbox=(left+25, top+141, left+25 + 419, top+141 + 130))
        
        # 计算关卡位置
        (x1,y1) = win32gui.ClientToScreen(hwnd, (204, 182))
        (x2,y2) = win32gui.ClientToScreen(hwnd, (398, 224))
        print(x1, y1, x2, y2)
        
        game_level = 0
        time_start = datetime.now()

        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        result = reader.readtext(cv2.cvtColor(nm.array(img), cv2.COLOR_BGR2GRAY))
        if len(result) > 0:
            game_level = result[0][1]
            print("启动脚本，检测当前关卡：", game_level)

        loop_count = 0
        while True:
            loop_count = loop_count + 1
            if loop_count % 1000 == 0:
                img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                result = reader.readtext(cv2.cvtColor(nm.array(img), cv2.COLOR_BGR2GRAY))
                if len(result) > 0 and result[0][1] != game_level:
                    game_level = result[0][1]
                    time_consume = (datetime.now() - time_start)
                    time_start = datetime.now()
                    print("检测到关卡变动：{}, 耗时：{}".format(game_level, time_consume))

            left_click_position(hwnd, 299, 783, 0.01)

        # print(img.mode)
        # print(range(img.width), range(img.height))

        for i in range(img.width):
            for j in range(img.height):
                try:
                    r, g, b = img.getpixel((i, j))
                    color_set = [[48, 48, 48, 32], [82, 31, 26, 40]]
                    for color in color_set:
                        if color[0] - color[3] < r < color[0] + color[3] and color[1] - color[3] < g < color[1] + color[3] and color[2] - color[3] < b < color[2] + color[3]:
                            img.putpixel((i, j), (0, 0, 0))
                            break
                        else:
                            img.putpixel((i, j), (255, 255, 255))
                except Exception as e:
                    print(e)
                    continue

        if img != img_old:
            img_old = img
            img.save('tmp.jpg')

            question_str = ""

            result = reader.readtext('tmp.jpg')

            for item in result:
                # question_str += find_chinese(item[1])
                question_str += item[1] + ""

            question_str = question_str.replace(" ", "")

            if question_str != question_str_old:
                question_str_old = question_str
                max = 0.4
                result = {}

                for item in ans:
                    ret = stri_similar(question_str, item['q'])
                    if ret > max:
                        max = ret
                        result = item

                if max > 0.4:
                    file_name = time.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
                    img.save(file_name)

                    print(question_str)
                    print(max, result, result['ans'])
                    if (result['ans'] == '对'):
                        win32api.SetCursorPos([left+166, top+930])
                        win32api.mouse_event(
                            win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.01)
                        win32api.mouse_event(
                            win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

                    if (result['ans'] == '错'):
                        win32api.SetCursorPos([left+422, top+923])
                        win32api.mouse_event(
                            win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.01)
                        win32api.mouse_event(
                            win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

            time.sleep(0.2)

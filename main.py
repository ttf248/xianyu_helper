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


def stri_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def find_chinese(file):
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    chinese = re.sub(pattern, '', file)
    return chinese


def read_ans(file_name):
    
    with open(file_name, 'r', encoding="utf-8") as f:
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


if __name__ == '__main__':
    dms = ctypes.windll.LoadLibrary(r'G:\python\xianyu_helper\RegDll.dll')

    dms.SetDllPathW(r'data/dm.dll', 0)
    dm = CreateObject('dm.dmsoft')
    print(dm.Ver())

    print(stri_similar('咸鱼之王里宝箱积分达分时可一键领取累计积分奖励宝箱',
          '《咸鱼之王》里宝箱积分达1000分时，可一键领取累计积分奖励宝箱。'))

    classname = "Chrome_WidgetWin_0"
    titlename = "咸鱼之王"
    # 获取句柄
    hwnd = win32gui.FindWindow(classname, titlename)
    # 获取窗口左上角和右下角坐标
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    print("识别到小程序位置：", left, top, right, bottom)
    print(left+25, top+141, left+25 + 419, top+141 + 130)

    ans = read_ans('ans.txt')

    # max = -1
    # result = {}
    # for item in ans:
    #     ret = stri_similar('兄融夫人是《三国演义》虚构人8勿。', item['q'])
    #     if ret > max:
    #         max = ret
    #         result = item
    # print(result)

    reader = easyocr.Reader(['ch_sim', 'en'])

    img_old = ImageGrab.Image
    question_str_old = ""

    while True:
        img = ImageGrab.grab(bbox=(left+25, top+141, left+25 + 419, top+141 + 130))

        # print(img.mode)
        # print(range(img.width), range(img.height))

        for i in range(img.width):
            for j in range(img.height):
                try:
                    r,g,b = img.getpixel((i,j))
                    color_set = [[48, 48, 48, 32],[82,31,26,40]]
                    for color in color_set:
                        if color[0] - color[3] < r < color[0] + color[3] and color[1] - color[3] < g < color[1] + color[3] and color[2] - color[3] < b < color[2] + color[3]:
                            img.putpixel((i,j), (0, 0, 0))
                            break
                        else:
                            img.putpixel((i,j), (255, 255, 255))
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
                    print("=================pytesseract========================")
                    tmp = pytesseract.image_to_string(Image.open('tmp.jpg'), lang='chi_sim')
                    tmp = tmp.replace("\n", "").replace(" ", "")
                    print(tmp)
                    print("=================easyocr========================")
                    print(question_str)
                    print(max, result, result['ans'])
                    # if(result['ans'] == '对'):
                    #     win32api.SetCursorPos([left+166,top+930])
                    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    #     time.sleep(0.01)
                    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

                    # if(result['ans'] == '错'):
                    #     win32api.SetCursorPos([left+422,top+923])
                    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    #     time.sleep(0.01)
                    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

            time.sleep(0.2)

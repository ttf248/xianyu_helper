import re
import os
import cv2
import time
import difflib
import windows
import win32gui
import easyocr
import numpy as np
from loguru import logger
from PIL import ImageGrab, Image, ImageDraw, ImageFont



def replace_chinese(file):
    """去除字符串中的中文"""
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    chinese = re.sub(pattern, '', file)
    return chinese


def stri_similar(s1, s2):
    """比较两个字符串的相似度"""
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


class Utils():
    def __init__(self, ocr_reader):
        # debug开关（开启后，成功匹配会弹出图片，上面用圈标明了匹配到的坐标点范围）；尝试 OCR 识别
        self.debug = True
        # 咸鱼之王不支持按照句柄截图，前台窗口截图
        self.capture_method = "foreground"
        # 计数
        self.cnt = 0
        # 分辨率相关
        self.screen_height = 2560
        self.screen_width = 1440
        self.scale_percentage = 100
        # 图像匹配阈值
        self.threshold = 0.90
        # 全局句柄
        self.hwnd = windows.find_hwd("Chrome_WidgetWin_0", "咸鱼之王")
        # 窗口坐标
        self.left, self.top, self.right, self.bottom = 0, 0, 0, 0
        # 获取窗口左上角和右下角坐标
        self.left, self.top, self.right, self.bottom = windows.get_window_pos(self.hwnd)
        logger.info("咸鱼之王屏幕坐标：{} {} {} {}", self.left, self.top, self.right, self.bottom)
        # 设置为前台
        win32gui.SetForegroundWindow(self.hwnd)
        # 公用OCR，初始化太慢
        self.reader = ocr_reader

    # 加载图像资源, 返回图像资源列表; 图像都是通过Sniff截图，保持图片画质稳定
    def load_res(self):
        # 匹配对象的字典
        self.res = {}
        file_dir = os.path.join(os.getcwd(), "data")
        temp_list = os.listdir(file_dir)
        for item in temp_list:
            if item.endswith(".bmp"):
                self.res[item] = {}
                res_path = os.path.join(file_dir, item)
                # 路径包含中文无法使用cv2.imread读取
                # self.res[item]["img"] = cv2.imread(res_path)
                self.res[item]["img"] = cv2.imdecode(np.fromfile(res_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                # 图片读取失败
                if self.res[item]["img"] is None:
                    logger.warning(f"图片{item}读取失败")
                    continue
                # 如果不是原尺寸（1440P），进行对应缩放操作
                if self.scale_percentage != 100:
                    self.res[item]["width"] = int(self.res[item]["img"].shape[1] * self.scale_percentage / 100) 
                    self.res[item]["height"] = int(self.res[item]["img"].shape[0] * self.scale_percentage / 100)
                    self.res[item]["img"] = cv2.resize(self.res[item]["img"], (self.res[item]["width"], self.res[item]["height"]), interpolation=cv2.INTER_AREA)
                else:
                    self.res[item]["height"], self.res[item]["width"], self.res[item]["channel"] = self.res[item]["img"].shape[::]

                
    # 获取截图
    def get_img(self, pop_up_window=False, save_img=False, file_name='screenshot.png'):
        if self.capture_method == "foreground":
            # 前台窗口截图
            image_bytes = ImageGrab.grab(bbox=(self.left, self.top, self.right, self.bottom))
        else:
            image_bytes = windows.capture(self.hwnd)

        image_bytes = np.array(image_bytes, dtype=np.uint8)
        if image_bytes.size == 0:
            logger.warning("截图失败，检查窗口是否被遮挡")
        else:
            self.target_img = image_bytes
            if save_img:
                cv2.imwrite(file_name, self.target_img)
            if pop_up_window:
                self.show_img()

                

    def cv2ImgAddText(self, img, text, left, top, textColor=(0, 255, 0), textSize=20):
        if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # 创建一个可以在给定图像上绘图的对象
        draw = ImageDraw.Draw(img)
        # 字体的格式
        fontStyle = ImageFont.truetype(
            "data/simsun.ttc", textSize, encoding="utf-8")
        # 绘制文本
        draw.text((left, top), text, textColor, font=fontStyle)
        # 转换回OpenCV格式
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


    # 展示图片
    def show_img(self):
        img = self.target_img        
        if self.debug:
            # 统计耗时
            start = time.time()
            result = self.reader.readtext(img)
            end = time.time()
            logger.debug("OCR耗时：{}ms", (end - start) * 1000)
            spacer = 100
            for detection in result:
                top_left = tuple(detection[0][0])
                bottom_right = tuple(detection[0][2])
                text = detection[1]
                img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),1)
                img = self.cv2ImgAddText(img, text, 100, 100 + spacer)
                spacer+=20
        
        #cv2.namedWindow("screenshot", cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('screenshot', 360, 640)
        cv2.imshow("screenshot", img)
        cv2.waitKey()


if __name__ == '__main__':
    utils = Utils(easyocr.Reader(['ch_sim', 'en']))
    utils.load_res()
    utils.get_img(pop_up_window=True)

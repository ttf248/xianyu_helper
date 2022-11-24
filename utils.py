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

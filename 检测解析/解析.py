# -*- coding: utf-8 -*-
import random
import sqlite3
from 彩虹屁.语料库 import girl_ls
from wxauto import WeChat
from datetime import datetime
import time
import re
from DrissionPage import ChromiumPage, ChromiumOptions, WebPage
from DownloadKit import DownloadKit
import time
import os
import requests
import re

wx = WeChat()


class VideoAnalyze:
    """
    解析视频下载到本地。

    主要应用于不可下载视频的解析，可自动识别内容，下载后自动转发。
    """

    def __init__(self):
        co = ChromiumOptions()
        co.headless()  # 无头模式
        # co.set_argument('--window-position=-32000,-32000')  # 白屏问题：因浏览器版本原因，升级chrome至130没有白屏，或用临时解决方法使窗口生成在不可见区域。
        # co = co.set_argument('--no-sandbox')  # linux使用，解决$DISPLAY报错,linux只需要运行一次，运行后注释掉。
        co.no_imgs(True)  # 设置不加载图片
        co.mute(True)  # 静音
        self.page = ChromiumPage(co)

    def listen_url(self, url, video_name):
        print(f'打开网页: {url}')
        self.page.listen.start(targets=r'.*douyinvod.*', is_regex=True, )  # 以正则关键字监听视频链接
        self.page.get(url)
        print('等待视频加载，监听网页……')
        while True:
            res = self.page.listen.wait(timeout=10)
            self.page.refresh()
            if res:
                break

        video_url = res.url
        print('取得视频链接，下载中……')
        # 下载视频
        d = DownloadKit(r'.\抖音视频提取')  # 创建下载器对象
        d.download(video_url, rename=video_name, suffix='mp4', show_msg=True, file_exists='rename')
        # 当前所在路径
        print(f'下载完成。')
        self.page.quit()

    def extract_url(self, text):
        """从用户输入中提取抖音分享链接"""
        try:
            # 使用正则匹配链接部分
            url = re.search(r'https://v\.douyin\.com/\S+', text).group(0).strip('/')
            return url
        except AttributeError:
            return None

    def run(self, text, video_name):
        """程序入口"""
        url = self.extract_url(text)
        self.listen_url(url, video_name)


def rainbow_group(group):
    """
    监听群消息，并保存到SQLite数据库（实时保存，每条消息即刻写入）

    Args:
        group(str): 群名
    """
    wx.AddListenChat(who=group, savepic=False)  # 添加监听对象并且自动保存新消息图片
    Me = "清易"

    while True:
        msgs = wx.GetListenMessage()  # 获取监听到的消息
        for chat in msgs:  # chat 是一个带有聊天名称的 uia提示
            chat_name = str(chat)  # 转换群名为字符串，防止存储错误
            one_msgs = msgs.get(chat)
            for msg in one_msgs:
                ds = {}
                ds['记录日期'] = datetime.now().strftime("%Y-%m-%d")
                ds['群名'] = chat_name  # 将群名转换为字符串存储
                ds['内容类型'] = msg.type  # 需要清洗处理时另外写，这里取原始数据
                ds['发言者'] = Me if msg[0] == "Self" else msg[0]
                ds['发言内容'] = msg[1]
                ds['发言时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 使用正则匹配链接部分
                text = ds['发言内容']
                now = datetime.now().strftime("%Y%m%d%H%M%S")
                video_name = f'dy_{now}'
                try:
                    url = re.search(r'https://v\.douyin\.com/\S+', text).group(0).strip('/')
                    # 检测到符合条件的url时，自动解析并发送视频
                    if url:
                        VideoAnalyze().run(text, video_name)
                        # 发送视频
                        # files = [rf'D:\Code\wxauto\检测解析\抖音视频提取\dy_20241021172900.mp4', ]
                        path = os.path.join(os.getcwd(), '抖音视频提取', f'{video_name}.mp4')
                        # files = [rf'D:\Code\wxauto\检测解析\抖音视频提取\{video_name}.mp4', ]
                        files = [path, ]
                        wx.SendFiles(filepath=files, who=group)
                        # @某人并发送消息
                        at = ds['发言者']
                        msg = ' 视频已解析。'
                        wx.SendMsg(msg=msg, who=group, at=at)
                except Exception as e:
                    print(rf'非视频内容，跳过：{text}')
                    time.sleep(5)


rainbow_group('测试群wxauto')
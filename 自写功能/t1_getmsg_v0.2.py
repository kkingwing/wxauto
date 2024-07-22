# -*- coding: utf-8 -*-
# v0.2 清洗文本，加入ods、dw逻辑
# v0.1 基本功能实现

"""
记录微信消息
"""

from wxauto import WeChat
from datetime import datetime
import time
import pandas as pd
from sqlalchemy import create_engine
from config import CON
import re

import pymysql

pymysql.install_as_MySQLdb()

wx = WeChat()


# 一、功能： 聊天消息记录， 自动处理，调用excel宏生成分析图

# wx.ChatWith("wxauto交流")
# g1 = wx.CurrentChat() # 获取当前窗口名

def df2sql(df, save_type, save_name):
    """
    保存到数据库，根据指定的存储类型 ods|dw

    Args:
        df(DataFrame): 数据
        save_type(str): ods/dw
        save_name(str): 表名
    """
    engine = create_engine(CON)
    if save_type == "ods":
        df.to_sql(rf'ods_{save_name}', con=engine, if_exists='append', index=False)
    else:
        print("请输入正确的保存类型")


def listen_group(groups):
    """
    监听群消息，并保存到数据库

    Args:
        groups(list): 群名列表，不可监测企微群
    """
    for i in groups:
        wx.AddListenChat(who=i, savepic=False)  # 添加监听对象并且自动保存新消息图片

    wait = 20  # 设置20秒查看一次是否有新消息
    Me = "清易"
    CACHE_NUMBER = 5  # 这是「缓存的消息条数」超过这个数就将缓存写到数据库中.
    ls = []
    while True:
        msgs = wx.GetListenMessage()  # 这一句会先取原有的聊天内容，根据上下的聊天内容判断消耗新id是否为新
        for chat in msgs:  # chat 是一个带有聊天名称的 uia提示
            one_msgs = msgs.get(chat)  # 获取消息内容,one_msgs[0] # 说话者/时间/系统提示  one_msgs[1] 说话内容
            for msg in one_msgs:
                ds = {}
                ds['记录日期'] = datetime.now().strftime("%Y-%m-%d")
                ds['群名'] = chat  # listen_list[0]  # 暂时用这个方法
                ds['内容类型'] = msg.type  # 需要清洗处理时另外写，这里取原始数据
                ds['发言者'] = Me if msg[0] == "Self" else msg[0]  # 如果是自己说话，使用名称替换
                ds['发言内容'] = msg[1]
                ds['发言时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 误差约有{wait}秒
                # chat.SendMsg('收到')  # 回复收到
                print(ds)
                ls.append(ds)
                # 写入数据库
                if len(ls) >= CACHE_NUMBER:  # 这是「缓存的消息条数」超过这个数就将缓存写到数据库中.
                    df = pd.DataFrame(ls)
                    print(f'缓存消息大于 {CACHE_NUMBER} 条,df写入sql：\n{df}\n')
                    df2sql(df, save_type="ods", save_name="wxauto_wechat_msgs")
                    ls = []  # 重置列表为
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now} 缓存条数：{len(ls)}")
        time.sleep(wait)


# 不可监测企微群
# 免打扰也可获得内容
groups = ["wxauto交流", "天麒的高端会所群", "wxauto三群"]  #
listen_group(groups)

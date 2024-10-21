# -*- coding: utf-8 -*-
import random
import sqlite3
from 彩虹屁.语料库 import girl_ls
from wxauto import WeChat
from datetime import datetime
import time
import re

wx = WeChat()

# Database setup
DB_PATH = 'wechat_msgs.db'


def create_table_if_not_exists(conn):
    """
    Create table if it doesn't exist in the SQLite database.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS wxauto_wechat_rainbow (
        记录日期 TEXT,
        群名 TEXT,
        内容类型 TEXT,
        发言者 TEXT,
        发言内容 TEXT,
        发言时间 TEXT,
        夸奖内容 TEXT
    );
    """
    conn.execute(create_table_sql)


def insert_record(conn, record):
    """
    插入单条记录到本地SQLite数据库
    Args:
        conn: SQLite连接
        record: 字典格式的记录
    """
    insert_sql = """
    INSERT INTO wxauto_wechat_rainbow 
    (记录日期, 群名, 内容类型, 发言者, 发言内容, 发言时间, 夸奖内容) 
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    values = (
        record['记录日期'],
        record['群名'],
        record['内容类型'],
        record['发言者'],
        record['发言内容'],
        record['发言时间'],
        record.get('夸奖内容', None)  # 可能没有夸奖内容
    )
    conn.execute(insert_sql, values)
    conn.commit()


def rainbow_group(group):
    """
    监听群消息，并保存到SQLite数据库（实时保存，每条消息即刻写入）

    Args:
        group(str): 群名
    """
    wx.AddListenChat(who=group, savepic=False)  # 添加监听对象并且自动保存新消息图片
    Me = "清易"

    # 建立数据库连接
    conn = sqlite3.connect(DB_PATH)
    create_table_if_not_exists(conn)  # 确保表格存在

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

                if '#夸我' in ds['发言内容'] and ds['发言者'] != 'SYS':
                    # @某人并发送消息
                    for _ in range(3):  # 发送6条
                        praise_msg = ' ' + random.choice(girl_ls)
                        at = [ds['发言者'], ]
                        wx.SendMsg(msg=praise_msg, who=group, at=at)
                        ds['夸奖内容'] = praise_msg
                        print(ds)

                        # 写入数据库（每条消息实时写入）
                        insert_record(conn, ds)
                        print(f"记录已写入SQLite数据库：{ds}")



# 免打扰也可获得内容
group = '测试群wxauto'
rainbow_group(group)

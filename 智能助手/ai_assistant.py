# -*- coding: utf-8 -*-
import json
import random
import sqlite3
from 彩虹屁.语料库 import girl_ls
from wxauto import WeChat
from datetime import datetime
import time
import re

import threading
import random
from openai import OpenAI

wx = WeChat()

def process_content(user_content):
    """单次对话-非流式"""
    api_key = "sk-815d1fd5ebcc4b06bede6c9f3da020fd"
    temperature = 0.7
    system_prompt = """
    # 角色
    你是一个专业的记账助手，能将用户输入的内容转化为记账清单，不进行随意扩写。
    
    ## 技能
    ### 技能1：记账
    1. 当用户提供一段文本时，判断用户输入内容是某种费用，迅速将其记录类别、明细、金额，如果判断不是某种金额的记录，则返回："非开销花费，不记录"
    2. 确保记录的准备性和流畅性
    3. 以json格式输出，比如：
    {
    "类目": "交通",
    "明细": "打车费",
    "费用": 20
    }
    
    ## 限制：
    - 只进行记账工作，不回答与记账无关的问题
    - 严格按照用户输入进行记账，不得擅自更改    
    """

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        messages=[
            # system角色：设置AI助手的系统级指令，这里定义助手的行为准则
            {"role": "system", "content": system_prompt},  # "你是一个非常厉害、强大、世界第一的助手。"
            # user角色：用户实际发送的对话内容，这里发送的是"Hello"
            {"role": "user", "content": user_content},
        ],
        model="deepseek-chat",  # DeepSeek-V3
        max_tokens=2048,
        # 代码生成/数学解题:0,数据抽取/分析:1,通用对话:1.3,翻译:1.3,创意类写作/诗歌创作:1.5
        temperature=temperature,  # 0.7,
        stream=False
    )
    msg = response.choices[0].message.content
    print(f'用户输入：{user_content}')
    print(f'输出：\n{msg}')
    return msg


def ai_assistant(group):
    """
    监听群消息，记录信息，智能回复

    Args:
        group(str): 群名
    """
    wx.AddListenChat(who=group, savepic=False)  # 添加监听对象并且自动保存新消息图片
    Me = "清易"

    # 建立数据库连接
    conn = sqlite3.connect('record_fee.db')

    while True:
        msgs = wx.GetListenMessage()  # 获取监听到的消息
        for chat in msgs:  # chat 是一个带有聊天名称的 uia提示
            one_msgs = msgs.get(chat)
            print(one_msgs)
            for msg in one_msgs:
                if msg[0] != 'SYS':
                    ds = {}
                    # ds['内容类型'] = msg.type  # 需要清洗处理时另外写，这里取原始数据
                    ds['日期'] = datetime.now().strftime("%Y-%m-%d")
                    ds['名称'] = Me if msg[0] == "Self" else msg[0]
                    ds['内容'] = msg[1]
                    ds['群名'] = str(chat)  # 转换群名为字符串，防止存储错误
                    json_msg = process_content(msg[1])
                    # 如果不是json，跳过
                    if '非开销花费，不记录' in json_msg:
                        continue
                    data = json.loads(json_msg)
                    ds['类目'] = data['类目']
                    ds['明细'] = data['明细']
                    ds['费用'] = data['费用']
                    ds['时间'] = datetime.now().strftime("%Y-%m-% d %H:%M:%S")
                    print(ds)


# 免打扰也可获得内容
group = 'Deepseek研究'
ai_assistant(group)

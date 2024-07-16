# v0.3 总结的内容写入到本地txt以方便复制粘贴。
"""
将ods转为dw，并且分析数据。
fixme： AI总结不准确，需要处理prompt


"""
import os

import pandas as pd
from datetime import datetime
import re

CON = "mysql://root:huanqlu0123@39.98.120.220:3306/spider?charset=utf8mb4"


def ods2dw_wechat():
    """
    将微信ods转为dw，以便分析使用
    """
    ods_sql_name = "ods_wxauto_wechat_msgs"
    sql = rf"SELECT * FROM {ods_sql_name}"

    df = pd.read_sql(sql, CON)
    # 1. 过滤：当日，去掉系统消息和群聊时间。
    df = df[~((df['内容类型'] == 'sys') | (df['内容类型'] == 'time'))]  # ()
    # 2. 清洗不需要内容：使用df内置正则清洗。 （ 去掉 for 前面内容以及'>'）
    df['群名'] = df['群名'].str.replace(r'^.*?for ', '', regex=True).str.replace(r'>$', '', regex=True)
    # 去掉 「引用」文字及其后的内容
    df['发言内容'] = df['发言内容'].str.replace(r'引用.*$', '', regex=True)

    # 3. 写入为dw
    dw_sql_name = ods_sql_name.replace("ods_", "dw_")
    df.to_sql(dw_sql_name, CON, if_exists='replace')
    print('ods2d预览：\n', df.head())
    return df


def df_analyze(df):
    """
    分析df，处理每个群的发言总数、发言人数、每个人发言数量。

    Args:
        df (pandas.DataFrame): 需要分析的df
    """
    str_today = datetime.now().strftime('%Y-%m-%d')
    df = df[df['记录日期'] == str_today]
    pt_group = df.pivot_table(index='群名', values='发言内容', aggfunc='count')
    pt1 = pd.DataFrame(pt_group).reset_index(False)  # pt转为df
    for _index, group_name in enumerate(list(pt1['群名'])):
        # print(_index, group_name)
        df_i = df[df['群名'] == group_name]  # 取单群统计 "wxauto交流"
        pt_i = df_i.pivot_table(index=['发言者'], values='发言内容', aggfunc='count')  # 透视「发言者- 发言数量」
        # 构造「群发言总概况」输出
        df2 = pd.DataFrame(pt_i['发言内容']).reset_index()
        df2 = df2.sort_values(by="发言内容", ascending=False)  # 排序
        df2.reset_index(drop=True, inplace=True)  # 重置索引
        print(f'\n{group_name}'
              f'\n🏆今日发言榜：\n'
              f'\n💬发言总计: {df2["发言内容"].sum()} '
              f'\n👥聊天人数: {df2["发言者"].count()}'
              f'\n'
              )
        # 构造「各人-发言概况」输出
        pt_i = pd.DataFrame(pt_i).reset_index()
        pt_i.sort_values(by="发言内容", ascending=False, inplace=True)
        pt_i.reset_index(drop=True, inplace=True)
        for i, row in pt_i.iterrows():  # 打印排名，使用 emoji 表示前3名，之后使用数字
            if i < 3:
                # 对于前三名使用金银铜牌 Emoji
                if i == 0:
                    emoji = '🥇'
                elif i == 1:
                    emoji = '🥈'
                elif i == 2:
                    emoji = '🥉'
                print(f"{emoji} 「{row['发言者']}」 - {row['发言内容']}")
            else:
                # 对于其他名次使用数字 Emoji
                emoji = f"{i + 1}"
                print(f"{emoji}. 「{row['发言者']}」 - {row['发言内容']}")
            if i == 9:  # 只打印前10名
                break


import requests
import json


def ernie_128k(speech_string, group_name):
    """
    调用百度api，将prompt_pre和speech_string拼接起来，然后调用百度api，总结微信话题。
    本块定义写了正则的嵌套处理。

    Args:
        speech_string (str): 需要总结的微信消息df转列表再转为的字符串
    """
    # print('=' * 100)
    prompt_pre = r"""
    # 目的：请提供群聊的聊天对话文本，并总结聊天内容最核心的3个话题。请严格按照以下要求和格式操作。
    
    # 前提：每个话题要简洁，用5-10个字总结，请确保字数在10个字以内。
    
    # 格式要求：
        1. 请按照以下严格格式总结话题：
           1. 话题。
           2. 话题。 
           3. 话题。

        2. 格式举例，请严格按这种格式，不要有多余的任何交互内容：
           举例一： 
           1. 健康生活。
           2. 减脂增肌。
           3. 打卡与分享。

           举例二： 
           1. 微信防掉线。
           2. 爬虫抓取。
           3. 特朗普枪击。

           举例三： 
           1. 机器人使用。
           2. 云服务器布署。
           3. 大屏可视化。
        
    # 聊天文本提供：
    """
    # 去除的内容： 每个人的发言已使用句号"。"隔开。
    ## 三、不需要任何多余的描述，不需要概述。

    content = prompt_pre + speech_string
    API_KEY = "kuchhBziVRyYEF6ZbH3EmVB2"
    SECRET_KEY = "zm4zQO6cyDQ828ACOxGHwPINYM6Vf9AC"

    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    response = requests.post(url, params=params)
    access_token = response.json().get("access_token")
    url_128k = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token={access_token}"
    payload = json.dumps({"messages": [{"role": "user", "content": content}]})
    headers = {'Content-Type': 'application/json'}

    # print(rf"开始请求ai：{prompt_pre}")
    # print(speech_string)
    response = requests.post(url_128k, headers=headers, data=payload)
    _json = response.json()
    _result = _json["result"]

    #  以正则的方式 取出ai回答的需要内容，因调试ai过于麻烦，无法特别精确，匹配正则取结果。
    def re_clean_text(text):
        """
        正则表达式清洗文本，取出特征「数字、小数点、冒号/句号」，通过正则拿到据。

        以取出的逻辑，而不是去除的逻辑。
        """
        # 取 数字开头，有一个小数点，至到冒号或句号结束
        pattern = re.compile(r'.*?(\d+\.+.*?)[：。]')  # \d数字  \. 转义小数点， >*？ 任意内容 ， [：。]中文冒号或中文句号
        matches = pattern.findall(text)  # 使用findall方法找出所有匹配的项
        # for match in matches:
        #     print(match.strip())
        match_str = '\n'.join(matches)  # 将匹配项以逗号分隔的字符串
        # print(match_str)  # 将匹配项以逗号分隔的字符串)
        return match_str

    match_str = re_clean_text(str(_result))

    print(f'提取的正则内容：\n{match_str}')
    ctn_summary = f'\n🌟今日话题总结（{group_name}）:\n{match_str}'
    print(ctn_summary)

    # 保存到txt
    folder = "./data/微信总结/"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # 打开文件，读取其内容
    with open(f"./data/微信总结/{group_name}.txt", "r", encoding="utf-8") as f:
        file_content = f.read()
    # 将新内容插入到文件内容的开头
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_content = f"{current_time}\n{ctn_summary}\n\n\n{file_content}"
    # 写回文件
    with open(f"./data/微信总结/{group_name}.txt", "w", encoding="utf-8") as f:
        f.write(new_content)

    # print('=' * 100)
    return _result


def fetch_content():
    """
    取出微信聊天内容，转为字符串，用于传入ai总结为话题。

    主入口，提取dw数据库，遍历群消息做AI话题总题，通过prompt规整格式。

    """
    str_today = datetime.now().strftime('%Y-%m-%d')
    dw_name = "dw_wxauto_wechat_msgs"
    sql = rf"SELECT * FROM {dw_name}"
    df = pd.read_sql(sql, CON)
    df_copy = df.copy()  # 在for 会重新赋值，此处需要建个副本

    group_names = list(df['群名'].unique())  # 遍历群名
    print(f'群列表： {group_names}')
    for group_name in group_names:
        df2 = df[(df['记录日期'] == str_today) & (df['群名'] == group_name)]  # 提取群名
        if len(df2) == 0:
            pass
        else:
            print(f"\n{group_name}: 发言条数：{len(df2)}")
            # 清洗聊天文本
            speech_list = [speech.replace('\n', ' ') for speech in df2['发言内容']]  # 预处理列表元素每个换行
            speech_list = [re.sub(r'@\S*?\s', '', speech) for speech in speech_list]  # 正则表达式去除@开头与空格之间的文本
            talk_content = '。'.join(speech_list)  # 使用\n隔开每行内容，使ai判断断句
            talk_content = talk_content.replace('=', '')  # 去除聊天内容原有的 = 号

            talk_content = '==========<以下是聊天内容：' + talk_content + ' 以上是聊天内容>=========='  # 在前后加上 = ，让ai好判断哪些是聊天内容（标识作用）
            ernie_128k(talk_content, group_name)


## ods2dw
# 1. 发言排行
df = ods2dw_wechat()  # 将ods转为dw，
# df_analyze(df)  # 发言榜单

# 2. 话题总结
fetch_content()

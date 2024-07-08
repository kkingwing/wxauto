"""
将ods转为dw，并且分析数据。
"""
import pandas as pd
from datetime import datetime

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
    # 3. 写入为dw
    dw_sql_name = ods_sql_name.replace("ods_", "dw_")
    df.to_sql(dw_sql_name, CON, if_exists='replace')
    print(df)
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


def ernie_128k(speech_string):
    """
    调用百度api，将prompt_pre和speech_string拼接起来，然后调用百度api，总结微信话题。

    Args:
        speech_string (str): 需要总结的微信消息df转列表再转为的字符串
    """
    print('=' * 100)
    prompt_pre = r"""
    以下内容是我的一个群聊天记录，我已经清洗过了，每个人的发言使用了换行符\\n隔开，
    请帮我以总结出讨论的每个话题核心内容（都用10-20个字），结构格式是：「1. 话题（热度）：解决方法；」，注意要按讨论的数量当作热度排名。
    总结样例如： 「1. 图片识别和撤回处理（热度：高）\\n解决方法：……」，注意解决方法要使用陈述句给出精炼的短句。
    以下是该群的聊天内容：
    """

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

    print(rf"开始请求ai：{prompt_pre}")
    response = requests.post(url_128k, headers=headers, data=payload)
    _json = response.json()
    _result = _json["result"]
    print('\n\n🌟今日话题总结:\n', _result)
    print('=' * 100)
    return _result


def fetch_content():
    """
    取出微信聊天内容，转为字符串，用于传入ai总结为话题。
    """
    str_today = datetime.now().strftime('%Y-%m-%d')
    dw_name = "dw_wxauto_wechat_msgs"
    sql = rf"SELECT * FROM {dw_name}"
    df = pd.read_sql(sql, CON)
    df = df[(df['记录日期'] == str_today) & (df['群名'] == "wxauto交流")]  # 提取群名
    speech_list = [speech.replace('\n', ' ') for speech in df['发言内容']]  # 预处理列表元素每个换行
    talk_content = '\n'.join(speech_list)  # 使用\n隔开每行内容，使ai判断断句
    print(talk_content)
    return talk_content


# df = ods2dw_wechat()
# df_analyze(df)

talk_content = fetch_content()
ernie_128k(talk_content)
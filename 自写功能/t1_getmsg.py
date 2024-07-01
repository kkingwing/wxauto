"""
记录微信消息

1. 先测试记录一天有没有问题
2. 若没有问题，加入清洗加分析的逻辑
3. 若也无问题，再加入微信自动化逻辑


"""

from wxauto import WeChat
from datetime import datetime
import time
import pandas as pd
from sqlalchemy import create_engine
from config import CON

wx = WeChat()


# 一、功能： 聊天消息记录， 自动处理，调用excel宏生成分析图

# wx.ChatWith("wxauto交流")
# g1 = wx.CurrentChat() # 获取当前窗口名

def write_to_sql(df):
    engine = create_engine(CON)
    df.to_sql('wxauto_wechat_msgs', con=engine, if_exists='append', index=False)


# 指定监听目标，（不能放入while True中，会出现逻辑错误，一直为空）
listen_list = [
    "wxauto交流",
    # "python接单群2", # 不能监测企微群
    # "测试群wxauto",
]
for i in listen_list:
    wx.AddListenChat(who=i, savepic=False)  # 添加监听对象并且自动保存新消息图片

# 持续监听消息，并且收到消息后回复“收到”
wait = 20  # 设置20秒查看一次是否有新消息
Me = "清易"
CACHE_NUMBER = 5  # 这是「缓存的消息条数」超过这个数就将缓存写到数据库中.
ls = []
while True:
    msgs = wx.GetListenMessage()  # 这一句会先取原有的聊天内容，根据上下的聊天内容判断消耗新id是否为新
    # print(f"原监听消息内容是：{msgs}")
    for chat in msgs:  # chat 是一个带有聊天名称的 uia提示
        one_msgs = msgs.get(chat)  # 获取消息内容,one_msgs[0] # 说话者/时间/系统提示  one_msgs[1] 说话内容
        for msg in one_msgs:
            ds = {}
            ds['记录日期'] = datetime.now().strftime("%Y-%m-%d")
            ds['群名'] = chat  # listen_list[0]  # 暂时用这个方法
            ds['内容类型'] = msg.type  # 需要清洗处理时另外写，这里取原始数据
            ds['发言者'] = Me if msg[0] == "self" else msg[0]  # 如果是自己说话，使用名称替换
            ds['发言内容'] = msg[1]
            ds['发言时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # chat.SendMsg('收到')  # 回复收到
            print(ds)
            ls.append(ds)
            # 写入数据库
            if len(ls) >= CACHE_NUMBER:  # 这是「缓存的消息条数」超过这个数就将缓存写到数据库中.
                df = pd.DataFrame(ls)
                print(f'缓存消息大于 {CACHE_NUMBER} 条,df写入sql：\n{df}\n')
                write_to_sql(df)
                ls = []  # 重置列表为
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} 缓存条数：{len(ls)}")
    time.sleep(wait)

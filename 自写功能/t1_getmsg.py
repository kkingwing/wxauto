from wxauto import WeChat
import time

wx = WeChat()
# 一、功能： 聊天消息记录， 自动处理，调用excel宏生成分析图

# wx.ChatWith("wxauto交流")
# g1 = wx.CurrentChat() # 获取当前窗口名

# 指定监听目标
listen_list = [
    # '数据运营',
    "wxauto交流",
]
for i in listen_list:
    wx.AddListenChat(who=i, savepic=True)  # 添加监听对象并且自动保存新消息图片

# 持续监听消息，并且收到消息后回复“收到”
wait = 3  # 设置10秒查看一次是否有新消息
while True:
    msgs = wx.GetListenMessage()
    for chat in msgs:
        one_msgs = msgs.get(chat)  # 获取消息内容
        # 回复收到
        for msg in one_msgs:
            print(msg)
            if msg.type == 'friend':
                chat.SendMsg('收到')  # 回复收到
    time.sleep(wait)

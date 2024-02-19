
from wxauto import WeChat
wx = WeChat()

def main1():
    wx._show # 显示微信主界面，置顶
    msgs = wx.GetAllMessage() # 获取所有消息
    lastmsgid2 = msgs[-1][-1] if msgs else None
    while True:
        msgs = wx.GetNextNewMessage2(lastmsgid=lastmsgid2,savepic=False)
        if msgs is not None:
            for who, new_msgs in msgs.items():
                print(f"New messages for {who}:")
                for msg in new_msgs:
                    print(f"{msg[0]}: {msg[1]}")
                    # 如果收到消息为"你好"，则自动回复"你好"
                    if {msg[1]} == "你好":
                        wx.SendMsg("你好")
                    else:
                        wx.SendMsg("不理解")
        time.sleep(10)
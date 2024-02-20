from my_method import write_to_sql
from my_method import today

from wxauto import WeChat
import time
import pandas as pd


class WechatItemUse:
    def __init__(self):
        self.wx = WeChat()
        pass

    ###
    # 获取聊天记录(当前窗口,上面已跳转到目标窗口）
    ###
    def get_msg(self, ):
        who = 'wxauto交流'
        self.wx.ChatWith(who)  # 跳到窗口

        # 1. 加载所有消息 （注，当前没有办法将手机消息同步到电脑端显示，这是目前微信的问题。）
        flag = True  # 循环标志
        roll_times = 1  # 向上滚动次数，若为0则获取所有消息
        try:
            if roll_times > 0:
                for i in range(roll_times):
                    self.wx.LoadMoreMessage()  # 加载消息
                    time.sleep(0.1)
            elif roll_times == 0:
                while flag:
                    flag = self.wx.LoadMoreMessage()
                    time.sleep(0.1)
        except Exception:
            print('意料之外的错误，请检查原始方法。')  # 一般不会走到这里

        # 获取消息保存到Excel、sql
        ls = []
        msgs = self.wx.GetAllMessage(savepic=False)
        for msg in msgs:
            # msg[0] 说话者， mas[1] 说话内容
            # 跳过不规范的时间、系统提示，只获取内容
            if msg[0] == "Time":
                pass
            elif msg[0] == "SYS":
                pass
            else:
                ds = {}
                ds['说话者'] = msg[0]
                ds['说话内容'] = msg[1]
                ds['记录日期'] = today()
                ls.append(ds)
        # 写入数据库，保留本次运行的临时表格。
        df = pd.DataFrame(ls)
        df.to_excel('./本次获取内容.xlsx', index=False)
        write_to_sql(df)  # 写入我的sql
        print(df)

    ###
    # 2. 发送消息
    ###
    def send_msg(self, ):
        who = '文件传输助手'
        msg = "使用说明：\n" + \
              "wxauto发送消息\n" + \
              "测试"
        self.wx.SendMsg(msg, who, clear=True)

    ###
    # 3. 发送文件
    ###
    def send_files(self, ):
        who = "文件传输助手"
        filepath = r"D:\Code\wxauto\wxauto文档20240206.pdf"
        self.wx.SendFiles(filepath, who)

    ###
    # 4.  获取未读消息（未开免打扰），与「获取消息」合用，「检测消息后做动作」。
    ###
    def get_next_new_msg(self):
        msgs = self.wx.GetNextNewMessage()
        if msgs == None:
            print('没有新消息')

    ###
    # 5. 获取当前窗口名称，用于判断，结合判断做动作。
    ###
    def get_current_name(self):
        current_name = self.wx.CurrentChat()
        print(current_name)

    ###
    # 6. 监听消息
    ###
    def listen_chat_2(self):
        me = '清易'  # 用于判断最新消息记录是否为非本人
        who = "chatgpt测试群"
        self.wx.ChatWith(who=who)  # 跳到窗口
        msgs_1 = self.wx.GetAllMessage(savepic=False)  # 先读取一次消息，得到当前消息列表
        last_msg_id_1 = msgs_1[-1][-1] if msgs_1 else None  # 获取最后一句的消息的id

        # 监听消息并回复
        while True:
            # 读取最新聊天记录
            msgs_2 = self.wx.GetNextNewMessage_2(lastmsgid=last_msg_id_1, savepic=False)
            if msgs_2:
                for who, new_msgs in msgs_2.items():  # 遍历聊天窗口i
                    print('新的消息', who, new_msgs)
                    last_msg_id_1 = msgs_2[who][-1][-1]  # 更新最后一条的聊天记录
                    for msg in new_msgs:
                        print(f'消息内容：  {msg[0]}:{msg[1]}')
                        if msg[0] != 'SYS' and msg[0] != me:
                            # 这里写发送消息的方法 可以def
                            self.wx.SendMsg(msg="收到")
            else:
                print('消息为空，监听中……')
            time.sleep(5)


if __name__ == '__main__':
    # 获取微信窗口对象
    wiu = WechatItemUse()
    # wiu.get_msg() # 获取消息
    # wiu.send_msg()  # 发送消息
    # wiu.send_files()  # 发送文件
    # wiu.get_next_new_msg()  # 获取未读消息（未开免打扰），与「获取消息」合用，「检测消息后做动作」。
    # wiu.get_current_name()  # 获取当前窗口名称，用于判断
    wiu.listen_chat_2()  # 监听消息，自定义

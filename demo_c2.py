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
        who = "chatgpt测试群"
        self.wx.ChatWith(who=who)  # 跳到窗口
        msgs_1 = self.wx.GetAllMessage(savepic=False)  # 获取所有消息，图片是否保存
        # print("全消息:", msgs_1)
        # print('最后一句的消息', msgs_1[-1])
        last_msg_id_1 = msgs_1[-1][-1] if msgs_1 else None  # 获取最新消息的id
        print('最后一句的消息的id', last_msg_id_1)

        # 监听消息并回复
        while True:
            time.sleep(3)
            msgs_2 = self.wx.GetAllMessage(savepic=False)
            if last_msg_id_1 is not None and last_msg_id_1 in [i[-1] for i in msgs_2[:-1]]:
                msgs = self.wx.GetNextNewMessage()  # 获取未读消息
                print("新获取的未读消息内容: ", msgs)
                if msgs:
                    for who, msg in msgs.items():  # 遍历聊天窗口i
                        print(who, msg)
                        if msg:  # 如果i聊天窗口非空，发送以下内容
                            self.wx.SendMsg(msg="收到")
            else:
                print('有所不对，检验')



if __name__ == '__main__':
    # 获取微信窗口对象
    wiu = WechatItemUse()
    # wiu.get_msg() # 获取消息
    # wiu.send_msg()  # 发送消息
    # wiu.send_files()  # 发送文件
    # wiu.get_next_new_msg()  # 获取未读消息（未开免打扰），与「获取消息」合用，「检测消息后做动作」。
    # wiu.get_current_name()  # 获取当前窗口名称，用于判断
    wiu.listen_chat_2()  # 监听消息，自定义

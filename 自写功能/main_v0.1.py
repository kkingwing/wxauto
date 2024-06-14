# v0.1 现可用功能罗列
# 作者：清易
# 用途：自用

###
# 功能：使用git_wxauto项目，经过修改，达到微信的一些自动化效果。
# 当前功能：「获取消息、发送消息及文件、获取未读消息、监听消息」
# 用途：自动任务，群消息监测转发，消息监测。
###

from wxauto import WeChat
import time
from datetime import datetime
import pandas as pd

CON = "mysql://root:huanqlu0123@39.98.120.220:3306/spider?charset=utf8mb4"


class WechatItemUse:
    def __init__(self):
        self.wx = WeChat()

    ###
    # 获取聊天记录(当前窗口,上面已跳转到目标窗口）
    def get_msg(self, ):
        who = 'wxauto交流'
        self.wx.ChatWith(who)  # 跳到窗口

        # 1. 加载所有消息 （注，当前没有办法将手机消息同步到电脑端显示，这是目前微信的问题。）
        flag = True  # 循环标志
        roll_times = 2  # 向上滚动次数，若为0则获取所有消息
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
                ds['记录时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ls.append(ds)
        # 写入数据库，保留本次运行的临时表格。
        df = pd.DataFrame(ls)
        df.to_excel('./本次获取内容.xlsx', index=False)
        # write_to_sql(df)  # 写入我的sql
        print(df)

    ###
    # 2.1 发送消息
    ###
    def send_msg(self, ):
        who = '文件传输助手'
        msg = "使用说明：\n" + \
              "wxauto发送消息\n" + \
              "测试"
        self.wx.SendMsg(msg, who, clear=True)

    ###
    # 2.2 发送消息
    ###
    def read_sql_and_send_msg(self, ):
        # who = '文件传输助手'
        whos = ["chatgpt测试群", "峡谷啊", ]  # 暂未支持emoji名称,需要设置备注名
        # whos = ["家有儿女",]
        df = read_sql_info_brief()
        _head = f"今日要闻（{today()}）：\n"
        msgs = []
        msgs.append(_head)
        for (i, (category, title, summary, url)) in enumerate(zip(df['Ai类别'], df['标题'], df['Ai摘要'], df['链接'])):
            _msg = f"{i + 1}.\n" + \
                   f"类别：{category}\n" + \
                   f"标题：{title}\n" + \
                   f"摘要：{summary}\n" + \
                   f"链接：{url}\n" + \
                   f"\n"
            msgs.append(_msg)
            time.sleep(1)
        notion = '（以上内容由AI总结生成，如有冒犯敬请见谅）\n'
        msgs.append(notion)
        # 将列表转为字符串
        msgs_str = "".join(msgs)

        for who in whos:
            self.wx.SendMsg(msgs_str, who, clear=True)

    ###
    # 3. 发送文件
    ###
    def send_files(self, ):
        who = "文件传输助手"
        filepath = r"D:\Code\wxauto\wxauto文档20240206.pdf"
        self.wx.SendFiles(filepath, who)

    ###
    # 4.  获取未读消息（未开免打扰），本方法没做任何动作，只是演示。 需要与「获取消息」合用，「检测消息后做动作」。
    ###
    def get_next_new_msg(self):
        while True:
            msgs = self.wx.GetNextNewMessage()
            if msgs == None:
                print('没有新消息')
            else:
                print(msgs)
                self.wx.ChatWith(who="文件传输助手")  # 跳到窗口
            time.sleep(5)

    ###
    # 5. 获取当前窗口名称，用于判断，结合判断做动作。
    ###
    def get_current_name(self):
        current_name = self.wx.CurrentChat()
        print(current_name)

    ###
    # 7. 监听所有消息（未被屏蔽） ，以下为指定，若需要监听所有，修改一下为未指定即可。 有所瑕疵，会持续跳助手。
    ###
    def listen_all(self):
        while True:
            msg = self.wx.GetNextNewMessage(savepic=False)
            print(msg)
            # 若存在消息且为指定群
            if msg and self.get_current_name() == 'gpt测试群':
                print(msg)
            else:
                print('无新消息')

            # 跳到其它位置，以免检测不到。
            if self.get_current_name() == '文件传输助手':
                pass
            else:
                self.wx.ChatWith(who='文件传输助手')  # 跳回文件传输助手
            time.sleep(5)

    ###
    # 8. 监测指定微信群/人消息，过滤并转发。（用于过滤关心的内容）
    ###
    def listen_and_transpond(self):
        me = '清易'  # 避开自身的消息检测
        origin_chat_window = '文件传输助手'
        listen_groups = ['chatgpt测试群', "小红书运营交流群18"]
        send_to_who = '数据运营'  # 发给谁，最好是唯一的，可以是备注名
        detected_word = '需求'  # 需要检测的关键字，空文本则不检测关键字
        self.wx.ChatWith(who=origin_chat_window)  # 初始跳到传输助手对话

        # 获取未读消息
        while True:
            # 检测新消息、之后跳回初始文件传输助手，避免检测不到消息
            msg_ds = self.wx.GetNextNewMessage_3(savepic=False)  # 获取下一个新消息
            print(msg_ds)
            if msg_ds:
                # 处理数据并转发
                for who, msgs in msg_ds.items():
                    # 若「监测名称」在监测列表中，且「监测消息」符合关键字，则转发。
                    # 去掉"已置顶"三个字
                    # 其中的这一串  "".join([i[-2] for i in msgs]) 是将消息合并，检测关键字是否在其中
                    bool_group = who.strip('已置顶') in listen_groups
                    bool_word = detected_word in "".join([i[-2] for i in msgs])
                    print(bool_group, bool_word)
                    if bool_group and bool_word:
                        # 转发，解析消耗表
                        # 解析新消息，并只保留「包含检测关键字的二级子列表元素」，替换msgs
                        msgs = [msg for msg in msgs if detected_word in msg[1]]
                        # 遍历消息，构造发送格式
                        send_msg = "\n".join([f"{msg[0]}：{msg[1]}" for msg in msgs])
                        self.wx.SendMsg(msg=send_msg, who=send_to_who)
                        print('转发成功')
                    else:
                        print('不需要转发')

                # 跳回文件助手
                self.wx.ChatWith(who=origin_chat_window)

            time.sleep(3)

    def get_group_member(self):
        wx = WeChat()
        wx.ChatWith(who="wxauto交流")
        members = wx.GetGroupMembers()
        print(f"成员共有：{len(members)}位，详情为：{members}")

    def get_all_friends(self):
        wx = WeChat()
        friends = wx.GetAllFriends()
        print(friends)

    ###
    # 应用1. 群活跃管理：监听消息，（监听指定消息窗口，记录，并后于统计，定时或触发消息发送.）
    # 单个群监测 √
    # 保存图片 √
    # emoji的记录
    # 多个群监测，下面的方法逻辑不适用多个窗口，需要另改逻辑。
    ###
    def listen_one_group(self):
        # me = '清易'  # 用于判断最新消息记录是否为非本人,新改动,自己为字符串「Self」
        who = "wxauto交流"  # 目前是单个群组
        who = "AI机器人测试"
        self.wx.ChatWith(who=who)  # 跳到窗口
        msgs_1 = self.wx.GetAllMessage(savepic=False)  # 先读取一次最近消息，得到当前消息列表
        print(msgs_1)
        last_msg_id_1 = msgs_1[-1][-1] if msgs_1 else None  # 获取最后一句的消息的id
        ###
        # 监听消息并回复
        # === 常量区 ===
        ls = []
        CACHE_NUMBER = 2
        # === 常量区 ===
        while True:
            time.sleep(0.5)  # 停顿监测 ，因要监测，这里的时间间隔尝试写为单秒。
            # 读取最新聊天记录
            msgs_2 = self.wx.GetNextNewMessage_2(lastmsgid=last_msg_id_1, savepic=True)
            if msgs_2 is not None:
                for who, new_msgs in msgs_2.items():  # 遍历聊天窗口i
                    print('新的消息', who, new_msgs)
                    last_msg_id_1 = msgs_2[who][-1][-1]  # 更新最后一条的聊天记录
                    for msg in new_msgs:
                        ds = {}
                        ds['记录日期'] = datetime.now().strftime("%Y-%m-%d")
                        ds['群名'] = who.split("(")[0] if "(" in who else who  # 这里的变量群名会自动变化。
                        ds['发言者'] = "清易" if msg[0] == "Self" else msg[0]
                        ds['发言内容'] = msg[1]  # 这里如果是图片的话，会是一个图片地址，保存在同目录下的「微信图片」文件夹中。
                        ds['消息id'] = msg[2]
                        ds['发言时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 这是一个模拟时间,记录是的电脑时间。需要时刻变化。
                        print(f'{ds},当前消息缓存长度 {len(ls) + 1} 条消息，满 {CACHE_NUMBER} 条时写入数据库。')
                        ls.append(ds)
                        if len(ls) >= CACHE_NUMBER:  # 这是「缓存的消息条数」超过这个数就将缓存写到数据库中.
                            df = pd.DataFrame(ls)
                            print(f'消息大于20条,df写入sql{df}')
                            # write_to_sql(df)
                            print(f'写入完成.')
                            ls = []  # 重置列表为
            else:
                print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  消息为空，监听中……')

    def at_somebody(self):
        wx = WeChat()
        who = 'AI机器人测试'
        # msg = '通知：测试'
        # wx.AtAll(msg=msg, who=who)

        at_list = ['巨神峰', 'chenqiuyuan_968']  # 可以是微信号
        msg = "消息测试"
        wx.SendMsg(msg=msg, who=who, at=at_list)


if __name__ == '__main__':
    # 获取微信窗口对象
    wx = WechatItemUse()
    # wx.get_msg()  # 获取消息 （电脑端消息不全，需要实时记录） 可用 √

    # wx.send_msg()  # 发送消息 ,（「文本资讯内容」在这个方法发送）
    # wx.read_sql_and_send_msg()  # 读取资讯sql发送消息
    # wx.send_files()  # 发送文件  （「文件」使用这个方法发送」）
    # wx.get_next_new_msg()  # 获取未读消息（未开免打扰），演示没有做任何动作，这是获取未读内容，要结合其它逻辑使用。
    # who = wx.get_current_name()  # 获取当前窗口名称，用于判断
    # wx.listen_all()  # 监听所有消息（未被屏蔽）
    # wx.listen_and_transpond()  # 监测指定微信群/人消息，过滤并转发。
    # wx.get_artile_link() # 获取文章链接
    # wx.get_group_member()  # 获取群成员
    # wx.get_all_friends() # 获取所有联系人 {名称、备注、标签}
    #
    wx.listen_one_group()  # 监听指定窗口消息,记录。
    #
    # wx.at_somebody()

# 后续功能：转发消息
# 想要了解这个项目，需要更深一步了解 uiauto
# 用3.9.8.15的版本，不然容易 出问题。（见云盘）

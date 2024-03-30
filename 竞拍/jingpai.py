from wxauto import WeChat
import time
import re

# 实例化微信对象
wx = WeChat()

who = '九星组委会'


def find_max_value_and_key(aar):
    if not aar:
        return None, None

    max_value = float('-inf')
    max_key = None
    max_index = float('inf')

    for i, d in enumerate(aar):
        for k, v in d.items():
            if v > max_value:
                max_value = v
                max_key = k
                max_index = i
            elif v == max_value and i < max_index:
                max_key = k
                max_index = i

    return max_value, max_key, max_index


# 指定监听目标
def jianting(i_j, i_p):
    wait = 1  # 设置10秒查看一次是否有新消息
    i = 0
    stat = time.time()
    msg_pm = []
    releaseTime = []
    while i < 27:
        # 47为60秒，24为30秒
        msgs = wx.GetListenMessage()

        for chat in msgs:
            msg = msgs.get(chat)
            # msg_m = msg[-1][1]
            # msg_p = msg[-1][0]
            print(msg)
            # print(len(re.findall(r'\d+', msg_m)))
            # print(len(re.findall(r'\D+', msg_m)))
            # print(re.findall(r'\D+', msg_m))
            listEvs = []
            for msg_i in msg:
                msg_0 = []
                if re.search(r"，起拍价", msg_i[1]):
                    releaseTime = int(msg_i[2])
                    index = msg.index(msg_i)
                    x = msg.pop(index)
            # print(releaseTime, msg_i)
            # print(msg)

            for msg_i in msg:
                if len(re.findall(r'\d+', msg_i[1])) != 0 and len(re.findall(r'\D+', msg_i[1])) == 0 and int(
                        re.findall(r'\d+', msg_i[1])[0]) > i_j and ((int(re.findall(r'\d+', msg_i[1])[0])) - i_j) % 10 == 0 and int(msg_i[2])>releaseTime:
                    msg_0.append({msg_i[0]: int(re.findall(r'\d+', msg_i[1])[0])})
                    print(msg_0)
            if len(msg_0) > 0:
                msg_i[1], msg_i[0], max_index = find_max_value_and_key(msg_0)
                chat.SendMsg(f"★{msg_i[0]} ★ 有效叫价： {msg_i[1]} 元")
                chat.SendFiles(r'C:\Users\LvZexin\PycharmMypor\pythonProject1\jingpai_auto\play\30s.gif')
                msg_pm.append([msg_i[0], msg_i[1]])
                i = 13
                i_j = msg_i[1]

        time.sleep(wait)
        i += 1
        # print(msg_pm)
        if i == 27:
            if len(msg_pm) == 0:
                wx.SendMsg('恭喜 【提名者】 获得【' + i_p + '】！', who=who)



            else:
                wx.SendMsg(f'恭喜{msg_pm[-1][0]}，你以{msg_pm[-1][1]} 元获得【 {i_p} 】！', who=who)

        # print(i)

    time_t = time.time() - stat
    print(time_t)


wx.AddListenChat(who=who, savepic=False)  # 添加监听对象并且自动保存新消息图片
plays = [['1号:', 'C罗', 50], ['2号:', '哈兰德', 50], ['3号:', '姆巴佩', 50], ['4号:', '赖斯', 50],
         ['5号:', '莱万', 50]]
# 持续监听消息，并且收到消息后回复“收到”
for i, play in enumerate(plays, start=1):
    wx.SendMsg('竞拍时禁止闲谈，只能发送金额，比如“60”，不要带“元”！', who=who),
    wx.SendMsg(play[0] + "【" + play[1] + "】" + "，起拍价：" + str(play[2]), who=who)
    wx.SendFiles(fr'C:\Users\LvZexin\PycharmMypor\pythonProject1\jingpai_auto\play\{i}.jpg', who=who)
    wx.SendFiles(r'C:\Users\LvZexin\PycharmMypor\pythonProject1\jingpai_auto\play\60s.gif', who=who)
    jianting(play[2], play[1])
wx.SendMsg('本次竞拍结束', who=who)

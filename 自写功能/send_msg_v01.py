from wxauto import WeChat

wx = WeChat()

# 发送图片
files = [
    # r'C:\Users\user\Desktop\1.jpg',   # 图片
    # r'C:\Users\user\Desktop\2.txt',   # 文件
    # r'C:\Users\user\Desktop\3.mp4'    # 视频
    r"D:\Users\Desktop\运营排行榜\0924\运营榜单_0924.png"
]

who = '文件传输助手'
wx.SendFiles(filepath=files, who=who)
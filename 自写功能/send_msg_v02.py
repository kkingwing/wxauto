from wxauto import WeChat
from datetime import datetime

wx = WeChat()

today = datetime.today().strftime('%m%d')
ex_today = datetime.today().strftime('%Y%m%d')
# 给多人发送文件
names = ['文件传输助手', '测试群wxauto']
for who in names:
    files = [
        # r'C:\Users\user\Desktop\1.jpg',   # 图片
        # r'C:\Users\user\Desktop\2.txt',   # 文件
        # r'C:\Users\user\Desktop\3.mp4'    # 视频
        rf"D:\Users\Desktop\运营报告\1-5正式运行{today}\【运营日报】BI仪表盘{today}.xlsx",
        rf"D:\Users\Desktop\运营报告\1-5正式运行{today}\{ex_today}_092010.png",
        rf"D:\Users\Desktop\运营排行榜\{today}\运营榜单_0924.png"
    ]
    wx.SendFiles(filepath=files, who=who)

# msg = '文件已发送，请查收。'
# who = '工作群A'
# at = ['张三', '李四']  # 要@的人
# wx.SendMsg(msg=msg, who=who, at=at)

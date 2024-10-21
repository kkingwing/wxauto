from custom_method import find_files
from wxauto import WeChat
from datetime import datetime

# 要查找的文件信息(目录, 发送文件的关键字, 后缀名)
full_today, today = datetime.today().strftime('%Y%m%d'), datetime.today().strftime('%m%d')
files_info = [
    (rf"D:\Users\Desktop\运营报告\1-5正式运行{today}", f"【运营日报】BI仪表盘", ".xlsx"),
    (rf"D:\Users\Desktop\运营报告\1-5正式运行{today}", f"{full_today}", ".png"),
    (rf"D:\Users\Desktop\运营排行榜\{today}", "运营榜单", ".png")
]

files = find_files(files_info)

# files = [r'D:\Code\wxauto\检测解析\抖音视频提取\dy_20241021170931.mp4',] # 这是一个列表


# 实例
wx = WeChat()
# 发送文件
who_s = ['文件传输助手', '测试群wxauto', ]
for who in who_s:
    wx.SendFiles(filepath=files, who=who)
    # @某人并发送消息
    at = ['数据运营', '墨云霄']  # 要@的人
    msg = ' 文件已发送，请查收。'
    wx.SendMsg(msg=msg, who=who, at=at)

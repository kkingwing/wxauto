import os
from wxauto import WeChat
from datetime import datetime


# 函数：根据关键字在指定路径中查找文件
def find_file(path, keyword, file_ls):
    for root, _, files in os.walk(path):  # 分别是： 目录，子目录，全文件名列表
        for file in files:  # 在「全文件名列表」中查找文件
            if keyword in file and file.endswith(file_ls):  # 如果关键字在文件名中且扩展名匹配
                target_files = os.path.join(root, file)  # # 只返回第一个匹配的文件
                return target_files
    return None  # 后续列表中会自动忽略None


# 要发送的文件，参数分别为：(目录， 关键字，扩展名)
# 构造文件列表
full_today = datetime.today().strftime('%Y%m%d')
today = full_today[-4:]
files_info = [
    (rf"D:\Users\Desktop\运营报告\1-5正式运行{today}", f"【运营日报】BI仪表盘", ".xlsx"),
    (rf"D:\Users\Desktop\运营报告\1-5正式运行{today}", f"{full_today}", ".png"),
    (rf"D:\Users\Desktop\运营排行榜\{today}", "运营榜单", ".png")
]

# 若找到文件，则添加到列表中，None在列表中会被忽略
files_to_send = [find_file(path, keyword, file_ls)
                 for path, keyword, file_ls in files_info
                 if find_file(path, keyword, file_ls)
                 ]

# 初始化 WeChat 实例
wx = WeChat()
# 要发送的人的列表
names = ['文件传输助手', '测试群wxauto']
for who in names:
    wx.SendFiles(filepath=files_to_send, who=who)
    # 发送后艾特某人某消息
    msg = ' 文件已发送，请查收。'
    at = ['数据运营', '墨云霄']  # 要@的人
    wx.SendMsg(msg=msg, who=who, at=at)

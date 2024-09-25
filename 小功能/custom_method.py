import os


def find_files(files_info):
    """
    根据关键字在指定路径中查找文件，构造目标文件列表

    Args:
        files_info (list): 待发达的文件特征列表，每个元素为 (目录, 发送文件的关键字, 后缀名)
    Returns:
        list: 查找到的文件路径列表
    Example:
        files_info = [
            (rf"D:\Users\Desktop\运营报告\1-5正式运行{today}", f"【运营日报】BI仪表盘", ".xlsx"),
            (rf"D:\Users\Desktop\运营报告\1-5正式运行{today}", f"{full_today}", ".png"),
            ]
    """
    files2send = []
    for path, keyword, suffix in files_info:
        for root, _, files in os.walk(path):  # 遍历目录、子目录、全文件名列表
            for file in files:  # 遍历「全文件名列表」
                if keyword in file and file.endswith(suffix):  # 查找包含关键字的文件
                    files2send.append(os.path.join(root, file))
                    break  # 找到第一个匹配的文件后就退出当前循环
    print(f'待发送文件：{files2send}')
    return files2send

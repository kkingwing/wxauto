import re

text = """
 根据提供的聊天文本，最核心的三个话题可能是：

1. 打卡。
2. 图片分享。
3. 视频分享。
"""


def re_clean_text(text):
    """
    正则表达式清洗文本，取出特征「数字、小数点、冒号/句号」，通过正则拿到据。

    以取出的逻辑，而不是去除的逻辑。
    """
    # 取 数字开头，有一个小数点，至到冒号或句号结束
    pattern = re.compile(r'.*?(\d+\.+.*?)[：。]')  # \d数字  \. 转义小数点， >*？ 任意内容 ， [：。]中文冒号或中文句号
    matches = pattern.findall(text)  # 使用findall方法找出所有匹配的项
    # for match in matches:
    #     print(match.strip())
    match_str = ', '.join(matches)  # 将匹配项以逗号分隔的字符串
    print(match_str)  # 将匹配项以逗号分隔的字符串)
    return match_str


re_clean_text(text)

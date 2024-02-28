def find_all_children(control, cmp, level=0):
    """查找所有满足要求的元素，并返回列表"""
    children = control.GetChildren()
    result = []
    for child in children:
        if cmp(child):  # child.ControlTypeName == "TextControl" :
            # print(" "*level,level,end = "          ")
            # print(child)
            result.append(child)
            # print(child.ControlTypeName, " - " , child.Name)
        result.extend(find_all_children(child, cmp, level + 1))
    return result


def linkprase(wx, user):
    ## 点开链接
    wx.ChatWith(user)
    c = find_all_children(wx.ChatBox, lambda a: True if a.Name == "[链接]" else False)[-1]
    C_MsgList = wx.C_MsgList
    linkcontrol = c.ButtonControl(Name="")
    if linkcontrol.BoundingRectangle.top < C_MsgList.BoundingRectangle.top:
        # 上滚动
        while True:
            C_MsgList.WheelUp(wheelTimes=1, waitTime=0.1)
            if linkcontrol.BoundingRectangle.top > C_MsgList.BoundingRectangle.top:
                break
    elif linkcontrol.BoundingRectangle.bottom > C_MsgList.BoundingRectangle.bottom:
        # 下滚动
        while True:
            C_MsgList.WheelDown(wheelTimes=1, waitTime=0.1)
            if linkcontrol.BoundingRectangle.bottom < C_MsgList.BoundingRectangle.bottom:
                break
    linkcontrol.Click(simulateMove=False)
    ## 找到标题和链接
    import uiautomation as uia
    class_name = 'Chrome_WidgetWin_0'
    UiaAPI = uia.PaneControl(ClassName=class_name, searchDepth=1)
    title = UiaAPI.TabItemControl().Name
    menu = find_all_children(UiaAPI,
                             lambda a: True if a.ControlTypeName == "MenuItemControl" and a.Name == "更多" else False)
    import win32gui
    HWND = win32gui.FindWindow(class_name, None)
    win32gui.ShowWindow(HWND, 1)
    UiaAPI.SwitchToThisWindow()
    for btn in menu:
        btn.Click()
        child = find_all_children(UiaAPI, lambda a: True if a.Name == "复制链接" else False)
        for c in child:
            c.Click()
    import pyperclip
    url = pyperclip.paste()
    ## 关闭链接页面
    close_btn = find_all_children(UiaAPI, lambda
        a: True if a.ControlTypeName == "ButtonControl" and a.Name == "关闭" else False)
    for btn in close_btn:
        try:
            btn.Click()
        except:
            pass
    result = f"Title:{title}\nURL:{url}"
    print(result)
    return result


import re


def fileprase(wx, user, file_dir):
    wx.ChatWith(user)
    files = find_all_children(wx.ChatBox, lambda a: True if a.Name == "[文件]" else False)[-1]
    texts = find_all_children(files, lambda a: True if a.ControlTypeName == "TextControl" else False)
    result = f"File Name : {texts[0].Name}\n"
    if file_dir:
        result += f"Dir Path : {file_dir}\n"
    return result

# demo
from wxauto import WeChat

wx = WeChat()
linkprase(wx, user='清易')  # 这里改成要获取的人

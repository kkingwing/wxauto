# v0.1 投资策略提醒，企微群，邮件。用于定时于linux
from email.mime.text import MIMEText
import smtplib

from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
import datetime
import os
import requests


class EmailSendToMe:
    def __init__(self, subject, note=None, to_mails_ls=None, to_names_ls=None, attachments_ls=None, att_dir=None):
        # 这里简化为一个「邮件标题subject」，其它参数全写为无，默认接收人为自己，无附件，是可选参数，如有需要可以写。
        self.subject = subject  # 邮件标题，日期已自带，实际效果如： 【运营日报】1102
        self.note = '' if note is None else note  # 附加信息，如：「测试」

        self.to_mails_ls = ['495017921@qq.com', ] if to_mails_ls is None else to_mails_ls  # 'chenqiuyuan@37wxcul.com',
        self.to_names_ls = ['Creator', ] if to_names_ls is None else to_names_ls  # '清易',

        self.att_dir = att_dir  # 要添加的「附件所在的文件夹名称」
        # 判断是否有附件
        if attachments_ls is not None:
            self.att_paths = [os.path.join(self.att_dir, att) for att in attachments_ls]  # 构造所有文件的绝对路径
        else:
            self.att_paths = []

        self.today = datetime.datetime.now().strftime("%m%d")  # 变量初始化
        self.my_add = '495017921@qq.com'  # 固定变量初始化
        self.token = 'uqhzjtugbxefbhch'
        self.my_mail_name = "清易的Robot"  # 发件昵称，注意敏感词右上角的逗号/单引号，会发送失败。

    ###
    # 1.1、添加正文
    ###
    def append_text(self, i, msg):
        # 将正文放入msg中。（3个参数分别是：邮件正文、格式、编码。）
        if len(self.att_paths) > 0:
            self.mail_text = f""" 
                    <p>Dear {self.to_names_ls[i]}：</p>
                    <p>您好，附件为{self.subject}概况，请查看。</p>
                    <p>若手机直接打开附件的观看效果不好，建议使用wps/office等app打开文件查看~</p>
                    <p>（「附件位置」一般位于邮件底部，下滑即可看到。该邮件目前测试运行，若有问题会及时更正。）</p>
                    <p>Best Regards!</p>
                    <p>——————</p>
                    <p></p>
                    <p>秋元</p>
                    <p>18719054374</p>
                    """
        else:
            self.mail_text = f""" 
                    <p>Dear {self.to_names_ls[i]}：</p>
                    <p>{self.note}</p>
                    <p>------------</p>
                    <p>Entering when underrated and exiting when overrated is always a winning strategy<p>            
                    """  # mail_msg是正文内容
        msg.attach(MIMEText(self.mail_text, 'html', 'utf-8'))

    ###
    # 1.2、添加附件
    ###
    def append_att(self, msg, att_path):
        # 添加附件
        att_name = os.path.basename(att_path)  # 取出文件路径的文件名称
        att = MIMEText(open(att_path, 'rb').read(), 'base64', 'gb2312')
        att['Content-Type'] = 'application/octet-stream'
        att.add_header('Content-Disposition', 'attachment', filename=att_name)
        msg.attach(att)

    ###
    # 1.0 （& 1.1 & 1.2）、构造邮件，「实例化，添加正文，添加附件」
    ###
    def create_email(self, i):
        msg = MIMEMultipart()  # 实例化邮件对象
        msg['From'] = formataddr([self.my_mail_name, self.my_add])
        msg['to'] = formataddr([self.to_names_ls[i], self.to_mails_ls[i]])
        msg['Subject'] = rf'【{self.subject}】{self.today}'
        self.append_text(i, msg)
        for att_path in self.att_paths:
            self.append_att(msg, att_path)
        return msg

    ###
    # 2.发送构造好的邮件
    ###
    def send_mail(self, i, msg):
        # 登录服务器发送邮件
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)  # python与授权码通过，若是SMTP此处不用改
        server.login(self.my_add, self.token)  # 模拟登录
        server.sendmail(self.my_add, [self.to_mails_ls[i], ], msg.as_string())  # 邮件发送内容
        server.quit()  # 关闭连接通道

    ###
    # 企微提醒
    ###
    @staticmethod
    def wxrobot(reminder_msg):
        # 企微群通知
        # md_content是markdown的格式
        markdown_msg = (f"{'-' * 10}  定点提醒  {'-' * 10}\n"
                        f'\n\n'
                        f'提醒：<font color="info">{reminder_msg}</font>\n\n'
                        f"\n{'-' * 30}\n")
        headers = {'Content-Type': 'application/json'}
        params = {'key': '1d7f2f23-9a6f-4bf9-b81e-79801fa1faf7'}
        json_data = {"msgtype": "markdown", "markdown": {"content": markdown_msg}}
        res = requests.post('https://qyapi.weixin.qq.com/cgi-bin/webhook/send', params=params, headers=headers,
                            json=json_data)
        print("推送情况", res.text)
        return None

    ###
    # 3.主思路，遍历发送构造好的邮件
    ###
    def run(self):
        self.wxrobot(self.note)  # 企微通知
        for i in range(len(self.to_mails_ls)):  # 遍历收件人邮件通知
            try:
                msg = self.create_email(i)
                self.send_mail(i, msg)
                print(f'发送邮件至第{i + 1}个收件人: {self.to_names_ls[i], self.to_mails_ls[i]} 成功。')
            except Exception as e:
                print(f'发送邮件至第{i + 1}个收件人: {self.to_names_ls[i], self.to_mails_ls[i]} 失败。\n{e}')


if __name__ == '__main__':
    subject = '报错提醒-wxauto'  # 邮件标题（日期已自带，实际效果如： 【运营日报】1102）
    note = """中断出错，详见机器."""
    em1 = EmailSendToMe(subject, note)  # 有附件的实例
    em1.run()

    # 标题可以直接用「调用者的类名」：
    # EmailSendToMe(subject=self.__class__.__name__).run()  # 以类名发送邮件

# 163邮件：User is over flow 当天上传流量超上限，多余时需要另备账号测试（一天约2G）
# (535, b'Error: authentication failed') 端口错误，检查sever
# QQ邮箱：550 Mail content denied ，敏感符号，不能有 ' 标题不能用右上角逗号

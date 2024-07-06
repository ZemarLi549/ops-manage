import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import os
import socket
MAIL_HOST = os.environ.get("MAIL_HOST", "mail.iflytek.com:465")
MAIL_USER = os.environ.get("MAIL_USER", "ccr_paas_postman@iflytek.com")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "UCNES5bC5geVRatG")
def send_mail(to_list, sub, content, subtype='html'):  # to_list：收件人；sub：主题；content：邮件内容
    me = f'AlarmMonitor<{MAIL_USER}>'  # 这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content, _subtype=subtype,_charset='utf-8')  # 创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub  # 设置主题
    msg['From'] = me
    msg['To'] = ", ".join(to_list)
    try:
        # 为了防止邮件发送超时，这里进行了20秒超时配置
        socket.setdefaulttimeout(20)
        s = smtplib.SMTP_SSL(MAIL_HOST)
        # s.connect('mail.iflytek.com',465)  # 连接smtp服务器
        # s.ehlo()  # 向服务器发送扩展 EHLO 命令
        # s.starttls()  # 尝试开启 TLS（即使实际不会使用加密）
        s.login(MAIL_USER, MAIL_PASSWORD)  # 登陆服务器
        s.sendmail(me, to_list, msg.as_string())  # 发送邮件
        s.close()
        print('send ok>>>')
        return True
    except Exception as e:
        print("email error %s" % e)
        return False
to_list = ['zxli22@iflytek.com']
sub = '告警测试'
content = """
<html>
<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"> </haed>
         <body>
         <style>table{font-size:14px;}</style>
         <div align="center">
         <font color="#525252">
           <table border="0" style="border:5px solid #F2F2F2;" cellspacing="2" cellpadding="2" width="600" style="table-layout:fixed">
         <tr bgcolor="#D1D1D1">
         <th align="middle" style="font-size:23px;"><img src="https://pic.imgdb.cn/item/65570357c458853aef6eff2c.jpg" style="width:100%;" contenteditable="false"/></marquee></th>
         </tr>  <tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">告警项名: {ITEM.NAME1}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word"><b>告警主机:</b>{HOST.NAME1}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">告警IP: {HOST.IP1}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">告警项Key值: {ITEM.KEY1}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">告警触发规则:{TRIGGER.EXPRESSION}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">告警时间:{EVENT.DATE} {EVENT.TIME}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">告警等级:{TRIGGER.SEVERITY}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">告警值: {ITEM.VALUE1}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">最新采集值: {{HOSTNAME}:{TRIGGER.KEY}.last(0)}
</td>  </tr>
<tr><td align="left" style="font-family:微软雅黑; size=5" style="WORD-WRAP:break-word">问题描述:{TRIGGER.DESCRIPTION}

</td>  </tr>

                 </table>


                 <p>此邮件为监控平台自动发送，请勿回复!</p>

                 </body>
                 </html>
"""
send_mail(to_list, sub, content, subtype='html')


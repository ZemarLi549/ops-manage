from utils.logger import logger
import smtplib

from email.mime.text import MIMEText
import socket
from ops_alarm.settings import MAIL_HOST,MAIL_USER,MAIL_PASSWORD,OPSMANAGE_DOMAIN
LEVEL_PIC = {
    'disaster':'https://pic.imgdb.cn/item/65570357c458853aef6eff10.jpg',
    'normal':'https://pic.imgdb.cn/item/65570357c458853aef6eff2c.jpg',
    'recovery':'https://pic.imgdb.cn/item/65570357c458853aef6eff42.jpg',
    'serious':'https://pic.imgdb.cn/item/65570357c458853aef6eff6b.jpg',
    'urgent':'https://pic.imgdb.cn/item/65570357c458853aef6eff84.jpg',
}
def send_mail(to_list, sub, content, subtype='html',mail_host=MAIL_HOST,mail_user=MAIL_USER,mail_pwd=MAIL_PASSWORD):  # to_list：收件人；sub：主题；content：邮件内容
    me = f'AlarmMonitor<{mail_user}>'  # 这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content, _subtype=subtype,_charset='utf-8')  # 创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub  # 设置主题
    msg['From'] = me
    msg['To'] = ", ".join(to_list)
    try:
        # 为了防止邮件发送超时，这里进行了20秒超时配置
        socket.setdefaulttimeout(20)
        logger.debug(f'mail_host>>>{mail_host},{mail_user},{mail_pwd}')
        s = smtplib.SMTP_SSL(mail_host)
        # s.connect('mail.iflytek.com',465)  # 连接smtp服务器
        # s.ehlo()  # 向服务器发送扩展 EHLO 命令
        # s.starttls()  # 尝试开启 TLS（即使实际不会使用加密）
        s.login(mail_user, mail_pwd)  # 登陆服务器
        s.sendmail(me, to_list, msg.as_string())  # 发送邮件
        s.close()
        logger.info('mail send ok>>>')
        return True
    except Exception as e:
        logger.error("email error %s" % e)
        return False




def email_send(alarm_list,post_data,userDict):
    try:
        for alarm_detail in alarm_list:
            send_to = alarm_detail.get('send_to',[])
            send_email = alarm_detail.get('send_email','').strip()
            alarm_status = post_data.get('status','firing')
            alarm_id= post_data.get('alarm_id',0)
            identity_freq= post_data.get('identity_freq','不收敛')
            identity_times= post_data.get('identity_times',0)
            recover_cnt= post_data.get('recover_cnt',0)
            deploy_time= post_data.get('deploy_time','0分钟')
            labels = post_data.get('labels',{})

            to_list = []
            for username in send_to:
                to_list.append( f'{userDict[username].get("email","")}')

            logger.info(f'email_send>>>{send_to}')
            logger.debug(f'email to_list>>>{to_list}')
            alarm_severity= labels.get('severity','一般')
            alarm_summary = post_data.get('annotations',{}).get('summary','')
            alarm_desc = post_data.get('annotations',{}).get('description','')

            alarm_img = LEVEL_PIC['normal']
            alarm_title_color = '#367fff'
            if alarm_status=='resolved':
                alarm_img = LEVEL_PIC['recovery']
                alarm_title_color = '#59ae6b'
            elif alarm_severity=='一般':
                alarm_img = LEVEL_PIC['normal']
                alarm_title_color = '#367fff'
            elif alarm_severity=='严重':
                alarm_img = LEVEL_PIC['serious']
                alarm_title_color = '#fdb408'
            elif alarm_severity=='紧急':
                alarm_img = LEVEL_PIC['urgent']
                alarm_title_color = '#fe2909'
            elif alarm_severity=='灾难':
                alarm_img = LEVEL_PIC['disaster']
                alarm_title_color = '#fe2909'
            else:
                alarm_img = LEVEL_PIC['normal']
                alarm_title_color = '#367fff'







            sub = alarm_summary
            content = f"""
            <html>
            <head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"> </haed>
                    <body>
                    <style>table</style>
                    <div align="center">
                    <font color="#525252">
                    <table border="0" style="border:5px solid #F2F2F2;font-size:14px;" cellspacing="2" cellpadding="2" width="400" style="table-layout:fixed">
                    <tr bgcolor="#D1D1D1">
                    <th align="middle" style="font-size:23px;"><img src="{alarm_img}" style="width:100%;" contenteditable="false"/></marquee></th>
                    </tr>  <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>时间: </b>{post_data.get('startsAt','')}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>指纹ID：</b>{alarm_id}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>告警ID: </b>{labels.get('id','')}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>告警次数：</b>{identity_times}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>恢复次数：</b>{recover_cnt}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>处理时间：</b>{deploy_time}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>告警间隔：</b>{identity_freq}
            </td>  </tr>
            <tr><td align="left" style="color:{alarm_title_color};font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>告警名称：</b>{labels.get('alertname','')}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>项目组件：</b>{labels.get('job','')}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>来源: </b>{labels.get('source','')}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>分组: </b>{labels.get('group','')}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>实例: </b>{labels.get('instance','')}
            </td>  </tr>
            <tr><td align="left" style="color:{alarm_title_color};font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>主题：</b>{alarm_summary}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; " style="WORD-WRAP:break-word"><b>详情：</b>{alarm_desc}
            </td>  </tr>
            <tr><td align="left" style="font-family:微软雅黑; size=10" style="WORD-WRAP:break-word"><a target="_blank" href="{OPSMANAGE_DOMAIN}/#/alarmdetail?alarmid={alarm_id}">[告警详情]</a>
                    <a target="_blank" href="{OPSMANAGE_DOMAIN}/#/alarmedit?alarmid={alarm_id}">[告警处理]</a>

            </td>  </tr>

                            </table>


                            <p>此邮件为监控平台自动发送，请勿回复!</p>

                            </body>
                            </html>
            """

            mail_host=MAIL_HOST
            mail_user=MAIL_USER
            mail_pwd=MAIL_PASSWORD
            if send_email:
                try:
                    mail_host,mail_user,mail_pwd = send_email.split('|#|')
                except:
                    logger.error('send_email format err')
            send_mail(to_list, sub, content,'html',mail_host,mail_user,mail_pwd)
    except Exception as e:
        logger.error(f'send email err>>>{e}')
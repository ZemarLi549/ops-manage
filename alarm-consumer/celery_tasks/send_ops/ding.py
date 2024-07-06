from utils.logger import logger
import requests
from urllib.parse import quote
from ops_alarm.settings import OPSMANAGE_DOMAIN
import json
LEVEL_PIC = {
    'disaster':'https://pic.imgdb.cn/item/65570357c458853aef6eff10.jpg',
    'normal':'https://pic.imgdb.cn/item/65570357c458853aef6eff2c.jpg',
    'recovery':'https://pic.imgdb.cn/item/65570357c458853aef6eff42.jpg',
    'serious':'https://pic.imgdb.cn/item/65570357c458853aef6eff6b.jpg',
    'urgent':'https://pic.imgdb.cn/item/65570357c458853aef6eff84.jpg',
}
def ding_send(alarm_list,post_data,userDict):
    try:
        for alarm_detail in alarm_list:
            send_to = alarm_detail.get('send_to',[])
            logger.info(f'ding_send>>>{send_to}')
            webhook_url = alarm_detail.get('robot_url','').strip()
            alarm_status = post_data.get('status','firing')
            alarm_id= post_data.get('alarm_id',0)
            identity_freq= post_data.get('identity_freq','不收敛')
            identity_times= post_data.get('identity_times',0)
            recover_cnt= post_data.get('recover_cnt',0)
            deploy_time= post_data.get('deploy_time','0分钟')
            labels = post_data.get('labels',{})
            phones = []
            for username in send_to:
                phones.append(userDict[username].get("phone",""))
            logger.debug(f'phones>>>{phones}')

            # alarm_title = '告警触发'
            # alarm_title_color = 'warning'
            # if alarm_status=='resolved':
            #     alarm_title = '告警恢复'
            #     alarm_title_color = 'green'

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
            # url = 'https://oapi.dingtalk.com/robot/send?access_token='
            # uri = url+group
            headers = {
                'content-type': 'application/json',
                'User-Agent': 'Mozilla/5.0(X11;Ubuntu;Linux x86_64;rv:22.0) Gecko/20100101 Firefox/22.0'
            }
            phonename = '@'.join(phones)
            contents = alarm_desc+'\n@'+phonename
            try:
                contents = alarm_desc.replace('\\n', '\n\n').replace('\n', '\n\n')
            except:pass

            alarm_id = labels.get('identity_id','')

            detail_link_url = f'{OPSMANAGE_DOMAIN}/#/alarmdetail?alarmid={alarm_id}'
            note_link_url = f'{OPSMANAGE_DOMAIN}/#/alarmedit?alarmid={alarm_id}'
            detail_link_url = quote(detail_link_url, safe='', encoding="utf-8")
            note_link_url = quote(note_link_url, safe='', encoding="utf-8")
            post_data = {
                "msgtype": "markdown",
                "markdown": {
                    "title":f"{labels.get('alertname','')}",
                    "text": f"""![screenshot]({alarm_img})\n
            \n **告警时间**：{post_data.get('startsAt','')}
            \n **指纹ID**：{alarm_id}
            \n **告警ID**：{labels.get('id','')}
            \n **告警次数**：{identity_times}
            \n **恢复次数**：{recover_cnt}
            \n **处理时间**：{deploy_time}
            \n **告警间隔**：{identity_freq}
            \n **告警级别**：{alarm_severity}
            \n **告警名称**：{labels.get('alertname','')}
            \n **项目组件**：{labels.get('job','')}
            \n **来源**：{labels.get('source','')}
            \n **分组**：{labels.get('group','')}
            \n **实例**：{labels.get('instance','')}
            \n **主题**：{alarm_summary}
            \n **告警内容**：
            \n{contents}
            \n___
            \n [**告警详情**](dingtalk://dingtalkclient/page/link?pc_slide=true&url={detail_link_url})&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[**告警处理**](dingtalk://dingtalkclient/page/link?pc_slide=true&url={note_link_url})""",
                },
                "at": {
                    "atMobiles": [
                        phones
                    ],
                    "atUserIds": [
                        "user123"
                    ],
                    "isAtAll": False
                }
            }

            try:
                requests.post(webhook_url, headers=headers, data=json.dumps(post_data))
                return True
            except Exception as e:
                logger.error("[创建钉钉失败：%s]" % e)
                return False
            pass
    except Exception as e:
        logger.error(f'send dingding err>>>{e}')
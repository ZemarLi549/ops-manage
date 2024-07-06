from utils.logger import logger
import requests
from urllib.parse import quote,unquote
from ops_alarm.settings import OPSMANAGE_DOMAIN,SMS_URL,SMS_PASS
def sendsms(phones, content):
    try:
        sms_send_url = SMS_URL
        paltform_pass = SMS_PASS
        msg = unquote(content)
        payload = {'uuid': paltform_pass,
               'params': str([msg]),
               'type_num': '2',
               'iphone': str(phones)}
        headers = {}
        files = []
        r = requests.request(
            "POST", sms_send_url, headers=headers, data=payload, files=files)
        logger.info(f"smsresp>>>{r.text}")
    except Exception as e:
        logger.error(f"sms send err>>>{e}")
def sms_send(alarm_list,post_data,userDict):
    try:
        for alarm_detail in alarm_list:
            send_to = alarm_detail.get('send_to',[])
            logger.info(f'sms_send>>>{send_to}')
            alarm_status = post_data.get('status','firing')
            alarm_id= post_data.get('alarm_id',0)
            identity_freq= post_data.get('identity_freq','不收敛')
            identity_times= post_data.get('identity_times',0)
            recover_cnt= post_data.get('recover_cnt',0)
            deploy_time= post_data.get('deploy_time','0分钟')
            labels = post_data.get('labels',{})
            alarm_severity= labels.get('severity','一般')
            alarm_summary = post_data.get('annotations',{}).get('summary','')
            alarm_desc = post_data.get('annotations',{}).get('description','')
            alarm_title = '告警触发'
            if alarm_status=='resolved':
                alarm_title = '告警恢复'
            phones = []
            for username in send_to:
                phones.append(userDict[username].get("phone",""))
            logger.debug(f'phones>>>{phones}')
            detail_link_url = f'{OPSMANAGE_DOMAIN}/#/alarmdetail?alarmid={alarm_id}'
            note_link_url = f'{OPSMANAGE_DOMAIN}/#/alarmedit?alarmid={alarm_id}'
            contents = f'''[{alarm_title}]|告警名称:{labels.get('alertname','')}|级别:{alarm_severity}|项目组件:{labels.get('job','')}|主题:{alarm_summary}|实例:{labels.get('instance','')}|告警ID:{labels.get('id','')}|告警次数:{identity_times}|恢复次数:{recover_cnt}|详情:({detail_link_url})|处理:({note_link_url})'''
            print(contents)
            sendsms(phones, quote(contents,safe='', encoding="utf-8"))
    except Exception as e:
        logger.error(f'send sms err>>>{e}')
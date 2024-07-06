from utils.logger import logger
import requests
from ops_alarm.settings import OPSMANAGE_DOMAIN
import json
def send_wechat(webhook_url,content):
    resp = requests.post(webhook_url,data=json.dumps(content))
    logger.debug(resp.text)
def wechat_send(alarm_list,post_data,userDict):
    try:
        for alarm_detail in alarm_list:
            send_to = alarm_detail.get('send_to',[])
            logger.info(f'wechat_send>>>{send_to}')
            webhook_url = alarm_detail.get('robot_url','').strip()
            alarm_status = post_data.get('status','firing')
            alarm_id= post_data.get('alarm_id',0)
            identity_freq= post_data.get('identity_freq','不收敛')
            identity_times= post_data.get('identity_times',0)
            recover_cnt= post_data.get('recover_cnt',0)
            deploy_time= post_data.get('deploy_time','0分钟')
            labels = post_data.get('labels',{})
            alarm_at = ''
            for username in send_to:
                alarm_at+= f'<@{userDict[username].get("name","")}>'
            logger.debug(f'alarm_at>>>{alarm_at}')

            alarm_title = '告警触发'
            alarm_title_color = 'warning'
            if alarm_status=='resolved':
                alarm_title = '告警恢复'
                alarm_title_color = 'green'


            alarm_severity= labels.get('severity','一般')
            alarm_summary = post_data.get('annotations',{}).get('summary','')
            alarm_desc = post_data.get('annotations',{}).get('description','')


            content_msg = {
            "msgtype": "markdown",
                "markdown": {
                    "content": f'''# <font color="{alarm_title_color}">【{alarm_title}】</font>
    >时间：<font color="comment">{post_data.get('startsAt','')}</font>
    >指纹ID：<font color="comment">{alarm_id}</font>
    >告警ID：<font color="comment">{labels.get('id','')}</font>
    >告警次数：<font color="comment">{identity_times}</font>
    >恢复次数：<font color="comment">{recover_cnt}</font>
    >处理时间：<font color="comment">{deploy_time}</font>
    >告警间隔：<font color="comment">{identity_freq}</font>
    >告警级别：**<font color="warning">{alarm_severity}</font>**
    >告警名称：**<font color="{alarm_title_color}">{labels.get('alertname','')}</font>**
    >项目组件：<font color="comment">{labels.get('job','')}</font>
    >来源: <font color="comment">{labels.get('source','')}</font>
    >分组: <font color="comment">{labels.get('group','')}</font>
    >实例: <font color="comment">{labels.get('instance','')}</font>
    >主题：<font color="{alarm_title_color}">{alarm_summary}</font>
    >详情：<font color="comment">{alarm_desc}</font>
    >[告警详情]({OPSMANAGE_DOMAIN}/#/alarmdetail?alarmid={alarm_id})        [告警处理]({OPSMANAGE_DOMAIN}/#/alarmedit?alarmid={alarm_id})\n
    {alarm_at}''',
                }
            }
            send_wechat(webhook_url,content_msg)
    except Exception as e:
        logger.error(f'send wechat err>>>{e}')
from utils.logger import logger
from utils.redisclient import get_user_info
from concurrent.futures import ThreadPoolExecutor
import copy
from celery_tasks.send_ops.wechat import wechat_send
from celery_tasks.send_ops.ding import ding_send
from celery_tasks.send_ops.sms import sms_send
from celery_tasks.send_ops.phone import phone_send
from celery_tasks.send_ops.email import email_send
import time
from utils.redisclient import has_identity_json
def send_task(alarm_to,post_data,kv_md5=None):
    logger.debug(f'send_task>>>{post_data}')
    customSend = post_data.get('customSend',{})
    if customSend:
        alarm_to = customSend
    if kv_md5:
        time.sleep(1.4)
        identity_info = has_identity_json(kv_md5)
        print('identitu_times>>>',int(identity_info.get('times',0)))
        print('recover_cnt>>>',int(identity_info.get('recover_cnt',0)))
        identity_times = int(identity_info.get('times',post_data['identity_times']))
        recover_cnt = int(identity_info.get('recover_cnt',post_data['recover_cnt']))
        post_data['identity_times'] = identity_times
        post_data['recover_cnt'] = recover_cnt
    #去重一次性 获取所有联系人 联系方式
    send_to_set = set()
    for alarm_type,alarm_list in alarm_to.items():
        for alarm_detail in alarm_list:
            send_to = alarm_detail.get('send_to')
            for username in send_to:
                send_to_set.add(username)
    userDict = {}
    logger.debug(f'send_to_set>>>{send_to_set}')
    for username in send_to_set:
        userinfo = get_user_info(username)
        userDict[username] = userinfo
    logger.debug(f'userDict>>>{userDict}')
    send_action = sendAction(userDict)
    send_action.send_start(alarm_to,post_data)


def send_alarm(alarm_type,alarm_list,post_data,userDict):
    alarm_data = copy.deepcopy(post_data)
    if alarm_type=='wechat':
        wechat_send(alarm_list,alarm_data,userDict)
    elif alarm_type=='sms':
        sms_send(alarm_list,alarm_data,userDict)
    elif alarm_type=='phone':
        phone_send(alarm_list,alarm_data,userDict)
    elif alarm_type=='ding':
        ding_send(alarm_list,alarm_data,userDict)
    elif alarm_type=='email':
        email_send(alarm_list,alarm_data,userDict)
class sendAction():
    def __init__(self,userDict):
        self.userDict = userDict
    def send_start(self,alarm_to,post_data):
        #多线程异步执行 各个方式的告警
        pp_executor= ThreadPoolExecutor(5)
        futures = []
        for alarm_type,alarm_list in alarm_to.items():
            pp_executor_callback=pp_executor.submit(send_alarm ,alarm_type,alarm_list,post_data,self.userDict)
            futures.append(pp_executor_callback)
        for future in futures:
            result = future.result()  # 获取每个任务的结果
            print(f"send Task result: {result}")



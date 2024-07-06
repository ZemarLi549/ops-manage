from celery_tasks.celery import app
from utils.logger import logger
from utils.helpers import decrypt
from utils.redisclient import release_lock,acquire_lock,get_rule_info,has_identity_key,set_identity_key,has_identity_json,set_identity_json,has_status_key,set_status_key
import time
import re
import json
import hashlib
from utils.dbtool import MysqlOp
from datetime import datetime
from celery_tasks.es_save import save_alarm
from celery_tasks.send_ops import send_task
from concurrent.futures import ThreadPoolExecutor,as_completed
from ops_alarm.settings import RESOLVED_TIME
import traceback
import random

@app.task(name='om_consumer_start')
def om_consumer_start(**kwargs):
    '''
    发送告警队列
    '''
    logger.info('%s:kwargs:%s' % ('worker_om_deploy_post', kwargs))
    post_data = decrypt(kwargs['post_data'])
    logger.info(f'consumer recv>>>>{post_data}')
    beg_time = datetime.now()
    try:
        start_deploy_alarm(post_data)
    except Exception as e:
        logger.error(f'start_deploy_alarm err>>>{str(traceback.format_exc())}')


    end_time = datetime.now()
    time_dtt = str((end_time - beg_time).total_seconds())
    logger.info(f'start_deploy_alarm 耗时>>>{time_dtt}')
    return f'start ok:{kwargs.get("id",0)}'


def get_identity_tag(rule_info,post_data):
    logger.debug(f'rule_info>>{rule_info}')
    identity_tag_kv = dict()
    # identity_tag_kv = collections.OrderedDict()
    extra = post_data.get("labels", {})
    rule_keys = rule_info.get("rule_keys", '').strip()
    re_str = rule_info.get("rule_re", '').strip()
    annotations = post_data.get('annotations',{})
    content = f"summary:{annotations.get('summary','')},description:{annotations.get('description','')}"
    logger.debug(f're_str>>{re_str}')
    for i in re_str.split('|#|'):
        if i:
            str_ls = i.split('&&')
            if len(str_ls)>=2:
                regex_str = str_ls[1]
                keyword = str_ls[0]
            else:
                regex_str = str_ls[0]
                keyword = str_ls[0]
            try:
                text_filter = re.search(regex_str, content)
            except:text_filter = None

            if text_filter:
                if len(str_ls) >= 2:
                    key_identity = keyword
                else:
                    key_identity = keyword.replace('"', '').replace("'", "").replace("{", "").replace("}", "").replace(")", "").replace("(", "").replace(":", "").replace("*", "").replace(".", "").replace("?", "").replace("^", "").replace("$", "").replace("[", "").replace("]", "")[:10]
                if text_filter.groups():
                    identity_tag_kv[key_identity] = text_filter.groups()[0]
                else:
                    try:
                        identity_tag_kv[key_identity] = text_filter.group()
                    except:pass


    for k, v in extra.items():
        if k in rule_keys:
            identity_tag_kv[k] = v
    # 按照键排序
    sorted_keys = sorted(identity_tag_kv.keys())
    # 创建一个新的有序字典
    sorted_tag_kv = {key: identity_tag_kv[key] for key in sorted_keys}
    logger.debug(f"identity_tag:{sorted_tag_kv}")
    kv_md5 = hashlib.md5(json.dumps(sorted_tag_kv,ensure_ascii=False).encode(encoding='utf-8')).hexdigest()
    return kv_md5,sorted_tag_kv
def deploy_freq(freq):
    try:
        freq_ls = freq.split(',')
        freq_num = freq_ls[0]
        freq_unit = freq_ls[1]
        if freq_unit == 'infinity':
            expire_time = 31556952
        elif freq_unit == 'minutes':
            expire_time = int(freq_num)*60
        elif freq_unit == 'hours':
            expire_time = int(freq_num)*60*60
        elif freq_unit == 'days':
            expire_time = int(freq_num)*60*60*24
        else:
            expire_time = 60*10
    except Exception as e:
        expire_time = 60*10
    return expire_time
def get_deploy_time(init_time,now_time):
    dt1 = datetime.strptime(init_time, '%Y-%m-%d %H:%M:%S')
    dt2 = datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
    diff = abs(dt1 - dt2)

    if diff.days > 0:
        return f"{diff.days}天"
    elif diff.seconds // 3600 > 0:
        return f"{diff.seconds // 3600}小时"
    elif diff.seconds // 60 > 0:
        return f"{diff.seconds // 60}分钟"
    else:
        return f"{diff.seconds}秒"

def update_mysql(table_name,update_data,condition):
    MysqlOp().update_info(table_name,update_data,condition)

def start_deploy_alarm(post_data):
    #在web端定义了，不在时间段不会发消息的
    # nowtime = time.strftime("%H:%M")
    # alert_start = post_data.get('alert_start','00:00')
    # alert_end = post_data.get('alert_end','23:59')
    # #在告警时间段内
    # if alert_start <= nowtime and nowtime <= alert_end:
    #     pass



    if 'alarm_id_dict' in post_data.keys():
        alarm_id_dict = post_data.pop('alarm_id_dict')
    else:
        alarm_id_dict = {}
    post_data['labels']['alarm_status'] = post_data.get('status','firing')
    rule_name = alarm_id_dict.get('rule_name')
    mustAlert = post_data.get('mustAlert',False)
    startsAt = post_data.get('startsAt',time.strftime('%Y-%m-%d %H:%M:%S'))
    deploy_time = '0分钟'
    ignoreAlert = False
    send_alert_flag = True
    recordIgnore = True
    #多线程异步执行发送告警和存储告警任务
    pp_executor= ThreadPoolExecutor(5)
    futures = []
    kv_md5 = None
    if rule_name:
        #有收敛
        rule_info = get_rule_info(rule_name)
        alarm_status =  post_data.get('status','firing')
        freq = rule_info.get('freq')
        resovle_freq = rule_info.get('resovle_freq')
        expire_time = deploy_freq(freq)
        resolve_expire_time = deploy_freq(resovle_freq)
        rate = rule_info.get('rate',1)
        kv_md5,identity_tag_kv = get_identity_tag(rule_info,post_data)

        #判断有无锁
        # while True:
        #     isMysqlDeploying = has_status_key(kv_md5)
        #     if not isMysqlDeploying:
        #         break
        #     time.sleep(random.uniform(0.1, 0.5))
        #     logger.warning(f'redis有锁>>>mysqldeploy:{kv_md5},val:{isMysqlDeploying}')
        identifier = acquire_lock(f'mysqldeploy:{kv_md5}')
        if identifier:   # 如果获取到锁,则执行业务逻辑
            # print(f'获取 redis 分布式锁成功！')
            try:
                identity_info = has_identity_json(kv_md5)
                identity_times = 0
                recover_cnt = 0
                # if not identity_list:
                if not identity_info:
                    #不存在相同指纹,第一次告警
                    post_data['execution'] = '发送告警'
                    set_identity_key(kv_md5,expire_time)
                    insert_data = {
                        "identity":kv_md5,
                        "identity_tag_kv":json.dumps(identity_tag_kv),
                        "times":0,
                        "score":rate,
                        "status":4,
                        "recover_cnt":0,
                        "created_at":time.strftime('%Y-%m-%d %H:%M:%S'),
                        "updated_at":time.strftime('%Y-%m-%d %H:%M:%S'),
                        "created_by":'sys',
                        "updated_by":'sys',
                        "record_ignore":1,
                    }

                    if alarm_status=='resolved':
                        recover_cnt+=1
                    else:
                        identity_times+=1
                    insert_data['times'] = identity_times
                    insert_data['recover_cnt'] = recover_cnt
                    identity_score = rate
                    if alarm_status=='resolved':
                        insert_data['status'] = 5


                    mysql_op = MysqlOp()
                    alarm_id = mysql_op.insert_info('alarm_identity',insert_data)
                    identity_json = {
                        'id':alarm_id,
                        'times':insert_data['times'],
                        'recover_cnt':insert_data['recover_cnt'],
                        'score':insert_data['score'],
                        'status':insert_data['status'],
                        'ignore_to':None,
                        'record_ignore':insert_data['record_ignore'],
                        'created_at':insert_data['created_at'],
                    }
                    set_identity_json(kv_md5,identity_json)
                else:
                    #存在未消除的相同指纹
                    # identity_info = identity_list[0]
                    deploy_time = get_deploy_time(identity_info['created_at'],time.strftime('%Y-%m-%d %H:%M:%S'))
                    identity_times = int(identity_info.get('times',0))
                    identity_score = int(identity_info['score'])
                    recover_cnt = identity_info.get('recover_cnt')
                    if not recover_cnt:
                        recover_cnt = 0
                    else:
                        recover_cnt = int(recover_cnt)
                    alarm_id = identity_info['id']
                    status = identity_info.get('status',1)

                    ignore_to = identity_info.get('ignore_to','')
                    ignore_expire = False
                    if ignore_to:
                        try:
                            if datetime.strptime(startsAt, '%Y-%m-%d %H:%M:%S')<datetime.strptime(ignore_to, '%Y-%m-%d %H:%M:%S'):
                                ignore_expire = True
                        except Exception as e:
                            logger.error(f'ignore_to err:{e}')
                    else:
                        #不填则忽略
                        ignore_expire = True
                    if int(status)==3 and ignore_expire:
                        #忽略告警
                        send_alert_flag = False
                        ignoreAlert = True
                        recordIgnore = identity_info.get('record_ignore',True)
                    else:
                        #自动恢复告警 另外设置收敛10min
                        if alarm_status=='resolved':
                            recover_cnt+=1
                            #判断是发送告警还是折叠告警
                            identity_exists = has_identity_key(kv_md5,prefix='alarm_resolved')
                            if identity_exists:
                                post_data['execution'] = '折叠告警'
                                send_alert_flag = False
                            else:
                                set_identity_key(kv_md5,resolve_expire_time,prefix='alarm_resolved')
                                post_data['execution'] = '发送告警'
                            update_data = {
                                "id":int(alarm_id),
                                "status":5,
                                "recover_cnt":recover_cnt,
                                "updated_at":time.strftime('%Y-%m-%d %H:%M:%S'),
                            }
                            identity_info.update(update_data)
                            set_identity_json(kv_md5,identity_info)
                            # pp_executor_callback_save=pp_executor.submit(update_mysql ,'alarm_identity',update_data,f'where id={int(alarm_id)}')
                            # futures.append(pp_executor_callback_save)
                            update_mysql('alarm_identity',update_data,f'where id={int(alarm_id)}')
                        else:
                            #告警触发
                            identity_times+=1
                            #判断是发送告警还是折叠告警
                            identity_exists = has_identity_key(kv_md5)
                            if identity_exists:
                                post_data['execution'] = '折叠告警'
                                send_alert_flag = False
                            else:
                                set_identity_key(kv_md5,expire_time)
                                post_data['execution'] = '发送告警'

                            update_data = {
                                "id":int(alarm_id),
                                "times":identity_times,
                                "score":identity_score+rate,
                                "updated_at":time.strftime('%Y-%m-%d %H:%M:%S'),
                            }
                            #自动恢复的告警 再告警回退 未处理
                            if int(identity_info['status']) == 5:
                                update_data['status'] = 4

                            identity_info.update(update_data)
                            set_identity_json(kv_md5,identity_info)
                            # pp_executor_callback_save=pp_executor.submit(update_mysql ,'alarm_identity',update_data,f'where id={int(alarm_id)}')
                            # futures.append(pp_executor_callback_save)
                            update_mysql('alarm_identity',update_data,f'where id={int(alarm_id)}')
                post_data['alarm_id'] = alarm_id
                post_data['identity_tag_kv'] = identity_tag_kv
                post_data['identity'] = kv_md5
                post_data['identity_times'] = identity_times
                post_data['identity_score'] = identity_score
                post_data['identity_freq'] = freq
                post_data['deploy_time'] = deploy_time
                post_data['recover_cnt'] = recover_cnt
            except Exception as e:
                logger.error(f'deploy identity err:{e}')
            res = release_lock(f'mysqldeploy:{kv_md5}', identifier)   # 处理完之后释放锁
            logger.info(f'锁释放状态: {res}')
        else:
            logger.warning(f'获取redis分布式锁失败, 其他进程正在使用')
        #从mysql并发有问题，改成redis
        # get_res_sql = f'select `id`,`times`,`recover_cnt`,`score`,`status`,`ignore_to`,`record_ignore`,`created_at` from alarm_identity where status!=0 and identity=%s'
        # mysql_op = MysqlOp()
        # identity_list = mysql_op.mysql_dict_query(get_res_sql, [kv_md5])

        #加锁
        # set_status_key(kv_md5,1)

        # finally:
        #     set_status_key(kv_md5,0)

    else:
        #无收敛，一般告警
        post_data['alarm_id'] = 0
        post_data['execution'] = '一般告警'
        post_data['identity_tag_kv'] = {}
        post_data['identity'] = 'null'
        post_data['identity_times'] = 0
        post_data['identity_score'] = 1
        post_data['identity_freq'] = '不收敛'
        post_data['deploy_time'] = deploy_time
        post_data['recover_cnt'] = 0
        if alarm_status=='resolved':
            post_data['recover_cnt'] = 1
        else:
            post_data['identity_times'] = 1


    if mustAlert:
        post_data['execution'] = '必须告警'
        send_alert_flag = True

    if ignoreAlert:
        post_data['execution'] = '忽略告警'
        send_alert_flag = False

    send_type= alarm_id_dict.get('send_type','common')
    label_name= alarm_id_dict.get('label_name','source')
    label_send= alarm_id_dict.get('label_send',[])
    label_send_dict = {}
    for labelDict in label_send:
        label_val = labelDict.get('label_val','')
        label_alarm_to = labelDict.get('label_alarm_to',{})
        if label_val and (not label_val in label_send_dict.keys()):
            label_send_dict[label_val] = label_alarm_to
    label_send = label_send_dict
    alarm_to = alarm_id_dict.get('alarm_to',{})
    print('label_send>>>',label_send)
    if send_type=='label_alarm':
        #分label 告警
        labelsDict = post_data.get('labels',{})
        label_val = labelsDict.get(label_name,'')
        if label_val:
            label_alarm_to = label_send.get(label_val,{})
            if not label_alarm_to:
                #试试从 default 获取
                label_alarm_to = label_send.get('default',{})
            if label_alarm_to:
                alarm_to = label_alarm_to
    print('alarm_to>>>',alarm_to)
    if send_alert_flag:
        #发送告警
        pp_executor_callback=pp_executor.submit(send_task ,alarm_to,post_data,kv_md5)
        futures.append(pp_executor_callback)
    if recordIgnore:
        pp_executor_callback_save=pp_executor.submit(save_alarm ,alarm_to,post_data)
        futures.append(pp_executor_callback_save)
    for future in futures:
        result = future.result()  # 获取每个任务的结果
        # logger.info(f"Task result: {result}")




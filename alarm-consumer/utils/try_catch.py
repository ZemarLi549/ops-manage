# -*-coding:utf-8-*-
import logging
import traceback
from utils.dbtool import MysqlOp
from datetime import datetime
from functools import wraps
import json

logger = logging.getLogger(__name__)

def get_next_run(Itemplate,Itask_en,edgeLabel):
    next_run = ''
    bak_next = ''
    i = 0
    for item in Itemplate:
        if item.get('source'):
            if item['source']['cell']==Itask_en:
                i+=1
                if edgeLabel:
                    bak_next = item['target']['cell']
                    if item.get('label','')==edgeLabel:
                        next_run = item['target']['cell']
                else:
                    next_run = item['target']['cell']
    if i>=2 and (not edgeLabel):
        next_run = ''
    if i==1 and (not next_run):
        next_run = bak_next
    return next_run

def try_task(func):
    func_name = func.__qualname__
    task_en = func_name.split('.')[-1]
    @wraps(func)
    def _do_try_catch(*args, **params):
        self_ = args[0]
        try:
            beg_time = datetime.now()
            started_at = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            data_start = {'started_at': started_at,'updated_at':started_at, 'status': 'running','updated_by':self_.login_user}
            MysqlOp().update_info('s_task', data_start, f" where task_en='{task_en}' and dag_id='{self_.dag_id}'")
            #backDict = {'edgeLabel':'','variable':{}}
            backDict = func(*args, **params)
            next_run =get_next_run(self_.template,task_en,backDict.get('edgeLabel',''))
            end_time = datetime.now()
            updated_at = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            status = backDict.get('status','success')
            task_data_end = {'updated_at': updated_at, 'status': status,'next_run':next_run}
            variable = backDict.get('variable')
            sub_variable = backDict.get('sub_variable')
            if variable:
                variable = json.dumps(variable)
                variable = variable.replace('\\','\\\\')
                task_data_end['variable'] = variable
            if sub_variable:#子task结果存储
                sub_variable = json.dumps(sub_variable)
                sub_variable = sub_variable.replace('\"', '\\"')
                task_data_end['sub_variable'] = sub_variable
            MysqlOp().update_info('s_task', task_data_end, f" where task_en='{task_en}' and dag_id='{self_.dag_id}'")
            time_dtt = str((end_time - beg_time).total_seconds())
            self_.logger.info('func: %s, cost:%s s' % (task_en, time_dtt))
            if status=='failed':
                data_dag = {'updated_at': updated_at, 'status': 'failed'}
                MysqlOp().update_info('s_dag', data_dag, f" where dag_id='{self_.dag_id}'")
                raise Exception(f'{task_en} run failed')
            return next_run
        except Exception as e:
            self_.logger.error(f'{task_en} run failed:{str(traceback.format_exc())}')
            updated_at = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            data_end = {'updated_at': updated_at, 'status': 'failed'}
            MysqlOp().update_info('s_task', data_end, f" where task_en='{task_en}' and dag_id='{self_.dag_id}'")

            data_dag = {'updated_at': updated_at, 'status': 'failed'}
            MysqlOp().update_info('s_dag', data_dag, f" where dag_id='{self_.dag_id}'")
            raise Exception(f'{task_en} run failed')

    return _do_try_catch
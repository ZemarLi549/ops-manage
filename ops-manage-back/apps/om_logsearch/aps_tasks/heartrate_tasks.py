import datetime
import logging
from apps.common.redisclient import acquire_lock_once,release_lock
import time
from apps.common.dbopr import dict_query
from apps.common.mysql_dao import MysqlOp
logger = logging.getLogger(__name__)


def remove_ignore_filter_job():
    redis_key = 'aps_log_filter_task'
    identifier = acquire_lock_once(redis_key)
    if identifier:
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            logger.info('remove_ignore_filter_job start! - [%s]' % now_time)
        except Exception as e:
            logger.error(f'ignore_task exe err:{e}')
        finally:
            res = release_lock(redis_key, identifier)
            if not res:
                logger.error(f'aps_ignore_task锁释放状态: {res}')
        params = []
        mysql_op = MysqlOp()


        params = []
        gate_remove_list = mysql_op.mysql_dict_query('select id,end_time from l_gatepass where (end_time IS NOT NULL)', [*params])

        for black_info in gate_remove_list:
            end_time = black_info['end_time']
            if now_time >= end_time:
                black_id = black_info['id']
                logger.info(f'start remove end_time id:{black_id}')
                mysql_op.mysql_other_op(f'delete from l_gatepass where id={black_id}')

        app_remove_list = mysql_op.mysql_dict_query('select id,end_time from l_apppass where (end_time IS NOT NULL)',
                                                      [*params])
        for black_info in app_remove_list:
            end_time = black_info['end_time']
            if now_time >= end_time:
                black_id = black_info['id']
                logger.info(f'start remove end_time id:{black_id}')
                mysql_op.mysql_other_op(f'delete from l_apppass where id={black_id}')
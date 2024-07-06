import datetime
import logging
from apps.common.redisclient import acquire_lock_once,release_lock
import time
from apps.common.dbopr import dict_query
from apps.common.mysql_dao import MysqlOp
logger = logging.getLogger(__name__)


def remove_ignore_black_job():
    redis_key = 'aps_ignore_task'
    identifier = acquire_lock_once(redis_key)
    if identifier:
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            logger.info('remove_ignore_black_job start! - [%s]' % now_time)
        except Exception as e:
            logger.error(f'ignore_task exe err:{e}')
        finally:
            res = release_lock(redis_key, identifier)
            if not res:
                logger.error(f'aps_ignore_task锁释放状态: {res}')
        params = []
        mysql_op = MysqlOp()
        #指纹忽略状态修改
        ignore_identity_list = mysql_op.mysql_dict_query('select id,ignore_to from alarm_identity where status=3 and (ignore_to IS NOT NULL)',[*params])

        for identity_info in ignore_identity_list:
            ignore_to = identity_info['ignore_to']
            if now_time>=ignore_to:
                identity_id = identity_info['id']
                logger.info(f'start modify ignore id:{identity_id}')
                update_info = {
                    'status':4,
                    'ignore_to':None,
                }
                mysql_op.update_info('alarm_identity',update_info, f' where id={identity_id}')
        #黑名单截至去除
        params = []
        black_remove_list = mysql_op.mysql_dict_query('select id,black_to from alarm_black where (black_to IS NOT NULL)', [*params])

        for black_info in black_remove_list:
            black_to = black_info['black_to']
            if now_time >= black_to:
                black_id = black_info['id']
                logger.info(f'start remove black_to id:{black_id}')
                mysql_op.mysql_other_op(f'delete from alarm_black where id={black_id}')
from celery import Celery
from dotenv import load_dotenv
load_dotenv(verbose=True)
import os
REDIS_HOST=os.environ.get('REDIS_HOST','10.110.1.17')
REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD','pieceloveredis')
REDIS_PORT=os.environ.get('REDIS_PORT',6380)
REDIS_DB=os.environ.get('REDIS_DB',10)
TIME_ZONE = 'Asia/Shanghai'
#CELERY TASKS
BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
app = Celery('tasks', broker=BROKER_URL)

from celery import shared_task
import functools


def celery_queue(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            queue = kwargs.get('queue')

            @shared_task(name=name, queue=queue)
            def pro_func(*args, **kwargs):
                resp = func(*args, **kwargs)
                return resp

            return pro_func.delay(*args, **kwargs)

        return wrapper

    return decorator


@celery_queue(name='om_consumer_start')
def om_consumer_start(**kwargs):
    '''
    发送告警队列
    '''
    print('%s:kwargs:%s' % ('om_consumer_start', kwargs))


@celery_queue(name='om_saver_start')
def om_saver_start(**kwargs):
    print('%s:kwargs:%s' % ('om_saver_start', kwargs))

if __name__ == '__main__':
    # om_consumer_start(**{'queue': 'ops_alarm_consumer'})
    om_saver_start(**{'queue': 'ops_alarm_saver'})
    # om_saver_start(**{'queue': 'ops_alarm_saver'})

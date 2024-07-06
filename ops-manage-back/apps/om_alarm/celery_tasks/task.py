from celery import shared_task
import logging
logger = logging.getLogger(__name__)
import functools

def celery_queue(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            queue = kwargs.pop('queue')
            @shared_task(name=name,queue=queue)
            def pro_func(*args, **kwargs):
                resp = func(*args, **kwargs)
                return resp
            pro_func.apply_async(queue=queue,task_name=name,args=args,kwargs=kwargs)
            #celery 5版本delay指定队列不行
            # return pro_func.delay(*args, **kwargs)

        return wrapper

    return decorator
@celery_queue(name='om_consumer_start')
def om_consumer_start(**kwargs):
    '''
    发送告警队列
    '''
    logger.info('%s:kwargs:%s' % ('om_consumer_start', kwargs))


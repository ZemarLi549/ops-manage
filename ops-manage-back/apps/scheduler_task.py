import logging
from django.conf import settings
from apscheduler.executors.pool import ThreadPoolExecutor,ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.interval import IntervalTrigger
redis_config = {
    'host': settings.REDIS_HOST,
    'port': int(settings.REDIS_PORT),
    'db': 0,
    # 如果有密码，添加密码参数
    'password': settings.REDIS_PASSWORD
}

executors = {
    'default': ThreadPoolExecutor(10),#默认线程数
    'processpool': ProcessPoolExecutor(3)#默认进程
}
jobstore = RedisJobStore(**redis_config)

from apps.om_alarm.aps_tasks.heartrate_tasks import remove_ignore_black_job
from apps.om_logsearch.aps_tasks.heartrate_tasks import remove_ignore_filter_job


logger = logging.getLogger(__name__)




def job_task():
    job_defaults = {
        'coalesce': True,
        'max_instances': 10,
        "misfire_grace_time": 3
    }
    # 创建后台调度器，并指定 jobstore
    scheduler = BackgroundScheduler(jobstores={'default': jobstore}, job_defaults=job_defaults, executors=executors,
                                    timezone='Asia/Shanghai')
    try:
        jobstore.remove_all_jobs()
        print(f'jobstore remove job ok')
    except Exception as e:
        print(f'jobstore remove job err:{e}')
    try:
        # minutes
        scheduler.add_job(id='remove_ignore_black', func=remove_ignore_black_job, trigger=IntervalTrigger(**{'minutes': 27}))
        scheduler.add_job(id='remove_ignore_filter_job', func=remove_ignore_filter_job, trigger=IntervalTrigger(**{'minutes': 1}))
    except Exception as e:
        print(f'add job err:{e}')
    scheduler.start()

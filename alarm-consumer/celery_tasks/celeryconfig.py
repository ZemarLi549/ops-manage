from dotenv import load_dotenv
load_dotenv(verbose=True)
import os
REDIS_URL = os.environ.get('REDIS_URL', 'redis://:pieceloveredis@10.110.1.17:6380/1')
REDIS_HOST=os.environ.get('REDIS_HOST','10.110.1.17')
REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD','pieceloveredis')
REDIS_PORT=os.environ.get('REDIS_PORT',6380)
REDIS_DB=os.environ.get('REDIS_DB',10)
IS_REDIS_CLUSTER=os.environ.get('IS_REDIS_CLUSTER','0')
REDIS_BACK_DB=os.environ.get('REDIS_BACK_DB',11)
if IS_REDIS_CLUSTER == '1':
    REDIS_DB = 0
    REDIS_BACK_DB = 0
TIME_ZONE = 'Asia/Shanghai'
#CELERY TASKS
BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_BACK_DB}'
# 连接超时
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 180}
# 消息格式
CELERY_ACCEPT_CONNECT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'  # 任务序列化和反序列化使⽤json
CELERY_RESULT_SERIALIZER = 'json'
# 时区

# CELERY_WORKER_CONCURRENCY = 20  # 并发worker数
# CELERYD_FORCE_EXECV = True    # 非常重要,有些情况下可以防止死锁
# CELERYD_WORKER_PREFETCH_MULTIPLIER = 1
# CELERY_WORKER_MAX_TASKS_PER_CHILD = 100    # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
# CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 10}# 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
# CELERY_WORKER_DISABLE_RATE_LIMITS = True

BROKER_CONNECTION_TIMEOUT = 30  # 设置连接超时时间为 30 秒
BROKER_CONNECTION_RETRY_ON_STARTUP=True
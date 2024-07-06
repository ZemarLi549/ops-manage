from celery import Celery
from celery_tasks import celeryconfig


app = Celery('djangoProject',include=[
    'celery_tasks.consumer_alarm',
                      ]
             )

# 引入配置文件
app.config_from_object(celeryconfig)
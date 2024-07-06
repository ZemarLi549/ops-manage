from celery import Celery
import os
# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "ops_manage.settings")

# 实例化celery
app = Celery("djangoProject")

# 使用django的配置文件进行配置
app.config_from_object('django.conf.settings')
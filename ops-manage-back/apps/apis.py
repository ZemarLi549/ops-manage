from django.urls import path, include
from apps.scheduler_task import job_task
job_task()
api_urls = [
    path('api/', include('apps.management.urls')),
    path('api/', include('apps.om_auth.urls')),
    path('api/log/', include('apps.om_logsearch.urls')),
    path('api/alarm/', include('apps.om_alarm.urls')),
]

# -*- coding: utf-8 -*-

from .views import *
from django.urls import path,include

urlpatterns = [
    path('user', AlarmUserView.as_view()),
    path('config', AlarmConfigView.as_view()),
    path('rule', AlarmRuleView.as_view()),
    path('alert', AlarmReceiverView.as_view()),
    path('black', AlarmBlackView.as_view()),
    path('cacheread', CacheReadlView.as_view()),
    path('identity', AlarmIdentityResourceView.as_view()),
    path('alarm_query', AlarmSearchView.as_view()),
    path('alarm_hisgram', AlarmHistoryGramAggView.as_view()),
    path('alarm_locate', AlarmLocateView.as_view()),
    path('comment', AlarmCommentResoureView.as_view()),#加入白名单，无request.realname
    path('putcmt', AlarmCommentResoureView.as_view()),
    path('solution', AlarmSolutionView.as_view()),#加入白名单，无request.realname
    path('putsolu', AlarmSolutionView.as_view()),
    path('identity_info', AlarmIdentityInfoView.as_view()),#加入白名单，无request.realname
    path('alarmsimilar', AlarmLastSilmilarView.as_view()),#加入白名单，无request.realname
    path('alarmexist', AlarmExistsResourceView.as_view()),#加入白名单，无request.realname
    path('batchcmt', AlarmBatchCommentResoureView.as_view()),
]
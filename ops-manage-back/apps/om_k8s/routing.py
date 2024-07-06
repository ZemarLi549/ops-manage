#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from apps.om_k8s.consumers import *
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws-api/terminal/(?P<cluster>[^/]+)/(?P<namespace>[^/]+)/(?P<cid>[^/]+)/(?P<group_name>.*)$', CurrentLog.as_asgi()),
    re_path(r'ws-api/nodeterm/(?P<cluster>[^/]+)/(?P<name>[^/]+)/(?P<group_name>.*)$', NodeShell.as_asgi()),
]
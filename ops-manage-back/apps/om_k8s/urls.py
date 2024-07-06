# -*- coding: utf-8 -*-

from .views import *
from django.urls import path,include

urlpatterns = [
    path('cluster', ClusterView.as_view(), name='k8s/cluster'),
    path('cluster/password', ClusterInfoView.as_view(), name='k8s/cluster/password'),
    path('nodes', NodeListView.as_view(), name='k8s/nodes'),
    path('node/detail', NodeDetailView.as_view(), name='node/detail'),
    path('log', PodLogView.as_view(), name='log'),
    path('namespace', K8sNamespacesView.as_view(), name='namespaces'),
    path('events', K8sEventsView.as_view(), name='events'),
    path('deployments', K8sDeploymentsView.as_view(), name='deployments'),
]
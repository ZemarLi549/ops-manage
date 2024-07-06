from django.urls import path
from .views import *


urlpatterns = [
    path('sys/user', UserView.as_view(), name='user.all'),
    path('sys/user/info', SearchUserInfoView.as_view(), name='user.info'),
    path('sys/role', RoleView.as_view(), name='sys/role'),
    path('sys/menu', ResourceView.as_view(), name='sys/menu'),

    path('account/info', UserInfoView.as_view(), name='account/info'),
    path('account/permmenu', UserPermView.as_view(), name='account/permmenu'),
    path('sys/dept', DepartmentView.as_view(), name='sys/dept'),
    path('sys/role/info', RoleInfoView.as_view(), name='sys/role/info'),


]

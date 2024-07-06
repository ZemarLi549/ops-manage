# -*- coding: utf-8 -*-

from .views import *
from django.urls import path,include

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('account/logout', LogoutView.as_view(), name='logout'),
    path('token', TokenView.as_view(), name='token'),
    path('register', UserRegView.as_view(), name='register'),
    path('captcha/', include('captcha.urls')),
    path('captcha/img', CapthaGetView.as_view(), name='captcha/img'),    # 图片验证码 路由

]
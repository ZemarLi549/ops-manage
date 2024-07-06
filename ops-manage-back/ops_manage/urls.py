"""ops_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from apps.apis import api_urls
from apps.health_check import HealthCheckView
# from django.contrib import admin
# from apps.swagger import get_swagger_view
from ops_manage.settings import BASE_URL

urlpatterns = [path(BASE_URL, include(api_urls))]

urlpatterns += [
    # path(BASE_URL+'admin/', admin.site.urls),
    # path(BASE_URL+'status/health.check', HealthCheckView.as_view()),
    # path(BASE_URL+'api/swagger',
    #      get_swagger_view().with_ui('swagger', cache_timeout=1),
    #      name="docs"),
    # path(BASE_URL+'api/redoc',
    #      get_swagger_view().with_ui('redoc', cache_timeout=1),
    #      name='redoc'),
]


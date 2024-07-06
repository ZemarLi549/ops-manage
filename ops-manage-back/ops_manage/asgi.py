"""
ASGI config for ops_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

# import os
# from channels.routing import get_default_application
# try:
#     if os.path.exists('.local/.env'):
#         import dotenv
#         dotenv.load_dotenv('.local/.env')
# except Exception as exc:
#     print(exc)
#     pass
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops_management.settings')
# application = get_default_application()


import os
try:
    if os.path.exists('.local/.env'):
        import dotenv
        dotenv.load_dotenv('.local/.env')
except Exception as exc:
    print(exc)
    pass
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops_manage.settings')
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# from channels.auth import AuthMiddlewareStack
# from apps.om_k8s.routing import websocket_urlpatterns as logsearchrouting



django_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket":
    #     URLRouter(
    #         logsearchrouting
    #     )

})

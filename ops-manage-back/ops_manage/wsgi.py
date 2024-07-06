"""
WSGI config for ops_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
try:
    if os.path.exists('.local/.env'):
        import dotenv
        dotenv.load_dotenv('.local/.env')
except Exception as exc:
    print(exc)
    pass
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops_management.settings')

application = get_wsgi_application()

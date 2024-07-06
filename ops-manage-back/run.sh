# python ops.py #king
gunicorn ops_manage.asgi:application  -k uvicorn.workers.UvicornWorker   -t 180 -w 8 --bind 0.0.0.0:8000 -p ./gunicorn.pid
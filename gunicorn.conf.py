import os

workers = int(os.getenv('GUNICORN_WORKERS', '2'))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gevent')
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))
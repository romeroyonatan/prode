web: gunicorn config.wsgi:application
worker: celery worker --app=prode.taskapp --loglevel=info

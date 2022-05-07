release: python manage.py migrate
web: daphane core.wsgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery -A core worker -l info
celery: celery -A core beat -l info
from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app     = Celery('core')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kathmandu')

app.config_from_object(settings, namespace='CELERY')

#Celery Beats Settings
app.conf.beat_schedule = {
    'check-completed-booking-everyday-at-12pm' : {
        'task'         : 'listings.tasks.check_for_completed_booking',
        'schedule'     : crontab(hour=12, minute=1),
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request : {self.request!r}' )
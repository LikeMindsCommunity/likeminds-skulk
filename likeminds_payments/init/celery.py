from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()
from django.conf import settings

if settings.IS_BETA:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'init.settings.beta')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'init.settings.production')

app = Celery('init', backend='amqp', broker=os.getenv('BROKER_URL'))
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.timezone = 'Asia/Kolkata'

app.conf.enable_utc = False

beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

app.conf.update(
    task_routes={
        'proj.tasks.add': {'queue': 'celery', 'delivery_mode': 'transient'}
    }
)

app.conf.update(
    task_acks_late=True
)

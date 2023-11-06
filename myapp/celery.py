from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')

celery = Celery('myapp')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()


celery.conf.beat_schedule = {
    'report_every_one_day': {
        'task': 'user.tasks.report',
        'schedule': crontab(hour=0, minute=0)
    }
}

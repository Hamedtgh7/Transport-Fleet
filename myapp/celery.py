from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')

celery = Celery('myapp')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()

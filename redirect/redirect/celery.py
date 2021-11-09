import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'redirect.settings')

app = Celery('clear_db')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Создаёт задачу на очистку базы данных кждый понедельник в 00:00
app.conf.beat_schedule = {
    'clear_db_every_week': {
        'task': 'redirect_app.tasks.clear_db',
        # 'schedule': crontab(minute=0, hour=0, day_of_week='monday')
        'schedule': crontab(minute='*/1')
    }
}
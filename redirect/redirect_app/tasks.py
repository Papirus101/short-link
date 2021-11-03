from redirect.celery import app

from .models import ShortLink
from .views import red

@app.task
def clear_db():
    ShortLink.objects.all().delete()
    red.flushdb()
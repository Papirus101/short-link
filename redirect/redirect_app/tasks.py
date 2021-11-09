import logging

from redirect.celery import app

from .models import ShortLink
from .views import red


@app.task
def clear_db():
    ShortLink.objects.all().delete()
    logging.info('Очистили базу данных')
    keys = red.keys('slug:*')
    logging.info(f'Начиинаем очистку Redis, всего найдено {len(keys)} значений')
    for key in keys:
        logging.info(f'Удаляем {key}')
        red.delete(key)
    logging.info('Завершили очистку Redis')

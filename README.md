#Сокращение ссылок
**Для запуска проекта необходимо:**
1. Установить все зависимости из файла requirements.txt `pip install -r requirements.txt`
2. Запустить redis
3. В файле .env указаать пременное окружение
4. Запустить MYSQL
5. Запустить миграции `python manage.py migrate`
6. Создать супер пользователя `python manage.py createsuperuser`
7. Запустить django проект `python manage.py runserver`
8. Запустить celery `celery -A redirect worker -l info` `celery -A redirect beat -l info`

**Если pip выдаёт ошибку при установке mysqlclient**
```
Шаг 1: sudo apt install python3-dev build-essential
Шаг 2: sudo apt install libssl1.1
Шаг 3: sudo apt install libssl1.1=1.1.1f-1ubuntu2
Шаг 4: sudo apt install libssl-dev
Шаг 5: sudo apt install libmysqlclient-dev
Шаг 5: pip3 install mysqlclient
```
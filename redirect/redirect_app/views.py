import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.db import transaction

from .forms import ShortLinkForm
from .models import ShortLink

import random
import string
import redis

from .services import get_user_links

red = redis.Redis()


class HomeView(View):

    def get(self, request, *args, **kwargs):
        """ Главная страница """
        user_pk = request.session.get('user_pk')
        logging.info('Пользователь зашёл на сайт, получаем его id из сессии')
        urls_user = get_user_links(user_pk)
        logging.info('Получаем уже созданные ссылки пользователя')
        if not user_pk:
            logging.info('Пользователя нет в сессии, добавялем...')
            request.session['user_pk'] = ShortLink.objects.latest('user_pk').user_pk + 1
        link_form = ShortLinkForm()
        logging.info('Загрузили форму для сокращения ссылок и отправили пользователю страницу')
        return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})

    def post(self, request, *args, **kwargs):
        """ Сокращение ссылки """
        logging.info('Пользователь прислал форму')
        user_pk = request.session.get('user_pk')
        urls_user = get_user_links(user_pk)
        link_form = ShortLinkForm(request.POST)
        logging.info('Заполнили форму данными')
        if link_form.is_valid():
            logging.info('Форма валидна')
            short_link = link_form.cleaned_data['short_link']
            long_link = link_form.cleaned_data['long_link']
            logging.info('Получаем короткую и длинную ссылку пользователя')
            # Если пользователь не указал ссылку, генерируем её сами
            if len(short_link) == 0:
                logging.info('Пользователь не указал желаему ссылку, генерируем сами')
                short_link = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                # Проверяем не повторяется ли ссылка, которую сгенерировали
                while ShortLink.objects.filter(short_link=short_link).exists():
                    logging.info('Проверяем короткую ссылку пользователя на наличие её в базе')
                    short_link = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            else:
                # Если пользователь указал желаемую ссылку, проверяем её доступность
                link_valid = ShortLink.objects.filter(short_link=short_link).exists()
                # Если такая ссылка уже используется, отправляем сообщение пользователю
                if link_valid:
                    logging.info('Пользователь указал уже существующую короткую ссылку')
                    messages.add_message(request, messages.ERROR, 'Данная ссылка занята')
                    urls_user = get_user_links(user_pk)
                    return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})
            try:
                ShortLink.objects.create(user_pk=user_pk, long_link=long_link,
                                         short_link=short_link)
                logging.info('Добавили ссылку в базу данных')
                messages.add_message(request, messages.SUCCESS, 'Ссылка успешно сокращена')
            # Обрабатываем ошшибку подключения к базе данных
            except transaction.TransactionManagementError:
                logging.error('Ошибка транзакции при добавлении ссылки в БД')

            try:
                red.set(f'slug:{short_link}', long_link)
                logging.info('Добавли ссылку в Redis')
            # Обрабатываем ошибку подключения к redis
            except redis.exceptions.ConnectionError:
                if ShortLink.objects.filter(short_link=short_link).exists():
                    logging.error('Ошибка подключения к Redis')
                else:
                    messages.add_message(request, messages.ERROR,
                                         'Ошибка сервера, попробуйте изменить желаемую короткую ссылку')
                    logging.error('Ошибка подключения к Redis и добавлении данных в БД')
            # Обрабатываем ошибку данных Redis
            except redis.exceptions.DataError:
                if ShortLink.objects.filter(short_link=short_link).exists():
                    logging.error('Ошибка подключения к Redis')
                else:
                    messages.add_message(request, messages.ERROR,
                                         'Ошибка сервера, попробуйте изменить желаемую короткую ссылку')
                    logging.error('Ошибка добавления данных в Redis и добавлении данных в БД')
            # Обновляем список ссылок пользователя
            urls_user = get_user_links(user_pk)
            return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})
        else:
            return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})


class RedirectUserView(View):
    """ Клас редиректа """

    def get(self, request, *args, **kwargs):
        # Получаем короткую ссылку из URL
        logging.info('Пользователь пришёл по короткой ссылке')
        short_link = kwargs['short_link']
        # Пробуем получить закешированный объект из redis
        try:
            long_link = red.get(f'slug:{short_link}')
            logging.info('Получили ссылку из Redis для редиректа')
        # Обрабатываем ошибку подключения к redis
        except redis.exceptions.ConnectionError:
            logging.info('Ошибка подключения к Redis во время редиректа')
        # Обрабатываем ошибку данных Redis
        except redis.exceptions.DataError:
            logging.info('Ошибка получения данных из Redis во время редиректа')
        # Если в редисе отсутствует, берём из базы данных
        if not long_link:
            logging.info('Ссылка в Redis не найдена, ищем в БД')
            long_link = get_object_or_404(ShortLink, short_link=short_link).long_link
        else:
            # Если нашли в редис, преобразуем в строку
            long_link = long_link.decode('utf-8')
        # Проверяем указал ли пользтователь http or https
        if not long_link.startswith(('http', 'https')):
            # Если не указал, то добавляем сами
            return redirect(f'http://{long_link}')
        return redirect(long_link)

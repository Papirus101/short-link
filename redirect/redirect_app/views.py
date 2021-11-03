from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages

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
        # Получем пользователя из сессии
        user_pk = request.session.get('user_pk')
        urls_user = get_user_links(user_pk)
        if not user_pk:
            request.session['user_pk'] = ShortLink.objects.latest('user_pk').user_pk + 1
        link_form = ShortLinkForm()
        return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})

    def post(self, request, *args, **kwargs):
        """ Сокращение ссылки """
        # Получаем id пользователя из сессии
        user_pk = request.session.get('user_pk')
        urls_user = get_user_links(user_pk)
        # Заполняем форму данными
        link_form = ShortLinkForm(request.POST)
        # Проверяем валидацию формры
        if link_form.is_valid():
            # Устанавливаем ссылки пользователя из формы
            short_link = link_form.cleaned_data['short_link']
            long_link = link_form.cleaned_data['long_link']
            # Если пользователь не указал ссылку, генерируем её сами
            if len(short_link) == 0:
                short_link = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            else:
                # Если пользователь указал желаемую ссылку, проверяем её доступность
                link_valid = ShortLink.objects.filter(short_link=short_link).exists()
                # Если такая ссылка уже используется, отправляем сообщение пользователю
                if link_valid:
                    messages.add_message(request, messages.ERROR, 'Данная ссылка занята')
                    urls_user = get_user_links(user_pk)
                    return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})
            # Проверяем не повторяется ли ссылка, которую сгенерировали
            while ShortLink.objects.filter(short_link=short_link).exists():
                short_link = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            # Записываем новую ссылку в базу
            ShortLink.objects.create(user_pk=user_pk, long_link=long_link,
                                     short_link=short_link)
            red.mset({short_link: long_link})
            # Обновляем список ссылок пользователя
            urls_user = get_user_links(user_pk)
            messages.add_message(request, messages.SUCCESS, 'Ссылка успешно сокращена')
            return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})
        else:
            return render(request, 'redirect_app/index.html', {'urls_user': urls_user, 'link_form': link_form})


class RedirectUserView(View):
    """ Клас редиректа """

    def get(self, request, *args, **kwargs):
        # Получаем короткую ссылку из URL
        short_link = kwargs['short_link']
        # Пробуем получить закешированный объект из redis
        long_link = red.get(short_link)
        # Если в редисе отсутствует, берём из базы данных
        if not long_link:
            long_link = get_object_or_404(ShortLink, short_link=short_link).long_link
        else:
            # Если нашли в редис, преобразуем в строку
            long_link = long_link.decode('utf-8')
        return redirect(long_link)

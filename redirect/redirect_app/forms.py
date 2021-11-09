import logging

from django import forms

from .models import ShortLink

import re

from .services import get_pattern_to_check_link


class ShortLinkForm(forms.ModelForm):
    """ Форма создания короткой ссылки """

    # Делаем поле короткой ссылки необязательным в форме
    def __init__(self, *args, **kwargs):
        super(ShortLinkForm, self).__init__(*args, **kwargs)
        self.fields['short_link'].required = False

    class Meta:
        model = ShortLink
        fields = ['long_link', 'short_link']
        labels = {
            'long_link': 'Ссылка которую необхожимо укоротить',
            'short_link': 'Желаемая ссылка',
        }
        # Указываем класс для работы с BootStrap
        widgets = {
            'long_link': forms.TextInput(attrs={'class': 'form-control'}),
            'short_link': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_short_link(self):
        """ Проверяет короткую ссылку пользователя """
        if len(self.cleaned_data['short_link']):
            logging.info('Проверяем короткую ссылку, которую указал пользователь')
            if bool(re.search('[^a-zA-z]', self.cleaned_data['short_link'])):
                logging.info('[ВАЛИДАЦИЯ ФОРМЫ] Пользователь указал некорректную ссылку')
                raise forms.ValidationError('Короткая ссылка должна состоять только из букв английского алфавита')
        return self.cleaned_data['short_link']

    def clean_long_link(self):
        """ Проверяет исходную ссылку пльзователя """
        if self.cleaned_data['long_link']:
            logging.info('Проверяем исходную ссылку пользователя')
            if not bool(get_pattern_to_check_link().match(self.cleaned_data['long_link'])):
                raise forms.ValidationError('Укажите ссылку в формате https://link.example/ или http://link.example/ '
                                            'или link.example или www.link.example')
        return self.cleaned_data['long_link']

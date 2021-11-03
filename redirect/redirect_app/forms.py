from django import forms

from .models import ShortLink

import re


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
            'long_link': forms.URLInput(attrs={'class': 'form-control'}),
            'short_link': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_short_link(self):
        """ Проверяет короткую ссылку пользователя """
        if not bool(re.search('[a-zA-z]', self.cleaned_data['short_link'])):
            raise forms.ValidationError('Короткая ссылка должна состоять только из букв английского алфавита')
        return self.cleaned_data['short_link']



from django.db import models


class ShortLink(models.Model):
    user_pk = models.PositiveIntegerField('Идентификатор пользователя')
    long_link = models.URLField('Длинная ссылка пользователя', max_length=255)
    short_link = models.CharField('Короткая ссылка пользователя', max_length=10)

    def __str__(self):
        return self.short_link
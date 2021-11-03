from .models import ShortLink


def get_user_links(user_pk):
    """ Получает ранее сокращенные ссылки пользователя """
    urls_user = ShortLink.objects.filter(user_pk=user_pk)
    if len(urls_user) == 0:
        urls_user = False
    return urls_user

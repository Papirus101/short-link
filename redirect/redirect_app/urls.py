from django.urls import path

from .views import HomeView, RedirectUserView

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('<str:short_link>', RedirectUserView.as_view(), name='redirect')
]

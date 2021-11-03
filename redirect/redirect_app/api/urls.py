from django.urls import path

from .api_views import LinkListApiView, GetLinkApiView

urlpatterns = [
    path('all_links/', LinkListApiView.as_view(), name='all_links'),
    path('get_link/', GetLinkApiView.as_view(), name='get_link'),
]
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from .serializers import LinkSerializers

from ..models import ShortLink


class LinkListApiView(ListAPIView):

    serializer_class = LinkSerializers
    queryset = ShortLink.objects.all()


class GetLinkApiView(ListAPIView):

    serializer_class = LinkSerializers
    queryset = ShortLink.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['short_link', 'long_link']

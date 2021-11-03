from rest_framework import serializers

from ..models import ShortLink


class LinkSerializers(serializers.ModelSerializer):

    long_link = serializers.URLField()
    short_link = serializers.CharField()

    class Meta:
        model = ShortLink
        fields = [
            'long_link',
            'short_link'
        ]

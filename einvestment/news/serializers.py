from rest_framework import serializers

from .models import News

class NewsListSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()
    
    class Meta:
        model = News
        fields = ('image', 'body', 'date_created')
    
    def get_body(self, object):
        return object.body[:256] + '...'


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

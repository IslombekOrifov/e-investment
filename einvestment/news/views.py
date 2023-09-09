from rest_framework import generics, status, permissions, views, mixins, viewsets

from .serializers import NewsListSerializer, NewsSerializer
from .models import News


class NewsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = News.objects.all()
    permission_classes = (permissions.AllowAny,)
    default_serializer_class = NewsSerializer
    serializer_classes = {
        'list': NewsListSerializer,
        'retrieve': NewsSerializer
    }
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

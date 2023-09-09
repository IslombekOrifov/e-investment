from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from .views import NewsViewSet

router = DefaultRouter()
router.register('news', NewsViewSet)

urlpatterns = []

urlpatterns += router.urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
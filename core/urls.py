from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import SupportViewSet ,SupportReplyViewSet


app_name = 'core'


router = DefaultRouter()
router.register('support', SupportViewSet, basename='support')
router.register('reply', SupportReplyViewSet, basename='Reply')


urlpatterns = [
    path('', include(router.urls)),
]

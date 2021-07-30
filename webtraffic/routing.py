from django.urls import re_path

from webtraffic.consumers import WebsiteConsumer

websocket_urlpatterns = [
    re_path(r'ws/websites/$', WebsiteConsumer.as_asgi()),
]
from django.urls import re_path

from room.consumers import room_chat, wishlist

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', room_chat.ChatConsumer.as_asgi()),
    re_path(r'ws/wishlist/(?P<room_name>\w+)/$', wishlist.WishlistConsumer.as_asgi()),
]
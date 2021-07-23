import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.postgres.search import TrigramSimilarity

from room.models import Room, RoomUser, RoomRecommendedProduct
from room.serializers import RoomRecommendationsSerializer
from accounts.models import User
from product.models import Product
from product.serializers.product import ProductListSerializer


class ChatRecommendationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope["user"]
        # self.room = await get_room(self.room_name)
        # self.room_group_name = 'recommendations_%s' % self.room_name
        self.room_group_name = 'recommendations'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive_json(self, text_data):
        if (text_data['sender'] != self.user.username) or (str(text_data['room_id']) != str(self.room.id)):
            await self.send(text_data=json.dumps({
                'message': "Wrong Username or Room ID",
            }))

    async def send_to_websocket(self, event):
        await self.send_json(event)

    async def send_room_recommendations(self, event):
        text = event["message"]
        data = await get_room_recommendations(text)
        await self.send_json(data)


@database_sync_to_async
def get_room(name):
    room = Room.objects.filter(name=name)[0]
    return room

@database_sync_to_async
def get_room_user(room, user):
    room_user = RoomUser.objects.filter(room=room, user=user)
    if room_user.exists():
        return room_user[0]
    return None

@database_sync_to_async
def get_room_username_list(room):
    room_users = room.users.values_list('username', flat=True)
    return room_users


@database_sync_to_async
def get_room_recommendations(text):
    # products = Product.objects.annotate(similarity=TrigramSimilarity('name', text),).filter(similarity__gt=0.3).order_by('-similarity')
    products = Product.objects.filter(name__icontains=text)[:5]
    serializer = ProductListSerializer(products, many=True)
    return serializer.data

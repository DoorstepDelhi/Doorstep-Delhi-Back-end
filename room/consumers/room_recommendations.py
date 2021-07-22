import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from room.models import Room, RoomUser, RoomRecommendedProduct
from room.serializers import RoomRecommendationsSerializer
from accounts.models import User


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope["user"]
        self.room = await get_room(self.room_name)
        self.room_user = await get_room_user(self.room, self.user)
        self.room_group_name = 'recommendations_%s' % self.room_name

        if self.room_user:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            self.room_username_list = await get_room_username_list(self.room)
            await self.send(text_data=json.dumps({
                'message': "Accepted",
            }))
        else:
            await self.send(text_data=json.dumps({
                'message': "Wrong User or Room ID",
            }))
            await self.disconnect(403)

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
        data = await get_room_recommendations(self.room)
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
def get_room_recommendations(room):
    products = RoomRecommendedProduct.objects.filter(room=room)
    serializer = RoomRecommendationsSerializer(products, many=True)
    return serializer.data


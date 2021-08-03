import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import datetime

from webtraffic.models import Website, WebsiteHit
from webtraffic.serializers import WebsiteSerializer
from accounts.models import User


class WebsiteConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        # self.room_group_name = 'chat_%s' % self.room_name
        # await self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        await self.accept()
        data = await get_website_detail(self.user)
        await self.send(text_data=json.dumps(data))

    async def disconnect(self, close_code):
        # await self.disconnect(403)
        # Leave room group
        pass
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

    # Receive message from WebSocket
    async def receive_json(self, text_data):
        type = text_data["type"]
        website = text_data["website"]
        created = await save_website_hit(self.user, website, type)
        data = await get_website_detail(self.user)
        await self.send(text_data=json.dumps(data))

    async def send_to_websocket(self, event):
        await self.send_json(event)


@database_sync_to_async
def get_website_detail(user):
    # surfed_websites = WebsiteHit.objects.filter(
    #     user=request.user,
    #     created_at__lt=datetime.datetime.now() - datetime.timedelta(days=1),
    # ).values_list("website")
    # user = User.objects.get(username="admin")
    websites = Website.objects.exclude(user=user).exclude(
        website_hits__user=user, website_hits__created_at__gt=datetime.datetime.now() - datetime.timedelta(days=1)
    )
    if websites.exists():
        website = websites.first()
        serializer = WebsiteSerializer(website, many=False)
        return serializer.data
    else:
        return None

@database_sync_to_async
def save_website_hit(user, website_id, type):
    # user = User.objects.get(username="admin")
    try:
        website = Website.objects.get(id=website_id)
        website_hit = WebsiteHit.objects.create(
            website=website, user=user, type=type
        )
        return True
    except:
        return False

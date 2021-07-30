import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from room.models import Room, RoomUser, Message, RoomWishlistProduct, WishlistProductVote, RoomOrder, RoomOrderLine
from room.serializers import RoomWishlistProductSerializer
from accounts.models import User
from product.models import Product


class WishlistConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope["user"]
        self.room = await get_room(self.room_name)
        self.room_user = await get_room_user(self.room, self.user)
        self.room_group_name = 'chat_%s' % self.room_name

        if self.room_user:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            self.room_username_list = await get_room_username_list(self.room)
            data = await self.get_product_variants()
            await self.send(text_data=json.dumps({
                'wishlist': data
            }))
        else:
            await self.send(text_data=json.dumps({
                'error': "Wrong User or Room ID",
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
        if (text_data['user'] != self.user.id) or (str(text_data['room']) != str(self.room.id)):
            await self.send(text_data=json.dumps({
                'error': "Wrong Username or Room ID",
            }))
            await self.disconnect(403)
        data = await self.get_product_variants()
        action_type = text_data['action_type']

        if action_type == "add":
            self.product_id = int(text_data['product_id'])
            if await self.add_product(self.product_id):
                data = await self.get_product_variants()
                await self.send(text_data=json.dumps({
                    'success': "Product Added to Wishlist",
                }))
            else:
                await self.send(text_data=json.dumps({
                    'error': "Product Already Exists in Wish List",
                }))

        if action_type == "remove":
            self.product_id = int(text_data['product_id'])
            if await self.remove_product(self.product_id):
                data = await self.get_product_variants()
                await self.send(text_data=json.dumps({
                    'success': "Product Removed from Wish List",
                }))
            else:
                await self.send(text_data=json.dumps({
                    'error': "Product does not exists in Wish List",
                }))

        if action_type == "vote":
            self.wishlist_variant_id = int(text_data['wishlist_product_id'])
            if await self.vote_product_variant(self.wishlist_variant_id):
                await self.send(text_data=json.dumps({
                    'success': "Your Vote has been registered",
                }))
            else:
                await self.send(text_data=json.dumps({
                    'error': "You have already votes",
                }))

        if action_type == "unvote":
            self.wishlist_variant_id = int(text_data['wishlist_product_id'])
            if await self.unvote_product_variant(self.wishlist_variant_id):
                await self.send(text_data=json.dumps({
                    'success': "Your Vote has been unregistered"
                }))
            else:
                await self.send(text_data=json.dumps({
                    'error': "You haven't voted yet"
                }))

        if action_type == "add_to_cart":
            self.wholesale_variant_id = int(text_data['wholesale_variant_id'])
            if await self.add_to_cart(self.wholesale_variant_id):
                await self.send(text_data=json.dumps({
                    'success': "Product Added to Cart"
                }))
            else:
                await self.send(text_data=json.dumps({
                    'error': "Product Already in Cart"
                }))

        print(data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_to_websocket',
                'wishlist': data
            }
        )

    async def send_to_websocket(self, event):
        await self.send_json(event)

    @database_sync_to_async
    def add_product(self, product_id):
        wishlist_product = RoomWishlistProduct.objects.filter(room=self.room, product__id=product_id)
        if wishlist_product.exists():
            return False
        else:
            product = Product.objects.get(id=product_id)
            wishlist_product = RoomWishlistProduct.objects.create(
                room=self.room,
                user=self.user,
                product=product
            )
        return wishlist_product

    @database_sync_to_async
    def remove_product(self, product_id):
        wishlist_product = RoomWishlistProduct.objects.filter(room=self.room, product__id=product_id)
        if wishlist_product.exists():
            wishlist_product.delete()
            return True
        return False

    @database_sync_to_async
    def get_product_variants(self):
        wishlist_products = RoomWishlistProduct.objects.filter(room=self.room)
        serializer = RoomWishlistProductSerializer(wishlist_products, many=True)
        return serializer.data

    @database_sync_to_async
    def vote_product_variant(self, wishlist_product_id):
        wishlist_product = RoomWishlistProduct.objects.get(id=wishlist_product_id)
        product_vote, created = WishlistProductVote.objects.get_or_create(product=wishlist_product, user=self.user)
        if created:
            wishlist_product = product_vote.product
            wishlist_product.votes += 1
            wishlist_product.save()
            return True
        else:
            return False

    @database_sync_to_async
    def unvote_product_variant(self, wishlist_product_id):
        try:
            wishlist_product = RoomWishlistProduct.objects.get(id=wishlist_product_id)
            product_vote = WishlistProductVote.objects.get(product=wishlist_product, user=self.user)
            wishlist_product = product_vote.product
            wishlist_product.votes -= 1
            wishlist_product.save()
            product_vote.delete()
            return True
        except Exception as e:
            return False

    @database_sync_to_async
    def add_to_cart(self, wholesale_variant_id):
        cart = RoomOrder.objects.filter(room=self.room, status = "draft")
        if cart.exists():
            cart = cart.first()
        else:
            cart = RoomOrder.objects.create(room=self.room, status = "draft")
        try:
            cart_product = RoomOrderLine.objects.get(order=cart, variant__id=wholesale_variant_id)
            return False
        except Exception as e:
            cart_product = RoomOrderLine.objects.create(user=self.user, order=cart, variant__id=wholesale_variant_id)
            return cart_product

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


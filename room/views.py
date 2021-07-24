from functools import reduce

from django.shortcuts import render
from .models import Room, RoomOrder, RoomUser, RoomWishlistProduct, UserOrderLine
from rest_framework import serializers, viewsets
from rest_framework.views import APIView
from django.contrib.postgres.search import TrigramSimilarity

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from room.serializers import MessageSerializer, RoomOrderSerializer, RoomSerializer, RoomListSerializer, \
    RoomUserSerializer, \
    RoomWishlistProductSerializer, RoomOrderLineSerializer, RoomLastMessageSerializer, Message
from shop.models import OrderEvent
from django.db.models import Q, F
import operator

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .pagination import CustomPagination
from product.models import Product
from product.serializers.product import ProductListSerializer


def index(request):
    return render(request, 'room/index.html', {})


def room(request, room_name):
    room = Room.objects.filter(name=room_name)[0]

    return render(request, 'room/room.html', {
        'room_name': room_name,
        'room': room
    })


class RoomViewset(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        rooms = Room.objects.filter(users=self.request.user, room_users__role__in=["A", "U"],
                                    room_users__left_at=None, deleted_at=None)
        return rooms

    def list(self, request):
        queryset = self.get_queryset()
        context = {'request':request}
        serializer = RoomListSerializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='room-users')
    def last_message(self, request, pk=None):
        context = {
            "request":request,
        }
        queryset = self.get_queryset()
        serializer = RoomLastMessageSerializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='room-users')
    def users(self, request, pk=None):
        users = RoomUser.objects.filter(room__id=pk)
        context = {'request': request}
        serializer = RoomUserSerializer(users, many=True, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='room-orders')
    def orders(self, request, pk=None):
        orders = RoomOrder.objects.filter(room__id=pk)
        context = {'request': request}
        serializer = RoomOrderSerializer(orders, many=True, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='room-orders')
    def chats(self, request, pk=None):
        room = self.get_object()
        messages = Message.objects.filter(room=room).order_by("-created_on")
        context = {'request': request}
        serializer = MessageSerializer(messages, many=True, context=context)
        return Response(serializer.data)


class RoomWishlistProductViewset(viewsets.ModelViewSet):
    serializer_class = RoomWishlistProductSerializer
    permission_classes = []
    queryset = RoomWishlistProduct.objects.all()

    def list(self, request):
        queryset = self.queryset
        context = {'request': request}
        serializer = RoomWishlistProductSerializer(queryset, many=True, context=context)
        return Response(serializer.data)


class UserOrderLineViewSet(viewsets.ModelViewSet):  # verify
    serializer_class = RoomOrderLineSerializer
    permission_classes = []

    def get_queryset(self):

        userorderlines = UserOrderLine.objects.all()
        orderevents = OrderEvent.objects.all()
        if not self.request.user.is_superuser:
            Roomorderlines = userorderlines.filter(user=self.request.user)
            Roomorderevents = orderevents.filter(user=self.request.user)

        if self.request.query_params.get("status", None):

            status = self.request.query_params.get("status", None)

            if status == "unpaid":
                userorderlines = userorderlines.filter(
                    Q(order_status_iexact="draft")
                )
            elif status == "shipped":
                userorderlines = userorderlines.filter(
                    order_status_in=['partially_fulfilled', 'unfulfilled']
                )

            elif status == "in_dispute":
                orderevents = orderevents.filter(
                    type__in=map(lambda x: x.upper(),
                                 ['fulfillment_canceled', 'payment_failed', 'payment_voided', 'other'])
                )
                orderlines = UserOrderLine.objects.filter(
                    Q(order_in=orderevents.values_list('order', flat=True)) | Q(orderstatus_iexact="unconfirmed")
                )

            elif status == "to_be_shipped":
                orderevents = orderevents.filter(
                    Q(type__iexact="confirmed")
                )
                orderlines = UserOrderLine.objects.filter(order__in=orderevents.values_list('order', flat=True))

        return userorderlines


class RecommendationKeywords(APIView):

    def post(self, request, format=None):
        print("DATA - -------------------------------")
        print(request.data)
        products = Product.objects.all()
        parameters = request.data['queryResult']['parameters']
        query_text = request.data['queryResult']['queryText']
        category = list(parameters.get("category", None))
        if len(category) > 0:
            query = reduce(operator.or_, (Q(sub_category__name__icontains=item) for item in category))
            products = products.filter(query)
        brand = list(parameters.get("brand", None))
        if len(brand) > 0:
            query = reduce(operator.or_, (Q(brand__name__icontains=item) for item in brand))
            products = products.filter(query)
        price_range = list(parameters.get("price_range", None))
        if price_range:
            if "high" in price_range:
                products = products.order_by('-product_qty')
            else:
                products = products.order_by('product_qty')
        number_integer2 = list(parameters.get("number-integer", None))
        number_integer = []
        for integer in number_integer2:
            if integer > 5000:
                number_integer.append(integer)
        if len(number_integer) == 1:
            products = products.filter(product_qty__lte=number_integer[0])
        elif len(number_integer) > 1:
            number_integer.sort()
            products = products.filter(product_qty__gte=number_integer[0], product_qty__lte=number_integer[-1])
        print(products)
        # products = products.annotate(similarity=TrigramSimilarity('name', query_text))
        # print(products)
        # products = products.annotate(similarity=TrigramSimilarity('name', query_text)).filter(
        #     similarity__gt=0.3).order_by('-similarity')
        serializer = ProductListSerializer(products, many=True, context={"request": request})
        print(serializer.data)
        print("DATA - -------------------------------")
        print(parameters)
        print(category, brand, price_range, number_integer)
        room_group_name = 'recommendations'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_group_name, {
                'type': "send_room_recommendations",
                'message': serializer.data
            }
        )
        return Response("Thanks")
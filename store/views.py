from rest_framework.permissions import IsAuthenticated
from shop.serializers import OrderLineSerializer
from django.shortcuts import render
from rest_framework import viewsets, generics, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import  StoreSerializer, ShippingZoneSerializer, ShippingMethodSerializer, PickupPointSerializer,BankAccountSerializer,BusinessSerializer

from .models import Store, ShippingZone, ShippingMethod, PickupPoint, BankAccount
from .permissions import IsAdminOrReadOnly, IsPickupPointOwner, IsStoreOwner
from django.db.models import Q
from shop.models import Order
from room.models import RoomOrderLine
from room.serializers import RoomOrderLineSerializer
from accounts.models import Address, User
from accounts.serializers import FullUserSerializer, AddressSerializer, FullAddressSerializer


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Store.objects.all()

    @action(detail=True, methods=["get"], permission_classes=[IsStoreOwner, ])
    def order_history(self, request, pk, *args, **kwargs):
        store = self.get_object()
        orders = RoomOrderLine.objects.filter(status__in = ("canceled", "fulfilled"), variant__store = store)
        data = OrderLineSerializer(orders, many=True)
        return Response(data.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsStoreOwner, ])
    def returns(self, request, pk, *args, **kwargs):
        store = self.get_object()
        orders = RoomOrderLine.objects.filter(status__in = ("returned", "partially returned"), variant__store=store)
        data = RoomOrderLineSerializer(orders, many=True)
        return Response(data.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsStoreOwner, ])
    def new_orders(self, request, pk, *args, **kwargs):
        store = self.get_object()
        orders = RoomOrderLine.objects.filter(status__in=("unfulfilled", "partially fulfilled"), variant__store=store)
        data = RoomOrderLineSerializer(orders, many=True)
        return Response(data.data, status=status.HTTP_200_OK)
    
    @action(detail =True , methods=['get','post'], permission_classes=[IsStoreOwner, ])
    def bank_details(self, request, pk, *args, **kwargs):
        store = self.get_object()
        bank_details = BankAccount.objects.filter(store = store)
        serializer = BankAccountSerializer(bank_details, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    @action(detail =True , methods=['get'], permission_classes=[IsStoreOwner, ])
    def address(self, request, pk, *args, **kwargs):
        address = self.get_object().address
        serializer = AddressSerializer(address)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    @action(detail =True , methods=['get'], permission_classes=[IsStoreOwner, ])
    def business(self, request, pk, *args, **kwargs):
        store = self.get_object()
        serializer = BusinessSerializer(store)
        return Response(serializer.data ,status= status.HTTP_200_OK)


class ShippingZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = ShippingZone.objects.all()


class ShippingMethodViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = ShippingMethod.objects.all()


class PickupPointViewSet(viewsets.ModelViewSet):
    serializer_class = PickupPointSerializer
    permission_classes = [IsPickupPointOwner]
    queryset = PickupPoint.objects.all()

    @action(detail=True, methods=["get"], permission_classes=[IsPickupPointOwner, ])
    def order_history(self, request, pk, *args, **kwargs):
        pickup_point = self.get_object()
        orders = pickup_point.orders.filter()
        user = request.user
        type = request.data["type"]
        # website_hit = WebsiteHit.objects.create(
        #     website=website, user=user, type=type
        # )
        # return Response("Done", status=status.HTTP_200_OK)
        # except:
        #     return Response("Error", status=status.HTTP_400_BAD_REQUEST)

class FullRegister(views.APIView):
        
    def post(self, request, *args, **kwargs):
        print(request.data)
        user_data = request.data.get('user')
        user = FullUserSerializer(data=user_data)
        if user.is_valid():
            user = user.save()
            username = user_data['username']
            reg_user = User.objects.get(username=username)


            address_data = request.data.get('address')
            address = Address.objects.create(user=reg_user, **address_data)
            address.save()

            store_data = request.data.get('store')
            shipping_zone_data = store_data.pop('shipping_zones')
            store = Store.objects.create(address=address , 
                                         name = store_data["name"], 
                                         email = store_data["email"],
                                         website = store_data["website"],
                                         facebook_link = store_data["facebook_link"],
                                         instagram_link = store_data["instagram_link"])
            
            store.save()
            print(reg_user)
            store.users.add(reg_user)
        
            if shipping_zone_data:
                shipping_zone, created = ShippingZone.objects.get_or_create(**shipping_zone_data)
                shipping_zone.save()
                store.shipping_zones.add(shipping_zone)
                print("SHIPPING ZONE DATA EXISTS")
                store.save()
            else:
                print("SHIIPING ZONE DATA DOESN'T EXIST")
            store.save()

            bank_account_data = request.data.pop('bank_account')
            bank_account = BankAccount.objects.create(store=store, **bank_account_data)
            bank_account.save()

            return Response("User, Store, Bank and Address Registered", status=status.HTTP_200_OK)
        else:
            return Response("INVALID User Data")

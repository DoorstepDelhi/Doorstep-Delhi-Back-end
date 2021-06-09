from django.shortcuts import render
from rest_framework import viewsets, generics, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import StoreSerializer, ShippingZoneSerializer, ShippingMethodSerializer, PickupPointSerializer
from .models import Store, ShippingZone, ShippingMethod, PickupPoint
from .permissions import IsAdminOrReadOnly, IsPickupPointOwner
from shop.models import Order
from accounts.models import Address, User
from accounts.serializers import FullUserSerializer, AddressSerializer, FullAddressSerializer

class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Store.objects.all()


class ShippingZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = ShippingZone.objects.all()


class ShippingMethodViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = ShippingMethod.objects.all()


class PikupPointViewSet(viewsets.ModelViewSet):
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
        user.is_valid()        
        user = user.save()
        username = user_data['username']
        reg_user = User.objects.get(username=username)


        address_data = request.data.get('address')
        address = Address.objects.create(user=reg_user, **address_data)
        address.save()

        store_data = request.data.get('store')

        shipping_zone_data = store_data.pop('shipping_zones')
        shipping_zone = ShippingZone.objects.create(**shipping_zone_data)
        shipping_zone = shipping_zone.save()

        store = Store.objects.create(address=address, **store_data)
        store.users.add(reg_user)
        store.shipping_zones.add(shipping_zone)
        store.save()
        return Response("User, Store and Address Registered", status=status.HTTP_200_OK)

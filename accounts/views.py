from django.shortcuts import render, get_object_or_404, get_list_or_404
from .serializers import AddressSerializer, UserSerializer, NearbyUserSerializer
from .models import Address, User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsOwnerOrAdmin
from room.models import Room
from room.serializers import RoomListSerializer


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = AddressSerializer

    def get_queryset(self):
        addresses = Address.objects.all()
        if not self.request.user.is_superuser:
            addresses = addresses.filter(user=self.request.user)
        return addresses

    @action(detail=True, methods=["post"], permission_classes=[IsOwnerOrAdmin, ], name="Set Default Shipping Address")
    def set_default_shipping(self, request, *args, **kwargs):
        address = self.get_object()
        user = address.user
        user.default_shipping_address = address
        user.save()
        return Response({"status": "Default Shipping Address Updated Successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsOwnerOrAdmin, ], name="Set Default Billing Address")
    def set_default_billing(self, request, *args, **kwargs):
        address = self.get_object()
        user = address.user
        user.default_billing_address = address
        user.save()
        return Response({"status": "Default Billing Address Updated Successfully"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    permissions_classes = [IsOwnerOrAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        users = User.objects.all()
        if not self.request.user.is_superuser:
            users = self.request.user
        return users

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated,], name="User Address")
    def adrresses(self, request, *args, **kwargs):
        addresses = get_list_or_404(Address, user=self.request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated,], name="Contacts")
    def contacts(self, request, *args, **kwargs):
        phone_numbers = request.data['phone_numbers']
        phone_numbers = list(phone_numbers.strip().strip(",").split(",").replace(" ", "").replace("-", ""))
        users = User.objects.filter(username__in=phone_numbers)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated,], name="Nearby People")
    def nearby(self, request, *args, **kwargs):
        # longitude = request.data['long']
        # latitude = request.data['lat']
        users = User.objects.all()[:20]
        serializer = NearbyUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated,], name="Nearby Groups")
    def groups_nearby(self, request, *args, **kwargs):
        # longitude = request.data['long']
        # latitude = request.data['lat']
        rooms = Room.objects.all()[:20]
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated,], name="User Default Shipping Address")
    def default_shipping_address(self, request, *args, **kwargs):
        address = request.user.default_shipping_address
        if address:
            serializer = AddressSerializer(address, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"Error": "You don't have a Default Shipping Address"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated,], name="User Default Billing Address")
    def default_billing_address(self, request, *args, **kwargs):
        address = request.user.default_billing_address
        if address:
            serializer = AddressSerializer(address, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"Error": "You don't have a Default Shipping Address"}, status=status.HTTP_404_NOT_FOUND)



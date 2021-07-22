from django.conf import settings
from django.core.checks import messages
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import ClientLog, Support, SupportCategory, SupportReply, SupportSubCategory
from .serializers import SupportSerializer, ClientLogSerializer, SupportCategorySerializer, SupportSubCategorySerilizer, \
    SupportReplySerializer


class SupportViewSet(viewsets.ModelViewSet):
    serializer_class = SupportSerializer

    def get_queryset(self):
        queryset = Support.objects.filter(user=self.request.user)
        serializer = SupportSerializer(queryset, many=True)
        return serializer.data


class SupportReplyViewSet(viewsets.ModelViewSet):
    serializer_class = SupportReplySerializer

    #  queryset = SupportReply.objects.all()

    def get_queryset(self):
        query_set = SupportReply.objects.filter(user=self.request.user)
        serializer = SupportReplySerializer(query_set, many=True)
        return serializer.data

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, ])
    def update_support(self, request, pk, *args, **kwargs):
        try:
            message = self.get_object()
            user = request.user
            file = request.data["file"]
            supportreply = SupportReply.objects.create(
                message=message, user=user, type=type
            )
            return Response("Done", status=status.HTTP_200_OK)
        except:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from django.db import transaction
from django.db.models import Q
import datetime

from .serializers import WebsiteSerializer
from .models import Website, WebsiteHit
from .permissions import IsWebsiteOwner


class WebsiteAPIViewSet(viewsets.ModelViewSet):
    serializer_class = WebsiteSerializer
    permission_classes = [IsWebsiteOwner]
    # queryset = Website.objects.all()

    def get_queryset(self):
        websites = Website.objects.all()
        if not self.request.user.is_superuser:
            websites = Website.objects.filter(user=self.request.user)

        if self.request.query_params.get("search", None):
            search = self.request.query_params.get("search", None)
            websites = websites.filter(
                Q(name__icontains=search) | Q(url__icontains=search)
            )

        if self.request.query_params.get("namesort", None):
            sort = self.request.query_params.get("namesort", None)
            if sort == "asc":
                websites = websites.order_by("name")
            elif sort == "dsc":
                websites = websites.order_by("-name")

        if self.request.query_params.get("sort", None):
            sort = self.request.query_params.get("sort", None)
            if sort == "nameasc":
                websites = websites.order_by("name")
            elif sort == "namedsc":
                websites = websites.order_by("-name")
            elif sort == "dateasc":
                websites = websites.order_by("created_at")
            elif sort == "datedsc":
                websites = websites.order_by("-created_at")

        return websites

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request, *args, **kwargs):
        response = {
            "points_earned": 234,
            "points_earned_txt": "Points Earned",
            "sites_visited": 24,
            "sites_visited_txt": "Sites Visited",
            "views_received": 345,
            "views_received_txt": "Views Received"
        }
        return Response(response)

    @action(detail=True, methods=["get"], permission_classes=[IsWebsiteOwner, ])
    def unpause(self, request, pk, *args, **kwargs):
        website = self.get_object()
        website.status = "A"
        website.save()
        return Response({"Success":"Website Activated"})

    @action(detail=True, methods=["get"], permission_classes=[IsWebsiteOwner, ])
    def pause(self, request, pk, *args, **kwargs):
        website = self.get_object()
        website.status = "I"
        website.save()
        return Response({"Success":"Website Paused"})

    @action(detail=False, methods=["get"], permission_classes=[IsWebsiteOwner, ])
    def pause_websites(self, request, *args, **kwargs):
        websites = request.data['websites']
        websites = list(map(int, websites.strip().strip(",").split(",")))
        websites = Website.objects.filter(id__in=websites, user=request.user)
        websites.update(status="I")
        return Response({"Success": "Website Paused"})

    @action(detail=False, methods=["get"], permission_classes=[IsWebsiteOwner, ])
    def unpause_websites(self, request, *args, **kwargs):
        websites = request.data['websites']
        websites = list(map(int, websites.strip().strip(",").split(",")))
        websites = Website.objects.filter(id__in=websites, user=request.user)
        websites.update(status="A")
        return Response({"Success": "Website Paused"})

    @action(detail=False, methods=["get"], permission_classes=[IsWebsiteOwner, ])
    def delete_websites(self, request, *args, **kwargs):
        websites = request.data['websites']
        websites = list(map(int, websites.strip().strip(",").split(",")))
        websites = Website.objects.filter(id__in=websites, user=request.user)
        websites.update(status="I")
        return Response({"Success": "Website UnPaused"})

    @action(detail=False, methods=["get"], permission_classes=[IsWebsiteOwner, ])
    def remove_websites(self, request, *args, **kwargs):
        websites = request.data['websites']
        websites = list(map(int, websites.strip().strip(",").split(",")))
        websites = Website.objects.filter(id__in=websites, user=request.user)
        websites.delete()
        return Response({"Success": "Website Deleted"})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated,])
    def surf_websites(self, request, *args, **kwargs):
        surfed_websites = WebsiteHit.objects.filter(
            user=request.user,
            created_at__lt=datetime.datetime.now() - datetime.timedelta(days=1),
        ).values_list("website")
        websites = Website.objects.exclude(user=request.user).exclude(
            id__in=surfed_websites
        )
        serializer = WebsiteSerializer(websites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated,])
    def hit(self, request, pk, *args, **kwargs):
        try:
            website = self.get_object()
            user = request.user
            type = request.data["type"]
            website_hit = WebsiteHit.objects.create(
                website=website, user=user, type=type
            )
            return Response("Done", status=status.HTTP_200_OK)
        except:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)

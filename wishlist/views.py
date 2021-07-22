from rest_framework import viewsets, permissions

from wishlist.permissions import IsOwnerOrAdmin
from wishlist.models import Wishlist, WishlistItem
from wishlist.serializers import WishlistItemSerializer


class WishlistItemAPIViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsOwnerOrAdmin, permissions.IsAuthenticated]

    def get_queryset(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
        return wishlist_items

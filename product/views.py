import datetime
from django.db.models import Avg,Min,Max
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache
from django.conf import settings
from rest_framework.serializers import Serializer

from product.models import (
    Category,
    SubCategory,
    ProductType,
    Variation,
    Customization,
    Product,
    ProductVariant,
    WholesaleProductVariant,
    ProductImage,
    VariantImage,
    WholesaleVariantImage,
    ProductReview,
    ProductReviewFile,
    CollectionProduct,
    Collection,
    Brand,
)
from product.permissions import IsWebsiteOwnerorAdmin, IsAdminOrReadOnly
from product.serializers import *  # """ NEED TO CHANGE ASAP """
from wishlist.models import Wishlist, WishlistItem
from wishlist.serializers import WishlistSerializer
from accounts.models import Address
from shop.serializers import OrderLineSerializer, OrderSerializer
from shop.models import Order, OrderLine

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()

    
    # @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request):
        categories = self.queryset
        if not self.request.user.is_superuser:
            categories = categories.filter(user = self.request.user)
        
        if self.request.query_params.get("search", None):
            search = self.request.query_params.get("search",None)
            categories = categories.filter(
                Q(name__icontains = search)
            )

        if self.request.query_params.get("sort", None):
            sort = self.request.query_params.get("sort", None)
            if sort == "nameasc":
                categories = categories.order_by("name")
            elif sort == "namedsc":
                categories = categories.order_by("-name")

        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data)



    # @method_decorator(cache_page(60 * 60 * 24))
    @action(detail=True, methods=['get'], name='Sub-Categories')
    def set_password(self, request, pk=None):
        category = self.get_object()
        sub_categories = SubCategory.objects.filter(category=category)
        serializer = SubCategorySerializer(sub_categories, many=True)
        return Response(serializer.data)


class ProductTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = ProductType.objects.all()

    # @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request):
        queryset = self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class VariationViewSet(viewsets.ModelViewSet):
    serializer_class = VariationSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Variation.objects.all()

    # @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request):
        queryset = self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CustomizationViewSet(viewsets.ModelViewSet):
    serializer_class = CustomizationSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Customization.objects.all()

    # @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request):
        queryset = self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Collection.objects.all()

    # @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request):
        queryset = self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    # @method_decorator(cache_page(60 * 60 * 24))
    @action(detail=True, methods=['get'])
    def products(self, request, pk = None):
        collection = self.get_object()
        products = collection.products.all()
        serializer = ProductListSerilaizer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # if cache.get("all_products"):
        #     products = cache.get("all_products")
        # else:
        products = Product.objects.filter()#visible_in_listings=True)
            
        if not self.request.user.is_superuser:
            products = products.filter(user = self.request.user)
        
        if self.request.query_params.get("search", None):
            search = self.request.query_params.get("search",None)
            products = products.filter(
                Q(name__icontains = search)
            )

        if self.request.query_params.get("sort", None):
            sort = self.request.query_params.get("sort", None)
            if sort == "nameasc":
                products = products.order_by("name")
            elif sort == "namedsc":
                products = products.order_by("-name")
            elif sort == "priceasc":
                products = products.annotate(min_w_v=Min('wholesale_variants__price')).order_by('min_w_v')
            elif sort == "pricedsc":
                products = products.annotate(min_w_v=Min('wholesale_variants__price')).order_by('-min_w_v')
            elif sort == "popularity":
                products = products.order_by("-views")
            elif sort == "rating":         #check
                products = products.annotate(avg_rating=Avg('productreview__rating')).order_by('-avg_rating')
        return products
    
    def list(self, request, *args, **kwargs):
        products = self.get_queryset()
        serializer = ProductListSerilaizer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        images = ProductImage.objects.all()
        return images


class ProductVariantViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        productVariants = ProductVariant.objects.all()
        return productVariants
    
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def add_to_wishlist(self, request, pk):
        product_variant = self.get_object()
        wishlist, created = Wishlist.objects.get_or_create(user = request.user)
        wishlist_item = wishlist.add_variant(product_variant)
        serializer = WishlistSerializer(wishlist, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def remove_from_wishlist(self, request, pk):
        product_variant = self.get_object()
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.remove_variant(product_variant)
        serializer = WishlistSerializer(wishlist, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])            #wholsale_min_qty constraint not applied
    def add_to_cart(self,request,pk):
        current_user = request.user
        product_variant = self.get_object()
        order = Order.objects.filter(user=current_user, billing_address=request.user.default_billing_address, shipping_address=request.user.default_shipping_address)
        orderlines = OrderLine.objects.filter(variant = product_variant, order__in = order)
        
        if(not (orderlines.exists() and order.exists())):
            order= Order.objects.create(
            user=current_user, 
            billing_address=current_user.default_billing_address, 
            shipping_address=current_user.default_shipping_address, 
            status ="draft", 
            )
           
            OrderLine.objects.create(variant = product_variant, 
                                                       quantity = 1,
                                                       quantity_fulfilled=0, 
                                                       order = order)
        
    
            serializer = OrderSerializer(order, many = False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            print("exist")
            order = Order.objects.get(
            user=current_user, 
            billing_address=request.user.default_billing_address, 
            shipping_address=request.user.default_shipping_address, 
            status ="draft", 
            )
            orderline = OrderLine.objects.get(variant = product_variant,
                                                       order = order)
            
            serializer = OrderSerializer(order, many = False)
            return Response(serializer.data, status=status.HTTP_200_OK)
            

   

class WholesaleProductVariantViewSet(viewsets.ModelViewSet):
    serializer_class = WholesaleProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]#[IsShopOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        wholesale_product_variants = WholesaleProductVariant.objects.all()
        return wholesale_product_variants
    


class BrandViewSet(viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Brand.objects.all()



class HomeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = HomeCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()

    
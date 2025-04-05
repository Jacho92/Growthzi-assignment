from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.conf import settings
from .models import Category, Product, ProductImage, Discount
from .serializers import CategorySerializer, ProductSerializer, DiscountSerializer
from .filters import ProductFilter

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'product_{instance.pk}'
        cached_data = cache.get(cache_key)

        if cached_data is None:
            serializer = self.get_serializer(instance)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=3600)  # Cache for 1 hour

        return Response(cached_data)

    @action(detail=True, methods=['post'])
    def set_primary_image(self, request, slug=None):
        product = self.get_object()
        image_id = request.data.get('image_id')

        try:
            image = product.images.get(id=image_id)
            product.images.update(is_primary=False)
            image.is_primary = True
            image.save()
            return Response({'message': 'Primary image updated successfully'})
        except ProductImage.DoesNotExist:
            return Response(
                {'error': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'code'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['code', 'description']
    filterset_fields = ['is_active', 'discount_type']

    @action(detail=True, methods=['get'])
    def validate(self, request, code=None):
        discount = self.get_object()
        return Response({
            'is_valid': discount.is_valid,
            'message': 'Discount is valid' if discount.is_valid else 'Discount is not valid'
        })

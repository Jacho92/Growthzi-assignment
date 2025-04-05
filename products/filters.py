import django_filters
from .models import Product
from django.db import models

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    in_stock = django_filters.BooleanFilter(field_name='stock', lookup_expr='gt', exclude=True)
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'in_stock']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value)
        ) 
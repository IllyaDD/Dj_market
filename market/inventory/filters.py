import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Name contains')
    unit = django_filters.ChoiceFilter(field_name='unit', choices=Product.Unit.choices, label='Unit')
    min_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gte', label='Min price')
    max_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lte', label='Max price')
    min_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='gte', label='Min quantity')
    max_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='lte', label='Max quantity')

    class Meta:
        model = Product
        fields = ['name', 'unit', 'min_price', 'max_price', 'min_quantity', 'max_quantity']
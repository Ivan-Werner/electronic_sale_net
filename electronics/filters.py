import django_filters
from .models import NetworkNode


class NetworkNodeFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name='city', lookup_expr='iexact')
    country = django_filters.CharFilter(field_name='country', lookup_expr='iexact')
    min_debt = django_filters.NumberFilter(field_name='debt_to_supplier', lookup_expr='gte')
    max_debt = django_filters.NumberFilter(field_name='debt_to_supplier', lookup_expr='lte')
    hierarchy_level = django_filters.NumberFilter(method='filter_by_hierarchy_level')

    class Meta:
        model = NetworkNode
        fields = ['node_type', 'city', 'country']

    def filter_by_hierarchy_level(self, queryset, name, value):
        """Кастомный фильтр по уровню иерархии"""
        try:
            level = int(value)
            # Фильтруем по уровню иерархии
            filtered_ids = [node.id for node in queryset if node.hierarchy_level == level]
            return queryset.filter(id__in=filtered_ids)
        except ValueError:
            return queryset


class SupplierFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(
        field_name='country',
        lookup_expr='iexact',
        label='Страна'
    )
    country_contains = django_filters.CharFilter(
        field_name='country',
        lookup_expr='icontains',
        label='Страна (содержит)'
    )
    min_debt = django_filters.NumberFilter(
        field_name='debt_to_supplier',
        lookup_expr='gte',
        label='Минимальная задолженность'
    )
    max_debt = django_filters.NumberFilter(
        field_name='debt_to_supplier',
        lookup_expr='lte',
        label='Максимальная задолженность'
    )
    has_debt = django_filters.BooleanFilter(
        field_name='debt_to_supplier',
        lookup_expr='gt',
        label='Есть задолженность'
    )

    class Meta:
        model = NetworkNode
        fields = ['country', 'city', 'node_type']

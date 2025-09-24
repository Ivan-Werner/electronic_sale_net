from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from electronics.models import NetworkNode, Product
from django.urls import reverse



@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'node_type_display',
        'hierarchy_level_display',
        'city',
        'supplier_link',
        'debt_to_supplier',
        'created_at'
    ]

    list_filter = [
        'city',
        'country',
        'node_type',
        'created_at'
    ]

    search_fields = [
        'name',
        'email',
        'city',
        'country'
    ]

    list_select_related = ['supplier']

    actions = ['clear_debt']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'node_type')
        }),
        ('Контактная информация', {
            'fields': ('email', 'country', 'city', 'street', 'house_number')
        }),
        ('Иерархия и финансы', {
            'fields': ('supplier', 'debt_to_supplier')
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'hierarchy_level_display']

    def node_type_display(self, obj):
        return obj.get_node_type_display()

    node_type_display.short_description = 'Тип звена'

    def hierarchy_level_display(self, obj):
        return obj.hierarchy_level

    hierarchy_level_display.short_description = 'Уровень иерархии'

    def supplier_link(self, obj):
        if obj.supplier:
            url = reverse('admin:electronics_networknode_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "—"

    supplier_link.short_description = 'Поставщик'
    supplier_link.allow_tags = True

    @admin.action(description="Очистить задолженность у выбранных объектов")
    def clear_debt(self, request, queryset):
        updated_count = queryset.update(debt_to_supplier=0.00)
        self.message_user(
            request,
            f"Задолженность очищена у {updated_count} объектов"
        )

    # Фильтр по городу с поиском
    def get_list_filter(self, request):
        base_filters = super().get_list_filter()

        # Добавляем кастомный фильтр для города с поиском
        from django.contrib.admin import SimpleListFilter

        class CityFilter(SimpleListFilter):
            title = 'Город'
            parameter_name = 'city'

            def lookups(self, request, model_admin):
                cities = NetworkNode.objects.values_list('city', flat=True).distinct()
                return [(city, city) for city in cities if city]

            def queryset(self, request, queryset):
                if self.value():
                    return queryset.filter(city=self.value())
                return queryset

        return list(base_filters) + [CityFilter]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'release_date', 'network_node']
    list_filter = ['release_date', 'network_node__city']
    search_fields = ['name', 'model']
    date_hierarchy = 'release_date'

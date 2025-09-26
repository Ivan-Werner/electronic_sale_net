from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import NetworkNode, Product


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'get_node_type_display',
        'get_hierarchy_level',
        'city',
        'supplier_link',
        'debt_to_supplier',
        'created_at'
    ]

    # ПРОСТО И ЭФФЕКТИВНО - стандартные фильтры
    list_filter = ['city', 'country', 'node_type', 'created_at']

    search_fields = ['name', 'email', 'city']
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

    readonly_fields = ['created_at', 'updated_at', 'get_hierarchy_level']

    def get_node_type_display(self, obj):
        return obj.get_node_type_display()

    get_node_type_display.short_description = 'Тип звена'

    def get_hierarchy_level(self, obj):
        return obj.hierarchy_level

    get_hierarchy_level.short_description = 'Уровень иерархии'

    def supplier_link(self, obj):
        if obj.supplier:
            url = reverse('admin:electronics_networknode_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "—"

    supplier_link.short_description = 'Поставщик'

    @admin.action(description="Очистить задолженность у выбранных объектов")
    def clear_debt(self, request, queryset):
        updated_count = queryset.update(debt_to_supplier=0.00)
        self.message_user(request, f"Задолженность очищена у {updated_count} объектов")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'release_date', 'network_node']
    list_filter = ['release_date', 'network_node__city']  # фильтр по связанному полю
    search_fields = ['name', 'model']

from rest_framework import serializers
from .models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at',)


class SupplierSerializer(serializers.ModelSerializer):
    """Сериализатор для поставщика с запретом обновления задолженности"""
    products = ProductSerializer(many=True, read_only=True)
    hierarchy_level = serializers.ReadOnlyField()
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'node_type', 'email', 'country', 'city',
            'street', 'house_number', 'supplier', 'supplier_name',
            'debt_to_supplier', 'created_at', 'updated_at',
            'hierarchy_level', 'products'
        ]
        read_only_fields = ('created_at', 'updated_at', 'hierarchy_level', 'debt_to_supplier')


class SupplierCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания поставщика"""
    class Meta:
        model = NetworkNode
        fields = [
            'name', 'node_type', 'email', 'country', 'city',
            'street', 'house_number', 'supplier', 'debt_to_supplier'
        ]


class SupplierUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления поставщика - запрещает изменения задолжанности"""
    class Meta:
        model = NetworkNode
        fields = [
            'name', 'email', 'country', 'city', 'street', 'house_number'
        ]


class NetworkNodeSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    hierarchy_level = serializers.ReadOnlyField()
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'node_type', 'email', 'country', 'city',
            'street', 'house_number', 'supplier', 'supplier_name',
            'debt_to_supplier', 'created_at', 'updated_at',
            'hierarchy_level', 'products'
        ]
        read_only_fields = ('created_at', 'updated_at', 'hierarchy_level')


class NetworkNodeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания (без продуктов)"""
    class Meta:
        model = NetworkNode
        fields = [
            'name', 'node_type', 'email', 'country', 'city',
            'street', 'house_number', 'supplier', 'debt_to_supplier'
        ]


class NetworkNodeUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления (можно менять не все поля)"""
    class Meta:
        model = NetworkNode
        fields = [
            'name', 'email', 'country', 'city', 'street',
            'house_number', 'debt_to_supplier'
        ]

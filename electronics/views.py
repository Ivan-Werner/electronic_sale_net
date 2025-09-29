from xmlrpc.client import Fault

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response


from .models import NetworkNode, Product
from .serializers import (NetworkNodeSerializer,
                          NetworkNodeCreateSerializer,
                          NetworkNodeUpdateSerializer,
                          ProductSerializer,
                          SupplierSerializer,
                          SupplierCreateSerializer,
                          SupplierUpdateSerializer)
from .filters import NetworkNodeFilter, SupplierFilter
from .permissions import IsActiveEmployee, IsActiveEmployeeOrReadOnly


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций со звеньями сети"""
    queryset = NetworkNode.objects.all().select_related('supplier').prefetch_related('products')
    permission_classes = [IsActiveEmployeeOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NetworkNodeFilter
    search_fields = ['name', 'email', 'city', 'country']
    ordering_fields = ['name', 'city', 'created_at', 'debt_to_supplier']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия"""
        if self.action == 'create':
            return NetworkNodeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NetworkNodeUpdateSerializer
        return NetworkNodeSerializer

    def perform_create(self, serializer):
        """Доп. действия при создании"""
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsActiveEmployee])
    def clear_debt(self, request, pk=None):
        """Кастомное действие для очистки задолженности"""
        node = self.get_object()
        node.debt_to_supplier = 0.00
        node.save()
        return Response({'status': 'Задолженность очищена'})


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с поставщиками.
    Запрещено обновление поля «Задолженность перед поставщиком» через API.
    """
    queryset = NetworkNode.objects.all().select_related('supplier').prefetch_related('products')
    permission_classes = [IsActiveEmployeeOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierFilter # фильтрация по стране
    search_fields = ['name', 'email', 'city', 'country']
    ordering_fields = ['name', 'country', 'city', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return SupplierCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SupplierUpdateSerializer  # запрещает обновление задолженности
        return SupplierSerializer

    @action(detail=False, methods=['get'])
    def factories(self, request):
        """Получить только заводы (уровень 0)"""
        factories = NetworkNode.objects.filter(supplier__isnull=True)
        serializer = self.get_serializer(factories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Фильтрация по стране"""
        country = request.query_params.get('country', '').strip()
        if not country:
            return Response({"error": "Укажите параметр country"}, status=400)

        suppliers = self.queryset.filter(country__iexact=country)
        serializer = self.get_serializer(suppliers, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций с продуктами"""
    queryset = Product.objects.all().select_related('network_node')
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployeeOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['network_node', 'release_date']
    search_fields = ['name', 'model']

    def perform_create(self, serializer):
        serializer.save()


class AdminOnlyViewSet(viewsets.ModelViewSet):
    """ViewSet только для администраторов (полный доступ)."""
    queryset = NetworkNode.objects.all()
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveEmployee]  # только активные сотрудники

    def get_queryset(self):
        return NetworkNode.objects.all()



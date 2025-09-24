from xmlrpc.client import Fault

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


from .models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, NetworkNodeCreateSerializer, NetworkNodeUpdateSerializer, ProductSerializer
from .filters import NetworkNodeFilter


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций со звеньями сети"""
    queryset = NetworkNode.objects.all().select_related('supplier').prefetch_related('products')
    permission_classes = [IsAuthenticated]
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def clear_debt(self, request, pk=None):
        """Кастомное действие для очистки задолженности"""
        node = self.get_object()
        node.debt_to_supplier = 0.00
        node.save()
        return Response({'status': 'Задолженность очищена'})

    @action(detail=False, methods=['get'])
    def factories(self, request):
        """Получить только заводы (уровень 0)"""
        factories = NetworkNode.objects.filter(supplier__isnull=True)
        serializer = self.get_serializer(factories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """Фильтрация по городу через query parameter"""
        city = request.query_params.get('city', None)
        if city:
            nodes = NetworkNode.objects.filter(city__iexact=city)
            serializer = self.get_serializer(nodes, many=True)
            return Response(serializer.data)
        return Response({"error": "Укажите параметр city"}, status=400)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций с продуктами"""
    queryset = Product.objects.all().select_related('network_node')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['network_node', 'release_date']
    search_fields = ['name', 'model']

    def perform_create(self, serializer):
        serializer.save()



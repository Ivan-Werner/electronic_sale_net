from django.urls import path, include
from rest_framework.routers import DefaultRouter

from config.urls import urlpatterns
from .views import NetworkNodeViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'network-nodes', NetworkNodeViewSet, basename='networknode')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('api/', include(router.urls)),
]
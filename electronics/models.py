from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from django.utils import timezone
from django.urls import reverse

class NetworkNode(models.Model):
    """Модель звена сети по продаже электроники"""

    FACTORY = 0
    RETAIL_NETWORK = 1
    INDIVIDUAL_ENTREPRENEUR = 2

    NODE_TYPES = (
        (FACTORY, 'Завод'),
        (RETAIL_NETWORK, 'Розничная сеть'),
        (INDIVIDUAL_ENTREPRENEUR, 'Индивидуальный предприниматель'),
    )

    #Основная информация
    name = models.CharField(
        max_length=255,
        verbose_name='Название звена',
        validators=[MinLengthValidator(2)]
    )

    #Тип звена
    node_type = models.PositiveSmallIntegerField(
        choices=NODE_TYPES,
        verbose_name='Тип звена',
    )

    #Контактная информация
    email = models.EmailField(verbose_name='Email', validators=[EmailValidator()])
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=255, verbose_name='Улица')
    house_number = models.CharField(max_length=20, verbose_name='Номер дома')

    #Иерархические связи
    supplier = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='clients',
        verbose_name='Поставщик'
    )

    #Финансовая информация
    debt_to_supplier = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Задолженность перед поставщиком'
    )

    #Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Время последнего обновления'
    )

    class Meta:
        verbose_name = 'Звено сети'
        verbose_name_plural = 'Звенья сети'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['supplier']),
            models.Index(fields=['node_type']),
        ]

    def __str__(self):
        return f"{self.get_node_type_display()}: {self.name}"

    @property
    def hierarchy_level(self):
        """Динамически вычисляет уровень иерархии"""
        if self.supplier is None:
            return 0

        level = 0
        current = self.supplier

        while current is not None:
            level += 1
            current = current.supplier

        return level

    def get_absolute_url(self):
        return reverse('admin:electronics_networknodedetail_change', args=[self.id])


class Product(models.Model):
    """Модель продукта"""
    name = models.CharField(
        max_length=255,
        verbose_name='Название продукта'
    )
    model = models.CharField(
        max_length=255,
        verbose_name='Модель'
    )
    release_date = models.DateField(
        verbose_name='Дата выхода на рынок'
    )

    # Связь с звеном сети (у одного звена может быть много продуктов)
    network_node = models.ForeignKey(
        NetworkNode,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Звено сети'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-release_date']

    def __str__(self):
        return f"{self.name} {self.model}"

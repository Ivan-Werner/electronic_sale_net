from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    position = models.CharField(max_length=100, blank=True, verbose_name='Должность')

    #Связь со звеном сети
    network_node = models.ForeignKey(
        'electronics.NetworkNode',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Привязанное звено сети'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    @property
    def is_active_employee(self):
        return self.is_active
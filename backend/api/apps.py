"""Модуль инициирования приложения API."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Класс инициирующий приложение."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

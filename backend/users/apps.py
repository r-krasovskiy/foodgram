"""Модуль инициирования приложения для работы с пользователями."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс инициирующий приложение."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

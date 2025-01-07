"""Модуль инициирования приложения Recipes."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Класс инициирующий приложение."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'

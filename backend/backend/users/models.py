"""Модель пользователей."""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from api.constants import MAX_LENGTH_MIDDLE, MAX_LENGTH_SHORT


class User(AbstractUser):
    """Кастомная модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    USER_ROLE = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    ]

    username = models.CharField(
        'Логин пользователя',
        max_length=MAX_LENGTH_SHORT,
        unique=True
    )
    password = models.CharField(
        'Пароль пользователя',
        max_length=MAX_LENGTH_SHORT
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH_MIDDLE
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=MAX_LENGTH_MIDDLE)
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True
    )
    role = models.CharField(
        'Роль пользователя',
        default='User',
        choices=USER_ROLE,
        max_length=MAX_LENGTH_SHORT

    )

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True
    )

    class Meta():
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Subscription(models.Model):
    """Подписка на авторов контента."""
    pass

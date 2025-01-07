"""Модель пользователей."""

from api.constants import MAX_LENGTH_MIDDLE, MAX_LENGTH_SHORT
from django.contrib.auth.models import AbstractUser
from django.db import models


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
    avatar = models.ImageField(
        'Аватар пользователя',
        blank=True,
        null=True,
        upload_to='profiles'
    )

    class Meta():
        """Метаданные модели."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username

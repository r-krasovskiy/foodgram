"""Модель пользователей."""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from api.constants import MAX_LENGTH_MIDDLE
from users.views import CustomUserManager


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
        max_length=MAX_LENGTH_MIDDLE,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Введите корректное имя пользователя.'
                'Допустимы только буквы, цифры и символы @/./+/-/_',
                code='invalid',
            )
        ]
    )
    password = models.CharField(
        'Пароль пользователя',
        max_length=MAX_LENGTH_MIDDLE
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
        upload_to='profiles',
        default=''
    )

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        """Метаданные модели."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username

"""Кастомное создание суперпользователя и пользователей."""

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя."""

    def create_user(self, email, username, password=None, **extra_fields):
        """Создание обычного пользователя."""
        if not email:
            raise ValueError('Email должен быть указан')
        if not username:
            raise ValueError('Имя пользователя (username) должно быть указано')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Создание суперпользователя."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True.'
            )

        if 'first_name' not in extra_fields or 'last_name' not in extra_fields:
            raise ValueError(
                'Для суперпользователя необходимо указать имя и фамилию.'
            )

        return self.create_user(email, username, password, **extra_fields)

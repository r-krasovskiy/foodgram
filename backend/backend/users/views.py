"""Модуль представлений пользователей проекта."""

from django.shortcuts import render
from rest_framework import viewsets

from .models import User
from api.permissions import IsOwnerOrAdmin

class UserViewSet(viewsets.ModelViewSet):
    """Представление пользователя и подписок."""
    queryset = User.objects.all()
    permission_classes = (IsOwnerOrAdmin, )


"""Модуль прав пользователей."""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Права владельца и администратора.

    Владелец или админ - просмотр и редактирование.
    Остальные - только просмотр.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_superuser)

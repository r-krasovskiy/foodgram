"""Модуль прав пользователей."""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Права владельца и администратора.

    Владелец или админ - просмотр и редактирование записей.
    Остальные - только просмотр.
    """

    def has_permission(self, request, view):
        """
        Проверяет общие права доступа.

        Возвращает True, если метод запроса безопасный (GET, HEAD, OPTIONS)
        или пользователь аутентифицирован.
        """
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Проверяет права доступа на уровне объекта.

        Возвращает True, если метод запроса безопасный,
        пользователь является автором объекта или суперпользователем.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_superuser)

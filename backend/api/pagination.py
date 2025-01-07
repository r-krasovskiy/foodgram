"""Модуль для пагинации выдачи ответов API."""

from rest_framework.pagination import PageNumberPagination


class ApiPagination(PageNumberPagination):
    """Пагинация ответов API.

    Позволяет управлять количеством объектов на странице
    через параметр 'limit'.
    По умолчанию возвращается 6 объектов на страницу.
    """

    page_size_query_param = "limit"
    page_size = 6

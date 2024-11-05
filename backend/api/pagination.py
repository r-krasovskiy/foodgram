"""Модуль для пагинации выдачи ответов API."""

from rest_framework.pagination import PageNumberPagination


class ApiPagination(PageNumberPagination):
    """Пагинация ответов API."""

    page_size_query_param = "limit"
    page_size = 6

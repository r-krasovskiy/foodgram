"""Модуль для пагинации выдачи ответов API."""

from rest_framework.pagination import PageNumberPagination

class ApiPaginator(PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })

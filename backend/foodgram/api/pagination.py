from django.conf import settings
from rest_framework.pagination import PageNumberPagination

from api.constants import MAX_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор для вывода 6 элементов на странице."""

    page_size = settings.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE

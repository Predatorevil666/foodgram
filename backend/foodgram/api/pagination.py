from django.conf import settings
from rest_framework.pagination import PageNumberPagination

from api.constants import MAX_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор для вывода 6 элементов на странице."""

    page_size = settings.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE

    # def paginate_queryset(self, queryset, request, view=None):
    #     print(f"Pagination params: page={request.GET.get('page')}, limit={request.GET.get('limit')}")
    #     return super().paginate_queryset(queryset, request, view)
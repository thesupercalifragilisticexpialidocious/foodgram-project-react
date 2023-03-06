from rest_framework.pagination import PageNumberPagination


class FlexiblePagination(PageNumberPagination):
    page_size_query_param = 'limit'

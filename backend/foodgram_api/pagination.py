from rest_framework.pagination import PageNumberPagination as pg


class PageNumberPagination(pg):
    page_size_query_param = 'limit'
    max_page_size = 6

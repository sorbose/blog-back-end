from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ArticleListPagination(PageNumberPagination):
    page_size = 2   # default page size
    page_size_query_param = 'size'  # ?page=xx&size=??
    max_page_size = 10 # max page size
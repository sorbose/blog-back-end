import django_filters
from .models import Article


class ArticleFilter(django_filters.FilterSet):
    year = django_filters.CharFilter(field_name='create_time__year', lookup_expr='icontains')
    month = django_filters.CharFilter(field_name='create_time__month', lookup_expr='icontains')
    class Meta:
        model = Article
        fields = ['content','tag_name','category_name','author','create_time','year','month']


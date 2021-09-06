from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, permissions
from rest_framework import generics
from article.models import Article, BrowseRecord, Tag, Category, ArticleArchive
from account.models import BlogUser
from . import serializers
from rest_framework.response import Response
from rest_framework import filters
from django.http import JsonResponse
from django.utils.decorators import method_decorator



def Success(response):
    d = {
        'success': True,
        'data': response.data
    }
    response.data = d
    return response


class ArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    filter_fields = ['title']
    search_fields = ('title', 'author__username')
    ordering_fields = ('title', 'id')
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, *args, **kwargs):
        return Success(super(ArticleList, self).get(request, *args, **kwargs))


class ArticleDelete(generics.DestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    permission_classes = (permissions.IsAdminUser,)

    def perform_destroy(self, instance):
        for tag in instance.tag_name.all():
            tag.update_number_with_this(-1)
        Category.objects.get(name=instance.category_name.name).update_number_with_this(-1)
        ac = ArticleArchive.objects.get(year=instance.create_time.year, month=instance.create_time.month)
        ac.count -= 1
        ac.save()
        instance.delete()


class UserList(generics.ListCreateAPIView):
    queryset = BlogUser.objects.filter(is_active=1)
    serializer_class = serializers.UserSerializer
    search_fields = ('username', 'email', 'date_joined')
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, *args, **kwargs):
        return Success(super(UserList, self).get(request, *args, **kwargs))

from rest_framework import status
class UserDelete(generics.DestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = BlogUser.objects.all()
    def delete(self, request, *args, **kwargs):
        obj = BlogUser.objects.get(*args,**kwargs)
        obj.is_active = 0
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BrowserList(generics.ListAPIView):
    queryset = BrowseRecord.objects.all()
    serializer_class = serializers.BrowserSerializer
    search_fields = ('time',)
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, *args, **kwargs):
        return Success(super(BrowserList, self).get(request, *args, **kwargs))


class BrowserDelete(generics.DestroyAPIView):
    queryset = BrowseRecord.objects.all()
    permission_classes = (permissions.IsAdminUser,)

def delete_zero(request):
    if request.method == 'DELETE':
        import pymysql
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='blogproject_django', charset='utf8')
        cursor = conn.cursor()
        cursor.callproc('delete_zeros')
        conn.commit()
        return JsonResponse(data={'success': True})

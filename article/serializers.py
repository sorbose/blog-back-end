from rest_framework import serializers
from .models import Article,Tag,Category
from django.core.exceptions import ValidationError
class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Article
        exclude = ('content_HTML','content')
    def get_author(self, instance):
        return instance.author.username


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = '__all__'
    def get_author(self, instance):
        return instance.author.username

    def is_valid(self, raise_exception=False):
        for tag in self.initial_data['tag_name']:
            obj, created = Tag.objects.get_or_create(name=tag)
            obj.update_number_with_this(1)
        obj, created = Category.objects.get_or_create(name=self.initial_data['category_name'])
        obj.update_number_with_this(1)
        return super(ArticleDetailSerializer, self).is_valid(raise_exception)

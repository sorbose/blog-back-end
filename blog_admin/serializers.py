from rest_framework import serializers
from article.models import Article,BrowseRecord
from account.models import BlogUser


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = Article
        fields = '__all__'

    def get_author(self, obj):
        return obj.author.username


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = BlogUser
        exclude = ('password', 'first_name', 'last_name', 'is_staff', 'groups', 'user_permissions')

class BrowserSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    article = serializers.SerializerMethodField()
    time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    def get_user(self, obj):
        return obj.user.username
    def get_article(self, obj):
        return obj.article.title

    class Meta:
        model = BrowseRecord
        fields = '__all__'
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
    class Meta:
        model = BrowseRecord
        fields = '__all__'
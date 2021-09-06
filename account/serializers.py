from rest_framework import serializers
from .models import  BlogUser
from django.contrib.auth.hashers import make_password

class ChangeInfoSerializer(serializers.ModelSerializer):
    birthday = serializers.DateTimeField(required=False)
    class Meta:
        model = BlogUser
        fields = ('birthday','password')

    def validate_password(self,value):
        print('验证')
        if value == '':
            raise serializers.ValidationError('密码不能为空字符串')
        value = make_password(value)
        return value

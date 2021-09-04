from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db import DatabaseError
from rest_framework.exceptions import NotFound
from .views import ArticleList

def common_exception_handler(exc, context):
    response = exception_handler(exc, context)
    # 在此处补充自定义的异常处理
    if response is not None:
        view = context['view']
        if isinstance(view, ArticleList) and isinstance(exc, NotFound):
            response = Response(status=status.HTTP_200_OK,data={
                'success': True,
                'data':{
                    'results':[]
                }
            })
    return response
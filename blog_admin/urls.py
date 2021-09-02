from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('articles/', views.ArticleList.as_view()),
    path('articles/<int:pk>/', views.ArticleDelete.as_view()),
    path('users/',views.UserList.as_view()),
    path('users/<int:pk>',views.UserDelete.as_view()),
    path('browser-record/',views.BrowserList.as_view()),
    path('browser-record/<int:pk>',views.BrowserDelete.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
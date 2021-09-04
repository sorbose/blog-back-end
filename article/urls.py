from django.urls import path
from . import views
urlpatterns = [
    path('tag/create/', views.TagCreateView.as_view()),
    path('tag/delete/', views.TagDeleteView.as_view()),
    path('tag/update/', views.TagUpdateView.as_view()),
    path('tag/query/', views.TagQueryView.as_view()),
    path('category/create/', views.CategoryCreateView.as_view()),
    path('category/delete/', views.CategoryDeleteView.as_view()),
    path('category/update/', views.CategoryUpdateView.as_view()),
    path('category/query/', views.CategoryQueryView.as_view()),
    path('category/reset_count/', views.CategoryResetCountView.as_view()),
    path('tag/reset_count/', views.TagResetCountView.as_view()),
    # path('create/', views.ArticleCreateView.as_view()),
    path('delete/', views.ArticleDeleteView.as_view()),
    path('update/', views.ArticleUpdateView.as_view()),
    path('browse/', views.ArticleBrowseView.as_view()),
    path('getArticleByAuthor/', views.Auther_ArticleQueryView.as_view()),
    path('LastestArticles/', views.LastestArticlesView.as_view()),
    path('search/', views.SearchArticlesView.as_view()),
    # path('advance_search/', views.AdvancedSearchArticlesView.as_view()),
    path('comment/create/', views.CommentCreate.as_view()),
    path('comment/delete/', views.CommentDelete.as_view()),
    path('comment/query/', views.CommentQuery.as_view()),
    path('browser_record/', views.BrowseRecordQuery.as_view()),
    path('upload_file/', views.upload_file),
    path('listArchives/', views.ArticleArchiveView.as_view()),

    path('list/', views.ArticleList.as_view()),
    path('create/', views.ArticleCreate.as_view())
]
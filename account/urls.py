from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [
    path('register/', views.register, name='register'),
    path('getcsrftoken/',views.get_csrftoken,name='getcsrftoken'),
    path('login/',views.user_login,name='user_login'),
    path('logout/',views.user_logout,name='user_logout'),
    path('delete/',views.delete_user,name='delete_user'),
    path('change/', views.change_account_inf),
    path('avatar/', views.upload_avatar),
    path('changepassword/',views.change_password,name='change_password'),
    path('query/',views.query_user,name='query_user'),
    path('query_username_by_id/', views.query_username_by_id),
    path('is_login/',views.is_login,name='is_login'),
    path('is_username_registered/',views.is_username_registered,name='is_username_registered'),
    path('blog_admin/create/',views.create_users,name='create_users'),
    path('<int:pk>/',views.ChangeUserInfo.as_view())
]
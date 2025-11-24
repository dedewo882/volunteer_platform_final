from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'), # 首页默认登录
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.my_profile_view, name='my_profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # 以下路径暂时保留，防止前端链接报错
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('certificate/', views.certificate_placeholder_view, name='certificate_placeholder'),
    path('message-wall/', views.message_wall_view, name='message_wall'),
    path('register/', views.register_view, name='register'),
]
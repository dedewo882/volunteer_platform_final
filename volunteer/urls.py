from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('profile/', views.my_profile_view, name='my_profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('certificate/', views.certificate_placeholder_view, name='certificate_placeholder'),
]
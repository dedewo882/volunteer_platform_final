from django.urls import path
from .views import (
    activity_list, activity_detail, my_profile_view, edit_profile_view,
    login_view, logout_view, certificate_placeholder_view, message_wall_view
) 

urlpatterns = [
    path('', activity_list, name='activity_list'),
    path('activity/<int:activity_id>/', activity_detail, name='activity_detail'),
    path('profile/', my_profile_view, name='my_profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('login/', login_view, name='login'),
    path('accounts/login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('certificate/', certificate_placeholder_view, name='certificate_placeholder'),
    
    # === [新增] 留言墙路由 ===
    path('message-wall/', message_wall_view, name='message_wall'),
]
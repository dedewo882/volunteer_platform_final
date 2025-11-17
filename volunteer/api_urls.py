from django.urls import path
from . import api_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # === 认证接口 ===
    # 前端React应用将向这个URL发送 {username:"学号", password:"密码"}
    # 如果成功，后端会返回 access token 和 refresh token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 用于刷新即将过期的 access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # === 业务API接口 ===
    # 获取所有开放报名的活动列表
    path('activities/', api_views.ActivityListView.as_view(), name='api_activity_list'),
    
    # 获取当前登录用户的个人资料
    path('profile/', api_views.CurrentUserProfileView.as_view(), name='api_my_profile'),
]
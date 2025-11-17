from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Activity
from .serializers import ActivitySerializer, UserSerializer

class ActivityListView(ListAPIView):
    """
    提供所有“报名中”的活动列表。
    这个接口允许任何人访问。
    """
    queryset = Activity.objects.filter(status="报名中").order_by('-id')
    serializer_class = ActivitySerializer
    permission_classes = [AllowAny]

class CurrentUserProfileView(RetrieveAPIView):
    """
    提供当前登录用户的详细信息（包括志愿者档案）。
    这个接口必须在提供了有效的JWT Token后才能访问。
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 直接返回当前通过JWT认证的用户
        return self.request.user
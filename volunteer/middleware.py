from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
import datetime

class TimeRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. 【特赦】允许访问静态文件 (CSS/JS/图片)
        # 如果拦截了这些，sleeping.html 就会变丑，而且这些文件不查数据库，放心放行。
        if request.path.startswith(settings.STATIC_URL) or request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # 3. 获取当前时间 (自动适配 settings.py 里的 Asia/Shanghai 时区)
        now = timezone.localtime(timezone.now()).time()
        
        # 4. 设定闭站时间 (晚上 23:00:00 到 早上 07:00:00)
        start_sleep = datetime.time(23, 0, 0)
        end_sleep = datetime.time(7, 0, 0)

        # 5. 判断逻辑：如果在 23:00 之后 或者 7:00 之前
        if now >= start_sleep or now < end_sleep:
            # === 核心操作 ===
            # 直接返回渲染好的 HTML，坚决不调用 self.get_response(request)
            # 这意味着后续的 SessionMiddleware、AuthMiddleware 统统不会执行
            # 数据库也就根本不知道有这回事。
            return render(request, 'volunteer/sleeping.html', status=503)

        return self.get_response(request)
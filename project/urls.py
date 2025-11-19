from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('volunteer.urls')),
    
    # 修复富文本：添加 ckeditor 的路由
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# 生产模式下，让 Django 托管 media/static 文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
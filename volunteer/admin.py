import pandas as pd
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path, re_path
from django.db.models import F
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from .models import VolunteerProfile, Activity, Registration, Grade, Announcement
from django.http import HttpResponse
import datetime

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

def export_as_excel(modeladmin, request, queryset):
    field_names = ['student__user__first_name', 'student__student_id', 'activity__title', 'phone_number', 'class_name', 'headteacher_name', 'registered_at']
    df = pd.DataFrame(list(queryset.values(*field_names)))
    df.rename(columns={
        'student__user__first_name': '姓名',
        'student__student_id': '学号',
        'activity__title': '活动名称',
        'phone_number': '手机号',
        'class_name': '班级',
        'headteacher_name': '班主任',
        'registered_at': '报名时间'
    }, inplace=True)
    df['报名时间'] = df['报名时间'].apply(lambda a: a.strftime('%Y-%m-%d %H:%M:%S') if a else '')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    filename = f"报名记录_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    df.to_excel(response, index=False)
    return response
export_as_excel.short_description = "导出所选记录为 Excel"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'registered_at')
    list_filter = ('activity',)
    search_fields = ('student__student_id', 'activity__title')
    actions = [export_as_excel]

class VolunteerProfileInline(admin.StackedInline):
    model = VolunteerProfile
    can_delete = False
    verbose_name_plural = '志愿者档案'
    fields = ('student_id', 'total_hours', 'total_xp', 'gender', 'grade')

class CustomUserChangeForm(UserChangeForm):
    first_name = forms.CharField(label="姓名", max_length=100)
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class CustomUserCreationForm(forms.ModelForm):
    """自定义用户创建表单，修改密码验证逻辑"""
    first_name = forms.CharField(label="姓名", max_length=100)
    password = forms.CharField(label="密码", widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ("username", "first_name")
    
    def save(self, commit=True):
        """保存用户并设置密码"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    inlines = (VolunteerProfileInline,)
    list_display = ('username', 'first_name', 'is_staff')
    list_editable = ('first_name',)
    search_fields = ('username', 'first_name')
    fieldsets = ((None, {'fields': ('username', 'password')}),('个人信息', {'fields': ('first_name',)}),('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),('重要日期', {'fields': ('last_login', 'date_joined')}),)
    add_fieldsets = ((None, {'classes': ('wide',),'fields': ('username', 'first_name', 'password'),}),)

    def get_urls(self):
        from django.urls import re_path
        urls = super().get_urls()
        custom_urls = [re_path(r'^batch_create/$', self.admin_site.admin_view(self.batch_create_view), name='batch_create')]
        return custom_urls + urls

    @transaction.atomic
    def batch_create_view(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get("excel_file")
            try:
                df = pd.read_excel(excel_file, dtype=str)
                created_count = 0
                for index, row in df.iterrows():
                    student_id = row['学号']
                    name = row['姓名']
                    password = row['初始密码']
                    if User.objects.filter(username=student_id).exists():
                        messages.warning(request, f"学号 {student_id} 已存在，跳过。")
                        continue
                    user = User.objects.create_user(username=student_id, password=password, first_name=name)
                    VolunteerProfile.objects.create(user=user, student_id=student_id)
                    created_count += 1
                messages.success(request, f"成功创建 {created_count} 个账号。")
            except Exception as e:
                messages.error(request, f"处理文件出错: {e}")
            return redirect('..')
        return render(request, 'admin/batch_create_users.html')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'capacity', 'hours_reward')
    list_filter = ('status',)
    search_fields = ('title',)
    filter_horizontal = ('grade_restriction',)
    
    def get_urls(self):
        from django.urls import re_path
        urls = super().get_urls()
        custom_urls = [re_path(r'^(?P<activity_id>\d+)/upload_hours/$', self.admin_site.admin_view(self.upload_hours_view), name='upload_hours')]
        return custom_urls + urls

    @transaction.atomic
    def upload_hours_view(self, request, activity_id):
        activity = Activity.objects.get(pk=activity_id)
        if request.method == 'POST':
            excel_file = request.FILES.get("excel_file")
            try:
                df = pd.read_excel(excel_file, dtype={'学号': str})
                updated_count = 0
                for index, row in df.iterrows():
                    student_id = row['学号']
                    hours_to_add = int(float(row['工时']))
                    try:
                        profile = VolunteerProfile.objects.get(student_id=student_id)
                        profile.total_hours = F('total_hours') + hours_to_add
                        profile.total_xp = F('total_xp') + hours_to_add
                        profile.save()
                        updated_count += 1
                    except VolunteerProfile.DoesNotExist:
                        messages.warning(request, f"未找到学号为 {student_id} 的志愿者档案，跳过。")
                messages.success(request, f"成功为 {updated_count} 名志愿者更新了时长。")
            except Exception as e:
                messages.error(request, f"处理文件出错: {e}")
            return redirect('..')
        context = dict(self.admin_site.each_context(request), activity=activity, title=f"为 '{activity.title}' 上传时长")
        return render(request, 'admin/upload_hours.html', context)
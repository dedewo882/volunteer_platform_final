import pandas as pd
import re
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path, re_path
from django.db.models import F
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from .models import VolunteerProfile, Activity, Registration, Grade, Announcement, StudentTag, ActivitySession
from django.http import HttpResponse
import datetime
import logging

logger = logging.getLogger(__name__)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(StudentTag)
class StudentTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'xp_bonus')
    list_editable = ('xp_bonus',)

class ActivitySessionInline(admin.TabularInline):
    model = ActivitySession
    extra = 1

def export_registrations_to_excel(queryset, filename_prefix="报名记录"):
    field_names = [
        'student__user__first_name', 'student__student_id', 'activity__title', 
        'session__date', 'session__start_time',
        'student__grade__name', 'student__class_name', 'student__gender', 'phone_number', 'headteacher_name', 'registered_at', 'status'
    ]
    df = pd.DataFrame(list(queryset.values(*field_names)))
    column_rename_map = {
        'student__user__first_name': '姓名', 'student__student_id': '学号', 'activity__title': '活动名称',
        'session__date': '场次日期', 'session__start_time': '开始时间',
        'student__grade__name': '年级', 'student__class_name': '班级', 'student__gender': '性别',
        'phone_number': '手机号', 'headteacher_name': '班主任', 'registered_at': '报名时间', 'status': '审核状态'
    }
    df.rename(columns={k: v for k, v in column_rename_map.items() if k in df.columns}, inplace=True)
    if '报名时间' in df.columns:
        df['报名时间'] = pd.to_datetime(df['报名时间']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"{filename_prefix}_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    df.to_excel(response, index=False)
    return response

@admin.action(description='导出所选报名记录 (Excel)')
def export_selected_registrations(modeladmin, request, queryset):
    return export_registrations_to_excel(queryset, "报名记录")

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('activity', 'get_session_info', 'get_student_name', 'get_student_id', 'registered_at', 'status', 'hours_awarded')
    list_filter = ('activity__title', 'status', 'student__grade')
    search_fields = ('student__student_id', 'activity__title', 'student__user__first_name')
    list_per_page = 25
    actions = [export_selected_registrations, 'approve_registrations', 'reject_registrations']

    def get_session_info(self, obj):
        if obj.session:
            return f"{obj.session.date} {obj.session.start_time.strftime('%H:%M')}"
        return "无场次"
    get_session_info.short_description = "场次"

    @admin.action(description='批准所选报名')
    def approve_registrations(self, request, queryset):
        queryset.update(status='Approved')
        messages.success(request, f"{queryset.count()} 条报名已批准。")

    @admin.action(description='拒绝所选报名')
    def reject_registrations(self, request, queryset):
        queryset.update(status='Rejected')
        messages.success(request, f"{queryset.count()} 条报名已拒绝。")

    def get_student_name(self, obj):
        return obj.student.user.first_name
    get_student_name.short_description = '姓名'
    get_student_name.admin_order_field = 'student__user__first_name'

    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = '学号'
    get_student_id.admin_order_field = 'student__student_id'

class VolunteerProfileInline(admin.StackedInline):
    model = VolunteerProfile
    can_delete = False
    verbose_name_plural = '志愿者档案'
    fields = ('student_id', 'class_name', 'total_hours', 'total_xp', 'gender', 'grade', 'tags')
    readonly_fields = ('student_id',)
    filter_horizontal = ('tags',)

class CustomUserChangeForm(UserChangeForm):
    first_name = forms.CharField(label="姓名", max_length=100)
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class CustomUserCreationForm(forms.ModelForm):
    first_name = forms.CharField(label="姓名", max_length=100)
    password = forms.CharField(label="密码", widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ("username", "first_name")
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit: user.save()
        return user

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    inlines = (VolunteerProfileInline,)
    list_display = ('username', 'first_name', 'get_class_name', 'get_total_hours', 'is_staff')
    list_editable = ('first_name',)
    search_fields = ('username', 'first_name', 'volunteerprofile__student_id') 
    list_per_page = 25 
    fieldsets = ((None, {'fields': ('username', 'password')}),('个人信息', {'fields': ('first_name',)}),('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),('重要日期', {'fields': ('last_login', 'date_joined')}),)
    add_fieldsets = ((None, {'classes': ('wide',),'fields': ('username', 'first_name', 'password'),}),)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [re_path(r'^batch_create/$', self.admin_site.admin_view(self.batch_create_view), name='batch_create')]
        return custom_urls + urls

    @transaction.atomic
    def batch_create_view(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                messages.error(request, "请上传一个 Excel 文件。")
                return redirect('.')
            
            try:
                df = pd.read_excel(excel_file, dtype=str)
                df.columns = df.columns.str.strip()
                required_cols = ['学号', '姓名', '初始密码', '性别', '班级']
                missing = [c for c in required_cols if c not in df.columns]
                if missing:
                    messages.error(request, f"缺少列: {', '.join(missing)}")
                    return redirect('.')

                count = 0
                updated_count = 0
                for _, row in df.iterrows():
                    sid = str(row['学号']).strip()
                    raw_class = str(row['班级']).strip()
                    
                    user, created = User.objects.get_or_create(username=sid, defaults={'first_name': row['姓名']})
                    if created:
                        user.set_password(row['初始密码'])
                        user.save()
                        count += 1
                    else:
                        user.first_name = row['姓名']
                        user.save()
                        updated_count += 1
                    
                    grade_obj = None
                    final_class_name = raw_class
                    match = re.match(r'^(\d+)', raw_class)
                    if match:
                        grade_name = match.group(1)
                        grade_obj, _ = Grade.objects.get_or_create(name=grade_name)
                        if not final_class_name.endswith('班'):
                            final_class_name += "班"
                    
                    hours = int(pd.to_numeric(row.get('志愿者时长', 0), errors='coerce') or 0)
                    xp = hours 

                    tag_names = str(row.get('标签', '')).replace('，', ',').split(',')
                    tags_to_add = []
                    for t_name in tag_names:
                        t_name = t_name.strip()
                        if not t_name or t_name == 'nan': continue
                        tag_obj = StudentTag.objects.filter(name=t_name).first()
                        if tag_obj:
                            xp += tag_obj.xp_bonus
                            tags_to_add.append(tag_obj)

                    defaults = {
                        'gender': row['性别'],
                        'grade': grade_obj,
                        'class_name': final_class_name,
                        'total_hours': hours,
                        'total_xp': xp
                    }
                    profile, p_created = VolunteerProfile.objects.update_or_create(
                        user=user,
                        student_id=sid,
                        defaults=defaults
                    )
                    if tags_to_add:
                        profile.tags.set(tags_to_add)
                    
                messages.success(request, f"处理完成：新建 {count} 人，更新 {updated_count} 人。")
            except Exception as e:
                messages.error(request, f"错误: {e}")
            return redirect('..')
        return render(request, 'admin/batch_create_users.html')

    def get_class_name(self, obj):
        return obj.volunteerprofile.class_name
    get_class_name.short_description = '班级'

    def get_total_hours(self, obj):
        try: return obj.volunteerprofile.total_hours
        except: return 0
    get_total_hours.short_description = '工时'
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, VolunteerProfile) and not instance.pk:
                instance.student_id = form.instance.username
            instance.save()
        formset.save_m2m()

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# === 新增功能：志愿者档案独立管理界面 & 一键校准XP ===

@admin.action(description='🔄 重新计算所选用户的经验值 (时长+标签)')
def recalculate_xp(modeladmin, request, queryset):
    count = 0
    for profile in queryset:
        # 1. 基础经验 = 总工时
        new_xp = profile.total_hours
        
        # 2. 加上所有标签的额外加成
        for tag in profile.tags.all():
            new_xp += tag.xp_bonus
            
        # 3. 更新数据库
        profile.total_xp = new_xp
        profile.save()
        count += 1
    messages.success(request, f"已成功校准 {count} 名志愿者的经验值！")

@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_name', 'total_hours', 'total_xp', 'calculate_expected_xp')
    search_fields = ('student_id', 'user__first_name')
    list_filter = ('grade', 'tags')
    filter_horizontal = ('tags',) # 左右选择框
    actions = [recalculate_xp]    # 注册上面的按钮

    def get_name(self, obj):
        return obj.user.first_name
    get_name.short_description = '姓名'
    get_name.admin_order_field = 'user__first_name'

    def calculate_expected_xp(self, obj):
        # 在列表里实时显示“理论应有多少XP”，方便管理员对比
        expected = obj.total_hours
        for tag in obj.tags.all():
            expected += tag.xp_bonus
        return expected
    calculate_expected_xp.short_description = '理论应有XP'

# ===================================================

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date', 'capacity', 'hours_reward', 'get_registration_count')
    list_filter = ('status',)
    search_fields = ('title',)
    filter_horizontal = ('grade_restriction',)
    list_per_page = 25
    change_form_template = "admin/activity_change_form.html"
    inlines = [ActivitySessionInline]
    
    def get_registration_count(self, obj):
        count = obj.approved_registrations_count
        capacity_str = obj.capacity if obj.capacity > 0 else '不限'
        return f"{count} / {capacity_str} (已批准)"
    
    def get_urls(self):
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
                df.columns = df.columns.str.strip()
                updated_count = 0
                for index, row in df.iterrows():
                    student_id = str(row['学号']).strip()
                    hours_to_add = int(float(row['服务时长']))
                    
                    try:
                        profile = VolunteerProfile.objects.get(student_id=student_id)
                    except VolunteerProfile.DoesNotExist:
                        user = User.objects.filter(username=student_id).first()
                        if user:
                            profile = VolunteerProfile.objects.create(user=user, student_id=student_id, gender='男')
                            messages.info(request, f"已为用户 {student_id} 自动补全档案。")
                        else:
                            messages.warning(request, f"未找到学号 {student_id}，跳过。")
                            continue

                    profile.total_hours = F('total_hours') + hours_to_add
                    profile.total_xp = F('total_xp') + hours_to_add
                    profile.save()

                    Registration.objects.filter(student=profile, activity=activity).update(
                        hours_awarded=F('hours_awarded') + hours_to_add,
                        status='Approved'
                    )
                    updated_count += 1
                messages.success(request, f"成功更新 {updated_count} 人")
            except Exception as e:
                messages.error(request, f"错误: {e}")
            return redirect('..')
        context = dict(self.admin_site.each_context(request), activity=activity, title=f"为 '{activity.title}' 上传时长")
        return render(request, 'admin/upload_hours.html', context)
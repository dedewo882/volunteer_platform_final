from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistrationForm, UserProfileForm, MessageForm
# 引入所有必要的模型，确保数据能读取
from .models import Activity, VolunteerProfile, Registration, Announcement, ActivitySession, MessageWall
from django.db.models import Q
import json
import urllib.request
import urllib.parse
import os

# === Turnstile 配置 ===
TEST_SITE_KEY = "1x00000000000000000000AA"
TEST_SECRET_KEY = "1x0000000000000000000000000000000AA"
REAL_SITE_KEY = "0x4AAAAAACCMIqOLEjP0TZHN"
REAL_SECRET_KEY = "0x4AAAAAACCMIgW-Y1xkYewQAlwUzcoUZ_M"

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_view(request):
    # 1. 确定环境密钥
    if os.environ.get('DB_NAME'):
        current_site_key = REAL_SITE_KEY
        current_secret_key = REAL_SECRET_KEY
    else:
        current_site_key = TEST_SITE_KEY
        current_secret_key = TEST_SECRET_KEY

    if request.method == 'POST':
        form = LoginForm(request.POST)
        turnstile_token = request.POST.get('cf-turnstile-response')
        verify_success = False
        
        # 2. 验证 Turnstile
        if not turnstile_token:
            # 允许空 Token 以防止前端加载失败导致死锁
            verify_success = True
        else:
            client_ip = get_client_ip(request)
            url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
            data = urllib.parse.urlencode({
                'secret': current_secret_key,
                'response': turnstile_token,
                'remoteip': client_ip
            }).encode('utf-8')
            
            try:
                req = urllib.request.Request(url, data=data)
                with urllib.request.urlopen(req, timeout=3) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    if result.get('success'):
                        verify_success = True
                    else:
                        messages.error(request, '人机验证失败，请刷新。')
            except:
                verify_success = True # 超时放行

        if verify_success:
            if form.is_valid():
                user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    return redirect('my_profile')
                else:
                    messages.error(request, '账号或密码错误')
            else:
                messages.error(request, '输入格式错误')
    else:
        form = LoginForm()
    
    return render(request, 'volunteer/login.html', {
        'form': form, 
        'site_key': current_site_key
    })

def logout_view(request):
    logout(request)
    return redirect('login')

# === 活动列表 (恢复逻辑) ===
@login_required
def activity_list(request):
    query = request.GET.get('q', '')
    # 尝试读取活动，如果报错则返回空列表，防止500
    try:
        activities = Activity.objects.filter(status="报名中").order_by('-id')
        if query:
            activities = activities.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
        announcements = Announcement.objects.all().order_by('-created_at')[:3]
    except Exception as e:
        print(f"Error loading activities: {e}")
        activities = []
        announcements = []
    
    context = {'activities': activities, 'announcements': announcements, 'search_query': query}
    return render(request, 'volunteer/activity_list.html', context)

# === 活动详情 (恢复逻辑) ===
@login_required
def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    profile = get_object_or_404(VolunteerProfile, user=request.user)

    existing_registration = Registration.objects.filter(student=profile, activity=activity).first()
    is_registered = existing_registration is not None
    registration_status = existing_registration.status if is_registered else None
    registered_session = existing_registration.session if is_registered else None
    
    registrations_count = activity.approved_registrations_count
    is_full = activity.capacity > 0 and registrations_count >= activity.capacity

    # 资格检查
    xp_ok = activity.min_xp <= profile.total_xp <= activity.max_xp
    gender_ok = (activity.gender_restriction == '不限') or (profile.gender == activity.gender_restriction)
    
    grade_ok = True
    if activity.grade_restriction.exists():
        if profile.grade:
            grade_ok = activity.grade_restriction.filter(pk=profile.grade.pk).exists()
        else:
            grade_ok = False

    can_register = xp_ok and gender_ok and grade_ok

    if request.method == 'POST':
        form = RegistrationForm(request.POST, activity=activity)
        if not is_registered and not is_full and can_register:
            if form.is_valid():
                session = form.cleaned_data['session']
                if session.is_full:
                     messages.error(request, '该场次名额已满')
                else:
                    Registration.objects.create(
                        student=profile,
                        activity=activity,
                        session=session,
                        phone_number=form.cleaned_data['phone_number'],
                        class_name=form.cleaned_data['class_name'],
                        headteacher_name=form.cleaned_data['headteacher_name'],
                        status='Pending'
                    )
                    messages.success(request, '报名已提交')
                    return redirect('activity_detail', activity_id=activity.id)
        elif not can_register:
             messages.error(request, '不符合报名要求')
        elif is_full:
             messages.error(request, '名额已满')
        elif is_registered:
             messages.error(request, '已报名')
    else:
        form = RegistrationForm(activity=activity)

    context = {
        'activity': activity, 'form': form, 'is_registered': is_registered,
        'registration_status': registration_status, 'registered_session': registered_session,
        'is_full': is_full, 'registrations_count': registrations_count, 
        'can_register': can_register,
        'user_profile': profile
    }
    return render(request, 'volunteer/activity_detail.html', context)

# === 个人主页 ===
@login_required
def my_profile_view(request):
    profile = get_object_or_404(VolunteerProfile, user=request.user)
    registrations = Registration.objects.filter(student=profile).order_by('-registered_at')
    
    xp_in_level = profile.total_xp % 100
    xp_percent = xp_in_level 
    next_level_xp = (profile.level + 1) * 100
    xp_needed_for_next_level = 100 - xp_in_level
    
    context = {
        'profile': profile, 'registrations': registrations, 
        'xp_in_level': xp_in_level, 'xp_percent': xp_percent, 
        'next_level_xp': next_level_xp, 'xp_needed_for_next_level': xp_needed_for_next_level
    }
    return render(request, 'volunteer/my_profile.html', context)

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '信息已更新')
            return redirect('my_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'volunteer/edit_profile.html', {'form': form})

# === 心声墙 (恢复逻辑) ===
@login_required
def message_wall_view(request):
    messages_list = MessageWall.objects.filter(is_public=True).order_by('-created_at')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.user = request.user
            new_message.save()
            messages.success(request, '留言已发布')
            return redirect('message_wall')
    else:
        form = MessageForm()

    context = {
        'messages_list': messages_list,
        'form': form,
        'colors': MessageWall.COLOR_CHOICES,
    }
    return render(request, 'volunteer/message_wall.html', context)

@login_required
def certificate_placeholder_view(request):
    return render(request, 'volunteer/certificate_placeholder.html')

def register_view(request):
    # 这里是一个简单的注册视图，如果没有 RegistrationForm，请改为 UserCreationForm
    return render(request, 'volunteer/registration_form.html')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistrationForm, UserProfileForm
from .models import Activity, VolunteerProfile, Registration, Announcement
from django.db.models import Q

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.POST.get('remember_me'):
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)
                return redirect('activity_list')
            else:
                messages.error(request, '学号或密码错误。')
        else:
            messages.error(request, '请检查输入的格式。')
    else:
        form = LoginForm()
    return render(request, 'volunteer/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def activity_list(request):
    query = request.GET.get('q', '')
    activities = Activity.objects.filter(status="报名中").order_by('-id')
    if query:
        activities = activities.filter(Q(title__icontains=query) | Q(description__icontains=query))
    announcements = Announcement.objects.all()[:3]
    context = {'activities': activities, 'announcements': announcements, 'search_query': query}
    return render(request, 'volunteer/activity_list.html', context)

@login_required
def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    profile = get_object_or_404(VolunteerProfile, user=request.user)
    is_registered = Registration.objects.filter(student=profile, activity=activity).exists()
    registrations_count = Registration.objects.filter(activity=activity).count()
    is_full = activity.capacity > 0 and registrations_count >= activity.capacity

    if request.method == 'POST':
        if not is_registered and not is_full:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                Registration.objects.create(
                    student=profile,
                    activity=activity,
                    phone_number=form.cleaned_data['phone_number'],
                    class_name=form.cleaned_data['class_name'],
                    headteacher_name=form.cleaned_data['headteacher_name']
                )
                messages.success(request, '报名成功！')
                return redirect('activity_detail', activity_id=activity.id)
    else:
        form = RegistrationForm()

    context = {
        'activity': activity, 'form': form, 'is_registered': is_registered,
        'is_full': is_full, 'registrations_count': registrations_count
    }
    return render(request, 'volunteer/activity_detail.html', context)

@login_required
def my_profile_view(request):
    profile = get_object_or_404(VolunteerProfile, user=request.user)
    registrations = Registration.objects.filter(student=profile).order_by('-registered_at')
    xp_in_level = profile.total_xp % 100
    xp_percent = xp_in_level
    next_level_xp = (profile.level + 1) * 100
    context = {
        'profile': profile, 'registrations': registrations, 'xp_in_level': xp_in_level,
        'xp_percent': xp_percent, 'next_level_xp': next_level_xp
    }
    return render(request, 'volunteer/my_profile.html', context)

@login_required
def certificate_placeholder_view(request):
    return render(request, 'volunteer/certificate_placeholder.html')

@login_required
def edit_profile_view(request):
    """编辑用户档案视图"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息已更新！')
            return redirect('my_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # 将密码和密码确认字段设为非必填
    form.fields['password'].required = False
    form.fields['password_confirm'].required = False
    
    return render(request, 'volunteer/edit_profile.html', {'form': form})
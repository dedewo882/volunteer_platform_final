from django import forms
from django.contrib.auth.models import User
from .models import ActivitySession

class LoginForm(forms.Form):
    username = forms.CharField(label='学号', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

class RegistrationForm(forms.Form):
    phone_number = forms.CharField(label='手机号', max_length=20)
    class_name = forms.CharField(label='班级', max_length=50)
    headteacher_name = forms.CharField(label='班主任姓名', max_length=50)
    
    session = forms.ModelChoiceField(
        queryset=ActivitySession.objects.none(), 
        label="选择场次", 
        required=True,
        empty_label="-- 请选择参加时间 --"
    )

    def __init__(self, *args, **kwargs):
        activity = kwargs.pop('activity', None)
        super().__init__(*args, **kwargs)
        if activity:
            self.fields['session'].queryset = activity.sessions.all()

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(label='密码确认', widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name')
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password_confirm and not password:
            return password_confirm
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("两次输入的密码不一致")
        return password_confirm
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
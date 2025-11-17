from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(label='学号', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

class RegistrationForm(forms.Form):
    phone_number = forms.CharField(label='手机号', max_length=20)
    class_name = forms.CharField(label='班级', max_length=50)
    headteacher_name = forms.CharField(label='班主任姓名', max_length=50)

class UserProfileForm(forms.ModelForm):
    """用户档案编辑表单，处理密码字段验证"""
    password = forms.CharField(label='密码', widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(label='密码确认', widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name')
    
    def clean_password_confirm(self):
        # 移除密码确认的必填验证，只有当输入密码时才进行匹配验证
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        # 如果只填写了密码确认，而没有填写密码，也不报错
        if password_confirm and not password:
            return password_confirm
        
        # 如果两者都填写了，才进行匹配验证
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("两次输入的密码不一致")
        
        return password_confirm
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # 只有当填写了密码时，才更新密码
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
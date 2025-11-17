from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Announcement(models.Model):
    title = models.CharField("标题", max_length=200)
    content = models.TextField("内容")
    created_at = models.DateTimeField("发布时间", auto_now_add=True)

    class Meta:
        verbose_name = "公告"
        verbose_name_plural = "公告"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Grade(models.Model):
    name = models.CharField("年级名称", max_length=100, unique=True)
    class Meta:
        verbose_name = "年级"
        verbose_name_plural = "年级"
    def __str__(self):
        return self.name

class VolunteerProfile(models.Model):
    GENDER_CHOICES = (('男', '男'), ('女', '女'),)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="关联用户")
    student_id = models.CharField("学号", max_length=100, unique=True)
    total_hours = models.PositiveIntegerField("总服务时长", default=0)
    total_xp = models.PositiveIntegerField("总经验值", default=0)
    gender = models.CharField("性别", max_length=2, choices=GENDER_CHOICES, default='男')
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="年级")
    class Meta:
        verbose_name = "志愿者档案"
        verbose_name_plural = "志愿者档案"
    def __str__(self):
        return f"{self.user.first_name} ({self.student_id})"
    @property
    def level(self):
        return self.total_xp // 100

class Activity(models.Model):
    STATUS_CHOICES = (('报名中', '报名中'), ('进行中', '进行中'), ('已结束', '已结束'),)
    GENDER_CHOICES = (('不限', '不限'), ('男', '男'), ('女', '女'),)
    title = models.CharField("活动标题", max_length=200)
    description = RichTextField("活动详情")
    status = models.CharField("活动状态", max_length=10, choices=STATUS_CHOICES, default='报名中')
    hours_reward = models.PositiveIntegerField("可获时长", default=0)
    min_xp = models.PositiveIntegerField("最低经验值要求", default=0)
    max_xp = models.PositiveIntegerField("最高经验值要求", default=10000)
    gender_restriction = models.CharField("性别限制", max_length=2, choices=GENDER_CHOICES, default='不限')
    grade_restriction = models.ManyToManyField(Grade, blank=True, verbose_name="年级限制")
    capacity = models.PositiveIntegerField("名额上限", default=0, help_text="设置为0表示无人数限制")
    class Meta:
        verbose_name = "活动"
        verbose_name_plural = "活动"
    def __str__(self):
        return self.title

class Registration(models.Model):
    student = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, verbose_name="学生")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动")
    registered_at = models.DateTimeField("报名时间", auto_now_add=True)
    phone_number = models.CharField("手机号", max_length=20)
    class_name = models.CharField("班级", max_length=50)
    headteacher_name = models.CharField("班主任姓名", max_length=50)
    class Meta:
        verbose_name = "报名记录"
        verbose_name_plural = "报名记录"
        unique_together = ('student', 'activity')
    def __str__(self):
        return f"{self.student} 报名了 {self.activity}"
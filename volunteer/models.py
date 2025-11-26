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

class StudentTag(models.Model):
    name = models.CharField("标签名称", max_length=50, unique=True)
    xp_bonus = models.PositiveIntegerField("额外经验加成", default=0)
    class Meta:
        verbose_name = "学生标签/职务"
        verbose_name_plural = "学生标签/职务"
    def __str__(self):
        return f"{self.name} (+{self.xp_bonus} XP)"

class VolunteerProfile(models.Model):
    GENDER_CHOICES = (('男', '男'), ('女', '女'),)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="关联用户")
    student_id = models.CharField("学号", max_length=100, unique=True)
    class_name = models.CharField("班级", max_length=100, blank=True, null=True) 
    total_hours = models.PositiveIntegerField("总服务时长", default=0)
    total_xp = models.PositiveIntegerField("总经验值", default=0)
    gender = models.CharField("性别", max_length=2, choices=GENDER_CHOICES, default='男')
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="年级")
    tags = models.ManyToManyField(StudentTag, blank=True, verbose_name="职务/标签")

    class Meta:
        verbose_name = "志愿者档案"
        verbose_name_plural = "志愿者档案"
    def __str__(self):
        return f"{self.user.first_name} ({self.student_id})"
    
    @property
    def level(self):
        return self.total_xp // 100

    @property
    def rank(self):
        lvl = self.level
        if lvl <= 10: return "青铜"
        elif lvl <= 30: return "白银"
        elif lvl <= 60: return "黄金"
        elif lvl <= 100: return "铂金"
        else: return "钻石"

class Activity(models.Model):
    STATUS_CHOICES = (('报名中', '报名中'), ('进行中', '进行中'), ('已结束', '已结束'),)
    GENDER_CHOICES = (('不限', '不限'), ('男', '男'), ('女', '女'),)
    title = models.CharField("活动标题", max_length=200)
    description = RichTextField("活动详情")
    status = models.CharField("活动状态", max_length=10, choices=STATUS_CHOICES, default='报名中')
    start_date = models.DateField("活动开始日期", null=True, blank=True)
    end_date = models.DateField("活动结束日期", null=True, blank=True)
    hours_reward = models.PositiveIntegerField("可获时长", default=0)
    min_xp = models.PositiveIntegerField("最低经验值要求", default=0)
    max_xp = models.PositiveIntegerField("最高经验值要求", default=10000)
    gender_restriction = models.CharField("性别限制", max_length=2, choices=GENDER_CHOICES, default='不限')
    grade_restriction = models.ManyToManyField(Grade, blank=True, verbose_name="年级限制")
    capacity = models.PositiveIntegerField("总名额上限", default=0, help_text="设置为0表示无人数限制")

    class Meta:
        verbose_name = "活动"
        verbose_name_plural = "活动"
    def __str__(self):
        return self.title

    @property
    def approved_registrations_count(self):
        return self.registration_set.filter(status='Approved').count()

class ActivitySession(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='sessions', verbose_name="所属活动")
    date = models.DateField("日期")
    start_time = models.TimeField("开始时间")
    end_time = models.TimeField("结束时间")
    location = models.CharField("地点", max_length=100, blank=True)
    capacity = models.PositiveIntegerField("本场次名额", default=0)

    class Meta:
        verbose_name = "活动场次"
        verbose_name_plural = "活动场次"
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} ({self.location})"
    
    @property
    def current_count(self):
        return self.registrations.exclude(status='Rejected').count()

    @property
    def is_full(self):
        if self.capacity == 0: return False
        return self.current_count >= self.capacity

class Registration(models.Model):
    STATUS_CHOICES = (
        ('Pending', '待审核'),
        ('Approved', '已批准'),
        ('Rejected', '已拒绝'),
    )
    
    student = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, verbose_name="学生")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动")
    session = models.ForeignKey(ActivitySession, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations', verbose_name="选择场次")
    registered_at = models.DateTimeField("报名时间", auto_now_add=True)
    phone_number = models.CharField("手机号", max_length=20)
    class_name = models.CharField("班级", max_length=50)
    headteacher_name = models.CharField("班主任姓名", max_length=50)
    status = models.CharField("审核状态", max_length=10, choices=STATUS_CHOICES, default='Pending')
    hours_awarded = models.PositiveIntegerField("获得时长", default=0, help_text="本次报名实际获得的时长")
    
    class Meta:
        verbose_name = "报名记录"
        verbose_name_plural = "报名记录"
        unique_together = ('student', 'activity', 'session')
    def __str__(self):
        return f"{self.student} 报名了 {self.activity} ({self.get_status_display()})"

# === [新增] 留言墙模型 ===
class MessageWall(models.Model):
    COLOR_CHOICES = (
        ('warning', '暖阳黄'),
        ('info', '天空蓝'),
        ('success', '草地绿'),
        ('danger', '樱花粉'),
        ('primary', '静谧紫'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="留言者")
    content = models.TextField("留言内容", max_length=200) 
    color = models.CharField("便利贴颜色", max_length=20, choices=COLOR_CHOICES, default='warning')
    created_at = models.DateTimeField("留言时间", auto_now_add=True)
    is_public = models.BooleanField("是否公开", default=True, help_text="取消勾选则仅管理员可见")
    is_anonymous = models.BooleanField("匿名发布", default=False, help_text="勾选后其他人看不到你的姓名")

    class Meta:
        verbose_name = "心声/留言"
        verbose_name_plural = "心声/留言"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.first_name}: {self.content[:20]}..."
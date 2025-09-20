"""
User and Authentication Models
نماذج المستخدمين والمصادقة
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Grade(models.Model):
    """الصفوف الدراسية"""
    name = models.CharField(_("اسم الصف"), max_length=50)
    level = models.CharField(_("المرحلة"), max_length=20, choices=[
        ('primary', 'ابتدائي'),
        ('middle', 'إعدادي'),
        ('secondary', 'ثانوي'),
    ])
    order = models.IntegerField(_("الترتيب"), default=0)
    
    class Meta:
        verbose_name = _("صف دراسي")
        verbose_name_plural = _("الصفوف الدراسية")
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Subject(models.Model):
    """المواد الدراسية"""
    name = models.CharField(_("اسم المادة"), max_length=100)
    code = models.CharField(_("رمز المادة"), max_length=20, unique=True)
    description = models.TextField(_("الوصف"), blank=True)
    icon = models.CharField(_("أيقونة"), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("مادة دراسية")
        verbose_name_plural = _("المواد الدراسية")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'مدير النظام'),
        ('MANAGER', 'مدير تنفيذي'),
        ('DESIGNER', 'مصمم'),
        ('CLIENT', 'عميل'),
    ]
    
    USER_TYPE_CHOICES = [
        ('teacher', 'مدرس'),
        ('shop', 'محل'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    # معلومات أساسية
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("البريد الإلكتروني"), unique=True)
    name = models.CharField(_("الاسم الكامل"), max_length=255)
    role = models.CharField(_("الدور"), max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    user_type = models.CharField(_("نوع المستخدم"), max_length=20, choices=USER_TYPE_CHOICES, blank=True)
    gender = models.CharField(_("الجنس"), max_length=10, choices=GENDER_CHOICES, blank=True)
    
    # معلومات التواصل
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="رقم الهاتف يجب أن يكون بالصيغة: '+999999999'. حتى 15 رقم مسموح."
    )
    phone = models.CharField(_("رقم الهاتف"), validators=[phone_regex], max_length=17, blank=True)
    whatsapp = models.CharField(_("واتساب"), validators=[phone_regex], max_length=17, blank=True)
    
    # روابط التواصل الاجتماعي
    facebook_url = models.URLField(_("رابط الفيسبوك"), blank=True)
    youtube_url = models.URLField(_("رابط اليوتيوب"), blank=True)
    instagram_url = models.URLField(_("رابط الإنستغرام"), blank=True)
    
    # معلومات تعليمية
    school_name = models.CharField(_("اسم المدرسة"), max_length=255, blank=True)
    region = models.CharField(_("المنطقة"), max_length=100, blank=True)
    subjects = models.ManyToManyField(Subject, verbose_name=_("المواد"), blank=True)
    grades = models.ManyToManyField(Grade, verbose_name=_("الصفوف"), blank=True)
    
    # الصورة الشخصية
    profile_image = models.ImageField(
        _("الصورة الشخصية"),
        upload_to='profiles/%Y/%m/',
        blank=True,
        null=True
    )
    
    # معلومات النظام
    is_verified = models.BooleanField(_("تم التحقق"), default=False)
    is_premium = models.BooleanField(_("عضوية مميزة"), default=False)
    balance = models.DecimalField(_("الرصيد"), max_digits=10, decimal_places=2, default=0)
    points = models.IntegerField(_("النقاط"), default=0)
    
    # التواريخ
    last_seen = models.DateTimeField(_("آخر ظهور"), null=True, blank=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    # إعدادات
    preferences = models.JSONField(_("التفضيلات"), default=dict, blank=True)
    notifications_enabled = models.BooleanField(_("تفعيل الإشعارات"), default=True)
    email_notifications = models.BooleanField(_("إشعارات البريد"), default=True)
    
    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمون")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.username})"
    
    @property
    def is_designer(self):
        return self.role == 'DESIGNER'
    
    @property
    def is_manager(self):
        return self.role in ['MANAGER', 'ADMIN']
    
    @property
    def is_client(self):
        return self.role == 'CLIENT'
    
    def update_last_seen(self):
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])


class DesignerProfile(models.Model):
    """ملف تعريف المصمم"""
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
        ('expert', 'خبير'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='designer_profile',
        verbose_name=_("المستخدم")
    )
    
    # معلومات المصمم
    bio = models.TextField(_("نبذة تعريفية"), blank=True)
    skills = models.JSONField(_("المهارات"), default=list, blank=True)
    skill_level = models.CharField(
        _("مستوى المهارة"),
        max_length=20,
        choices=SKILL_LEVEL_CHOICES,
        default='intermediate'
    )
    
    # الإحصائيات
    rating = models.DecimalField(_("التقييم"), max_digits=3, decimal_places=2, default=0)
    total_projects = models.IntegerField(_("إجمالي المشاريع"), default=0)
    completed_projects = models.IntegerField(_("المشاريع المكتملة"), default=0)
    ongoing_projects = models.IntegerField(_("المشاريع الجارية"), default=0)
    
    # معدلات الأداء
    completion_rate = models.DecimalField(
        _("معدل الإنجاز"),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="النسبة المئوية للمشاريع المكتملة في الوقت"
    )
    average_delivery_time = models.IntegerField(
        _("متوسط وقت التسليم"),
        default=0,
        help_text="بالساعات"
    )
    
    # التوفر
    is_available = models.BooleanField(_("متاح للعمل"), default=True)
    max_concurrent_projects = models.IntegerField(_("الحد الأقصى للمشاريع المتزامنة"), default=5)
    
    # معرض الأعمال
    portfolio_images = models.JSONField(_("صور المعرض"), default=list, blank=True)
    featured_works = models.JSONField(_("الأعمال المميزة"), default=list, blank=True)
    
    # الأسعار
    hourly_rate = models.DecimalField(
        _("السعر بالساعة"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # التخصصات
    specializations = models.JSONField(_("التخصصات"), default=list, blank=True)
    preferred_categories = models.JSONField(_("الفئات المفضلة"), default=list, blank=True)
    
    # التواريخ
    joined_as_designer = models.DateTimeField(_("تاريخ الانضمام كمصمم"), auto_now_add=True)
    last_project_date = models.DateTimeField(_("تاريخ آخر مشروع"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("ملف تعريف المصمم")
        verbose_name_plural = _("ملفات تعريف المصممين")
        ordering = ['-rating', '-completed_projects']
    
    def __str__(self):
        return f"مصمم: {self.user.name}"
    
    def calculate_rating(self):
        """حساب التقييم بناءً على التقييمات المستلمة"""
        from designs.models import Review
        reviews = Review.objects.filter(designer=self.user)
        if reviews.exists():
            self.rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.save(update_fields=['rating'])
    
    def update_statistics(self):
        """تحديث إحصائيات المصمم"""
        from designs.models import DesignRequest
        requests = DesignRequest.objects.filter(assigned_designer=self.user)
        
        self.total_projects = requests.count()
        self.completed_projects = requests.filter(status='DELIVERED').count()
        self.ongoing_projects = requests.filter(
            status__in=['IN_PROGRESS', 'REVIEWING', 'READY']
        ).count()
        
        if self.total_projects > 0:
            self.completion_rate = (self.completed_projects / self.total_projects) * 100
        
        self.save(update_fields=[
            'total_projects',
            'completed_projects',
            'ongoing_projects',
            'completion_rate'
        ])


class AuditLog(models.Model):
    """سجل التدقيق لتتبع جميع العمليات الحساسة"""
    
    ACTION_CHOICES = [
        ('CREATE', 'إنشاء'),
        ('UPDATE', 'تحديث'),
        ('DELETE', 'حذف'),
        ('LOGIN', 'تسجيل دخول'),
        ('LOGOUT', 'تسجيل خروج'),
        ('PERMISSION_CHANGE', 'تغيير الصلاحيات'),
        ('STATUS_CHANGE', 'تغيير الحالة'),
        ('PAYMENT', 'عملية دفع'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("المستخدم")
    )
    action = models.CharField(_("الإجراء"), max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(_("نوع النموذج"), max_length=100)
    object_id = models.CharField(_("معرف الكائن"), max_length=255, blank=True)
    data = models.JSONField(_("البيانات"), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_("عنوان IP"), null=True, blank=True)
    user_agent = models.TextField(_("وكيل المستخدم"), blank=True)
    timestamp = models.DateTimeField(_("الوقت"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("سجل تدقيق")
        verbose_name_plural = _("سجلات التدقيق")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.user} - {self.timestamp}"
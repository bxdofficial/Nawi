"""
Design Request and Order Models
نماذج طلبات التصميم والطلبات
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
import uuid


class DesignCategory(models.Model):
    """فئات التصميم"""
    name = models.CharField(_("اسم الفئة"), max_length=100)
    slug = models.SlugField(_("الرابط"), unique=True)
    description = models.TextField(_("الوصف"), blank=True)
    icon = models.CharField(_("الأيقونة"), max_length=50, blank=True)
    color = models.CharField(_("اللون"), max_length=7, default="#3B82F6")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("الفئة الأم")
    )
    is_active = models.BooleanField(_("نشط"), default=True)
    order = models.IntegerField(_("الترتيب"), default=0)
    
    class Meta:
        verbose_name = _("فئة التصميم")
        verbose_name_plural = _("فئات التصميم")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class DesignSize(models.Model):
    """أحجام التصميم المتاحة"""
    name = models.CharField(_("اسم الحجم"), max_length=100)
    width = models.IntegerField(_("العرض"), help_text="بالبكسل")
    height = models.IntegerField(_("الارتفاع"), help_text="بالبكسل")
    category = models.ForeignKey(
        DesignCategory,
        on_delete=models.CASCADE,
        related_name='sizes',
        verbose_name=_("الفئة")
    )
    platform = models.CharField(_("المنصة"), max_length=50, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('whatsapp', 'WhatsApp'),
        ('twitter', 'Twitter'),
        ('print', 'طباعة'),
        ('general', 'عام'),
    ], default='general')
    is_custom = models.BooleanField(_("مخصص"), default=False)
    price_multiplier = models.DecimalField(
        _("معامل السعر"),
        max_digits=4,
        decimal_places=2,
        default=1.0
    )
    
    class Meta:
        verbose_name = _("حجم التصميم")
        verbose_name_plural = _("أحجام التصميم")
        ordering = ['category', 'name']
        unique_together = [['category', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.width}x{self.height})"


class DesignRequest(models.Model):
    """طلبات التصميم"""
    
    STATUS_CHOICES = [
        ('RECEIVED', 'تم الاستلام'),
        ('REVIEWING', 'قيد المراجعة'),
        ('IN_PROGRESS', 'قيد التنفيذ'),
        ('READY', 'جاهز'),
        ('DELIVERED', 'تم التسليم'),
        ('ARCHIVED', 'مؤرشف'),
        ('CANCELLED', 'ملغي'),
    ]
    
    URGENCY_CHOICES = [
        ('normal', 'عادي (4 أيام)'),
        ('medium', 'متوسط (2 يوم)'),
        ('urgent', 'مستعجل (1 يوم)'),
    ]
    
    QUALITY_CHOICES = [
        ('standard', 'عادي'),
        ('professional', 'احترافي'),
        ('premium', 'مميز'),
    ]
    
    # معرف فريد
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_number = models.CharField(
        _("رقم الطلب"),
        max_length=20,
        unique=True,
        editable=False
    )
    
    # العلاقات الأساسية
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='design_requests',
        verbose_name=_("العميل")
    )
    assigned_designer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_designs',
        verbose_name=_("المصمم المعين")
    )
    
    # تفاصيل الطلب
    title = models.CharField(_("عنوان الطلب"), max_length=255)
    description = models.TextField(_("الوصف التفصيلي"))
    category = models.ForeignKey(
        DesignCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("فئة التصميم")
    )
    
    # المواصفات
    size = models.ForeignKey(
        DesignSize,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("الحجم")
    )
    custom_width = models.IntegerField(
        _("العرض المخصص"),
        null=True,
        blank=True,
        help_text="للأحجام المخصصة فقط"
    )
    custom_height = models.IntegerField(
        _("الارتفاع المخصص"),
        null=True,
        blank=True,
        help_text="للأحجام المخصصة فقط"
    )
    
    # المنصة المستهدفة
    target_platform = models.CharField(
        _("منصة النشر"),
        max_length=50,
        choices=[
            ('facebook', 'Facebook'),
            ('instagram', 'Instagram'),
            ('youtube', 'YouTube'),
            ('whatsapp', 'WhatsApp'),
            ('twitter', 'Twitter'),
            ('tiktok', 'TikTok'),
            ('print', 'طباعة'),
            ('multiple', 'متعدد'),
        ],
        default='facebook'
    )
    
    # مستوى الخدمة
    urgency = models.CharField(
        _("مستوى الاستعجال"),
        max_length=10,
        choices=URGENCY_CHOICES,
        default='normal'
    )
    quality_level = models.CharField(
        _("مستوى الجودة"),
        max_length=20,
        choices=QUALITY_CHOICES,
        default='standard'
    )
    
    # التسعير
    base_price = models.DecimalField(
        _("السعر الأساسي"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    urgency_fee = models.DecimalField(
        _("رسوم الاستعجال"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    quality_fee = models.DecimalField(
        _("رسوم الجودة"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_price = models.DecimalField(
        _("السعر الإجمالي"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # الحالة
    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='RECEIVED'
    )
    
    # الملاحظات والتعليقات
    client_notes = models.TextField(_("ملاحظات العميل"), blank=True)
    designer_notes = models.TextField(_("ملاحظات المصمم"), blank=True)
    manager_notes = models.TextField(_("ملاحظات المدير"), blank=True)
    
    # التقييم
    client_satisfied = models.BooleanField(_("رضا العميل"), null=True)
    revision_count = models.IntegerField(_("عدد التعديلات"), default=0)
    
    # المرفقات والنتائج
    reference_images = models.JSONField(
        _("صور مرجعية"),
        default=list,
        blank=True,
        help_text="روابط أو مسارات الصور المرجعية"
    )
    final_designs = models.JSONField(
        _("التصاميم النهائية"),
        default=list,
        blank=True,
        help_text="روابط أو مسارات التصاميم النهائية"
    )
    
    # التواريخ المهمة
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    due_date = models.DateTimeField(_("تاريخ الاستحقاق"), null=True, blank=True)
    started_at = models.DateTimeField(_("تاريخ البدء"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("تاريخ التسليم"), null=True, blank=True)
    
    # البيانات الإضافية
    metadata = models.JSONField(_("بيانات إضافية"), default=dict, blank=True)
    
    class Meta:
        verbose_name = _("طلب تصميم")
        verbose_name_plural = _("طلبات التصميم")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['assigned_designer', 'status']),
            models.Index(fields=['request_number']),
        ]
    
    def __str__(self):
        return f"#{self.request_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Generate request number if not exists
        if not self.request_number:
            from django.utils import timezone
            year = timezone.now().year
            month = timezone.now().month
            
            # Get the last request number for this month
            last_request = DesignRequest.objects.filter(
                request_number__startswith=f"DR{year}{month:02d}"
            ).order_by('request_number').last()
            
            if last_request:
                last_number = int(last_request.request_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.request_number = f"DR{year}{month:02d}{new_number:04d}"
        
        # Calculate total price
        self.calculate_total_price()
        
        # Set due date based on urgency if not set
        if not self.due_date and self.urgency:
            days_map = {'normal': 4, 'medium': 2, 'urgent': 1}
            from datetime import timedelta
            self.due_date = timezone.now() + timedelta(days=days_map.get(self.urgency, 4))
        
        super().save(*args, **kwargs)
    
    def calculate_total_price(self):
        """حساب السعر الإجمالي"""
        self.total_price = self.base_price + self.urgency_fee + self.quality_fee
        return self.total_price
    
    def assign_designer(self, designer):
        """تعيين مصمم للطلب"""
        self.assigned_designer = designer
        self.status = 'IN_PROGRESS'
        self.started_at = timezone.now()
        self.save(update_fields=['assigned_designer', 'status', 'started_at'])
    
    def mark_as_delivered(self):
        """تحديد الطلب كمسلّم"""
        self.status = 'DELIVERED'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])
    
    @property
    def is_overdue(self):
        """التحقق من تأخر الطلب"""
        if self.due_date and self.status not in ['DELIVERED', 'CANCELLED', 'ARCHIVED']:
            return timezone.now() > self.due_date
        return False
    
    @property
    def time_remaining(self):
        """الوقت المتبقي للتسليم"""
        if self.due_date and self.status not in ['DELIVERED', 'CANCELLED', 'ARCHIVED']:
            delta = self.due_date - timezone.now()
            return delta if delta.total_seconds() > 0 else None
        return None


class Attachment(models.Model):
    """المرفقات"""
    
    ATTACHMENT_TYPE_CHOICES = [
        ('reference', 'صورة مرجعية'),
        ('draft', 'مسودة'),
        ('final', 'نهائي'),
        ('revision', 'تعديل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        DesignRequest,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_("الطلب")
    )
    type = models.CharField(
        _("نوع المرفق"),
        max_length=20,
        choices=ATTACHMENT_TYPE_CHOICES,
        default='reference'
    )
    file = models.FileField(
        _("الملف"),
        upload_to='attachments/%Y/%m/%d/'
    )
    original_name = models.CharField(_("اسم الملف الأصلي"), max_length=255)
    file_size = models.IntegerField(_("حجم الملف"), help_text="بالبايت")
    mime_type = models.CharField(_("نوع الملف"), max_length=100)
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("رفع بواسطة")
    )
    uploaded_at = models.DateTimeField(_("تاريخ الرفع"), auto_now_add=True)
    
    description = models.TextField(_("الوصف"), blank=True)
    is_public = models.BooleanField(_("عام"), default=False)
    
    class Meta:
        verbose_name = _("مرفق")
        verbose_name_plural = _("المرفقات")
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.original_name} - {self.get_type_display()}"


class Review(models.Model):
    """التقييمات والمراجعات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(
        DesignRequest,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name=_("الطلب")
    )
    designer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        verbose_name=_("المصمم")
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_reviews',
        verbose_name=_("العميل")
    )
    
    rating = models.IntegerField(
        _("التقييم"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_("التعليق"), blank=True)
    
    # تفاصيل التقييم
    quality_rating = models.IntegerField(
        _("جودة التصميم"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True
    )
    speed_rating = models.IntegerField(
        _("سرعة التنفيذ"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True
    )
    communication_rating = models.IntegerField(
        _("التواصل"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True
    )
    
    is_featured = models.BooleanField(_("مميز"), default=False)
    created_at = models.DateTimeField(_("تاريخ التقييم"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("تقييم")
        verbose_name_plural = _("التقييمات")
        ordering = ['-created_at']
        unique_together = [['request', 'client']]
    
    def __str__(self):
        return f"تقييم {self.client.name} للطلب #{self.request.request_number}"


class PriceSetting(models.Model):
    """إعدادات الأسعار"""
    category = models.ForeignKey(
        DesignCategory,
        on_delete=models.CASCADE,
        related_name='price_settings',
        verbose_name=_("الفئة")
    )
    
    # الأسعار الأساسية
    base_price = models.DecimalField(
        _("السعر الأساسي"),
        max_digits=10,
        decimal_places=2
    )
    
    # معاملات الضرب
    quality_multiplier_standard = models.DecimalField(
        _("معامل الجودة العادية"),
        max_digits=4,
        decimal_places=2,
        default=1.0
    )
    quality_multiplier_professional = models.DecimalField(
        _("معامل الجودة الاحترافية"),
        max_digits=4,
        decimal_places=2,
        default=1.5
    )
    quality_multiplier_premium = models.DecimalField(
        _("معامل الجودة المميزة"),
        max_digits=4,
        decimal_places=2,
        default=2.0
    )
    
    urgency_multiplier_normal = models.DecimalField(
        _("معامل السرعة العادية"),
        max_digits=4,
        decimal_places=2,
        default=1.0
    )
    urgency_multiplier_medium = models.DecimalField(
        _("معامل السرعة المتوسطة"),
        max_digits=4,
        decimal_places=2,
        default=1.5
    )
    urgency_multiplier_urgent = models.DecimalField(
        _("معامل السرعة العاجلة"),
        max_digits=4,
        decimal_places=2,
        default=2.0
    )
    
    # خصومات
    bulk_discount_threshold = models.IntegerField(
        _("حد الخصم الجماعي"),
        default=5,
        help_text="عدد الطلبات للحصول على الخصم"
    )
    bulk_discount_percentage = models.DecimalField(
        _("نسبة الخصم الجماعي"),
        max_digits=5,
        decimal_places=2,
        default=10
    )
    
    is_active = models.BooleanField(_("نشط"), default=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("إعداد السعر")
        verbose_name_plural = _("إعدادات الأسعار")
        unique_together = [['category']]
    
    def __str__(self):
        return f"أسعار {self.category.name}"
    
    def calculate_price(self, quality='standard', urgency='normal'):
        """حساب السعر بناءً على الجودة والسرعة"""
        price = self.base_price
        
        # Apply quality multiplier
        quality_map = {
            'standard': self.quality_multiplier_standard,
            'professional': self.quality_multiplier_professional,
            'premium': self.quality_multiplier_premium,
        }
        price *= quality_map.get(quality, 1.0)
        
        # Apply urgency multiplier
        urgency_map = {
            'normal': self.urgency_multiplier_normal,
            'medium': self.urgency_multiplier_medium,
            'urgent': self.urgency_multiplier_urgent,
        }
        price *= urgency_map.get(urgency, 1.0)
        
        return price
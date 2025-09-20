"""
Chat and Notifications Models
نماذج الدردشة والإشعارات
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import uuid


class Conversation(models.Model):
    """المحادثات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # المشاركون
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        verbose_name=_("المشاركون")
    )
    
    # معلومات المحادثة
    title = models.CharField(_("العنوان"), max_length=255, blank=True)
    is_group = models.BooleanField(_("محادثة جماعية"), default=False)
    
    # الطلب المرتبط (إن وجد)
    design_request = models.ForeignKey(
        'designs.DesignRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
        verbose_name=_("طلب التصميم")
    )
    
    # الحالة
    is_active = models.BooleanField(_("نشط"), default=True)
    is_archived = models.BooleanField(_("مؤرشف"), default=False)
    
    # التواريخ
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("آخر تحديث"), auto_now=True)
    last_message_at = models.DateTimeField(_("آخر رسالة"), null=True, blank=True)
    
    # البيانات الإضافية
    metadata = models.JSONField(_("بيانات إضافية"), default=dict, blank=True)
    
    class Meta:
        verbose_name = _("محادثة")
        verbose_name_plural = _("المحادثات")
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['-last_message_at']),
            models.Index(fields=['design_request', 'is_active']),
        ]
    
    def __str__(self):
        if self.title:
            return self.title
        elif self.design_request:
            return f"محادثة الطلب #{self.design_request.request_number}"
        else:
            participants_names = ", ".join([p.name for p in self.participants.all()[:3]])
            return f"محادثة: {participants_names}"
    
    def get_other_participant(self, user):
        """الحصول على المشارك الآخر في محادثة ثنائية"""
        if not self.is_group:
            return self.participants.exclude(id=user.id).first()
        return None
    
    def mark_as_read(self, user):
        """تحديد جميع الرسائل كمقروءة للمستخدم"""
        self.messages.filter(is_read=False).exclude(sender=user).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    def add_participant(self, user):
        """إضافة مشارك للمحادثة"""
        self.participants.add(user)
        if self.participants.count() > 2:
            self.is_group = True
            self.save(update_fields=['is_group'])


class Message(models.Model):
    """الرسائل"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'نص'),
        ('image', 'صورة'),
        ('file', 'ملف'),
        ('audio', 'صوت'),
        ('system', 'نظام'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_("المحادثة")
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_messages',
        verbose_name=_("المرسل")
    )
    
    # محتوى الرسالة
    message_type = models.CharField(
        _("نوع الرسالة"),
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text'
    )
    content = models.TextField(_("المحتوى"))
    
    # المرفقات
    attachment = models.FileField(
        _("المرفق"),
        upload_to='chat/attachments/%Y/%m/%d/',
        null=True,
        blank=True
    )
    attachment_name = models.CharField(_("اسم المرفق"), max_length=255, blank=True)
    attachment_size = models.IntegerField(_("حجم المرفق"), null=True, blank=True)
    
    # الحالة
    is_read = models.BooleanField(_("مقروءة"), default=False)
    read_at = models.DateTimeField(_("وقت القراءة"), null=True, blank=True)
    is_edited = models.BooleanField(_("معدلة"), default=False)
    edited_at = models.DateTimeField(_("وقت التعديل"), null=True, blank=True)
    is_deleted = models.BooleanField(_("محذوفة"), default=False)
    deleted_at = models.DateTimeField(_("وقت الحذف"), null=True, blank=True)
    
    # التواريخ
    sent_at = models.DateTimeField(_("وقت الإرسال"), auto_now_add=True)
    
    # الرد على رسالة
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_("رد على")
    )
    
    # البيانات الإضافية
    metadata = models.JSONField(_("بيانات إضافية"), default=dict, blank=True)
    
    class Meta:
        verbose_name = _("رسالة")
        verbose_name_plural = _("الرسائل")
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender', 'sent_at']),
            models.Index(fields=['is_read', 'sent_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.name if self.sender else 'System'}: {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        # Update conversation's last message time
        if not self.pk:  # New message
            self.conversation.last_message_at = timezone.now()
            self.conversation.save(update_fields=['last_message_at'])
        
        super().save(*args, **kwargs)
    
    def mark_as_read(self):
        """تحديد الرسالة كمقروءة"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def edit(self, new_content):
        """تعديل الرسالة"""
        self.content = new_content
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['content', 'is_edited', 'edited_at'])
    
    def soft_delete(self):
        """حذف ناعم للرسالة"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])


class Notification(models.Model):
    """الإشعارات"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('design_request', 'طلب تصميم'),
        ('design_ready', 'تصميم جاهز'),
        ('design_delivered', 'تصميم مسلم'),
        ('message', 'رسالة جديدة'),
        ('payment', 'دفعة'),
        ('game_prize', 'جائزة لعبة'),
        ('system', 'إشعار نظام'),
        ('promotion', 'عرض ترويجي'),
        ('reminder', 'تذكير'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'منخفض'),
        ('normal', 'عادي'),
        ('high', 'مرتفع'),
        ('urgent', 'عاجل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("المستخدم")
    )
    
    # محتوى الإشعار
    type = models.CharField(
        _("نوع الإشعار"),
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(_("العنوان"), max_length=255)
    message = models.TextField(_("الرسالة"))
    
    # الأولوية والحالة
    priority = models.CharField(
        _("الأولوية"),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    is_read = models.BooleanField(_("مقروء"), default=False)
    read_at = models.DateTimeField(_("وقت القراءة"), null=True, blank=True)
    
    # الروابط
    action_url = models.CharField(_("رابط الإجراء"), max_length=500, blank=True)
    action_text = models.CharField(_("نص الإجراء"), max_length=100, blank=True)
    
    # البيانات المرتبطة
    related_object_type = models.CharField(_("نوع الكائن المرتبط"), max_length=50, blank=True)
    related_object_id = models.CharField(_("معرف الكائن المرتبط"), max_length=255, blank=True)
    
    # الإعدادات
    is_email_sent = models.BooleanField(_("تم إرسال بريد"), default=False)
    is_push_sent = models.BooleanField(_("تم إرسال إشعار فوري"), default=False)
    
    # البيانات الإضافية
    payload = models.JSONField(_("البيانات"), default=dict, blank=True)
    
    # التواريخ
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    expires_at = models.DateTimeField(_("تاريخ الانتهاء"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("إشعار")
        verbose_name_plural = _("الإشعارات")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['type', '-created_at']),
            models.Index(fields=['priority', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.name}"
    
    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def create_notification(cls, user, type, title, message, **kwargs):
        """إنشاء إشعار جديد"""
        notification = cls.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            **kwargs
        )
        
        # Send via WebSocket if available
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    'type': 'notification',
                    'notification': {
                        'id': str(notification.id),
                        'type': notification.type,
                        'title': notification.title,
                        'message': notification.message,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
        
        # Send email if enabled
        if user.email_notifications and not notification.is_email_sent:
            # Queue email task
            from chat.tasks import send_notification_email
            send_notification_email.delay(notification.id)
        
        return notification
    
    @classmethod
    def notify_design_status(cls, design_request, status):
        """إشعار بتغيير حالة الطلب"""
        status_messages = {
            'REVIEWING': 'طلبك قيد المراجعة',
            'IN_PROGRESS': 'بدأ العمل على طلبك',
            'READY': 'تصميمك جاهز للمراجعة',
            'DELIVERED': 'تم تسليم تصميمك',
        }
        
        if status in status_messages:
            cls.create_notification(
                user=design_request.client,
                type='design_request',
                title=f'تحديث الطلب #{design_request.request_number}',
                message=status_messages[status],
                related_object_type='DesignRequest',
                related_object_id=str(design_request.id),
                action_url=f'/requests/{design_request.id}/',
                action_text='عرض الطلب',
                priority='high' if status == 'DELIVERED' else 'normal'
            )


class OnlineStatus(models.Model):
    """حالة الاتصال للمستخدمين"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='online_status',
        verbose_name=_("المستخدم")
    )
    
    is_online = models.BooleanField(_("متصل"), default=False)
    last_seen = models.DateTimeField(_("آخر ظهور"), auto_now=True)
    
    # WebSocket connection info
    channel_name = models.CharField(_("اسم القناة"), max_length=255, blank=True)
    connection_count = models.IntegerField(_("عدد الاتصالات"), default=0)
    
    # النشاط
    is_typing = models.BooleanField(_("يكتب"), default=False)
    typing_in_conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("يكتب في محادثة")
    )
    
    class Meta:
        verbose_name = _("حالة الاتصال")
        verbose_name_plural = _("حالات الاتصال")
        ordering = ['-last_seen']
    
    def __str__(self):
        status = "متصل" if self.is_online else "غير متصل"
        return f"{self.user.name} - {status}"
    
    def set_online(self, channel_name=None):
        """تعيين المستخدم كمتصل"""
        self.is_online = True
        self.connection_count += 1
        if channel_name:
            self.channel_name = channel_name
        self.save(update_fields=['is_online', 'connection_count', 'channel_name', 'last_seen'])
    
    def set_offline(self):
        """تعيين المستخدم كغير متصل"""
        self.connection_count = max(0, self.connection_count - 1)
        if self.connection_count == 0:
            self.is_online = False
            self.channel_name = ''
        self.save(update_fields=['is_online', 'connection_count', 'channel_name', 'last_seen'])
    
    def set_typing(self, conversation=None, is_typing=True):
        """تعيين حالة الكتابة"""
        self.is_typing = is_typing
        self.typing_in_conversation = conversation if is_typing else None
        self.save(update_fields=['is_typing', 'typing_in_conversation'])
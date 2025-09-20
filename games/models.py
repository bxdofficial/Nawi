"""
Games Models
نماذج الألعاب التفاعلية
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import uuid
import random
import json


class WheelOfFortune(models.Model):
    """عجلة الحظ"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("العنوان"), max_length=255, default="عجلة الحظ اليومية")
    description = models.TextField(_("الوصف"), blank=True)
    
    # إعدادات العجلة
    segments = models.JSONField(
        _("قطاعات العجلة"),
        default=list,
        help_text="قائمة بالقطاعات وجوائزها"
    )
    """
    Example segments:
    [
        {"id": 1, "text": "خصم 10%", "color": "#FF6B6B", "weight": 30, "prize_type": "discount", "prize_value": 10},
        {"id": 2, "text": "تصميم مجاني", "color": "#4ECDC4", "weight": 5, "prize_type": "free_design", "prize_value": 1},
        {"id": 3, "text": "50 نقطة", "color": "#45B7D1", "weight": 20, "prize_type": "points", "prize_value": 50},
        {"id": 4, "text": "حظ أوفر", "color": "#96CEB4", "weight": 45, "prize_type": "nothing", "prize_value": 0}
    ]
    """
    
    # التحكم بالعجلة
    is_active = models.BooleanField(_("نشط"), default=True)
    start_date = models.DateTimeField(_("تاريخ البداية"), null=True, blank=True)
    end_date = models.DateTimeField(_("تاريخ النهاية"), null=True, blank=True)
    max_spins_per_day = models.IntegerField(_("الحد الأقصى للدورات يومياً"), default=1)
    requires_purchase = models.BooleanField(_("يتطلب شراء"), default=False)
    minimum_purchase = models.DecimalField(
        _("الحد الأدنى للشراء"),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # الإحصائيات
    total_spins = models.IntegerField(_("إجمالي الدورات"), default=0)
    total_prizes_given = models.IntegerField(_("إجمالي الجوائز الممنوحة"), default=0)
    
    # التصميم
    wheel_style = models.JSONField(
        _("تصميم العجلة"),
        default=dict,
        blank=True,
        help_text="CSS وإعدادات التصميم"
    )
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("عجلة الحظ")
        verbose_name_plural = _("عجلات الحظ")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def spin(self):
        """تدوير العجلة واختيار جائزة"""
        if not self.segments:
            return None
        
        # Calculate weighted random selection
        weights = [segment.get('weight', 1) for segment in self.segments]
        selected = random.choices(self.segments, weights=weights, k=1)[0]
        
        # Update statistics
        self.total_spins += 1
        if selected.get('prize_type') != 'nothing':
            self.total_prizes_given += 1
        self.save(update_fields=['total_spins', 'total_prizes_given'])
        
        return selected


class WheelSpin(models.Model):
    """سجل دورات عجلة الحظ"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wheel = models.ForeignKey(
        WheelOfFortune,
        on_delete=models.CASCADE,
        related_name='spins',
        verbose_name=_("العجلة")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wheel_spins',
        verbose_name=_("المستخدم")
    )
    
    # النتيجة
    result = models.JSONField(_("النتيجة"), default=dict)
    prize_type = models.CharField(_("نوع الجائزة"), max_length=50, blank=True)
    prize_value = models.CharField(_("قيمة الجائزة"), max_length=100, blank=True)
    prize_claimed = models.BooleanField(_("تم استلام الجائزة"), default=False)
    claimed_at = models.DateTimeField(_("تاريخ الاستلام"), null=True, blank=True)
    
    # معلومات الدورة
    spin_date = models.DateTimeField(_("تاريخ الدورة"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("عنوان IP"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("دورة عجلة")
        verbose_name_plural = _("دورات العجلة")
        ordering = ['-spin_date']
        indexes = [
            models.Index(fields=['user', 'spin_date']),
            models.Index(fields=['wheel', 'spin_date']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.wheel.title} - {self.spin_date}"
    
    def claim_prize(self):
        """استلام الجائزة"""
        if not self.prize_claimed and self.prize_type != 'nothing':
            self.prize_claimed = True
            self.claimed_at = timezone.now()
            self.save(update_fields=['prize_claimed', 'claimed_at'])
            
            # Apply prize to user account
            user = self.user
            if self.prize_type == 'points':
                user.points += int(self.prize_value)
                user.save(update_fields=['points'])
            elif self.prize_type == 'discount':
                # Create discount code or apply to account
                pass
            elif self.prize_type == 'free_design':
                # Add free design credit
                pass
            
            return True
        return False


class PuzzleGame(models.Model):
    """لعبة البازل"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("عنوان اللعبة"), max_length=255)
    description = models.TextField(_("الوصف"), blank=True)
    
    # الصورة
    original_image = models.ImageField(
        _("الصورة الأصلية"),
        upload_to='puzzles/originals/%Y/%m/'
    )
    thumbnail = models.ImageField(
        _("الصورة المصغرة"),
        upload_to='puzzles/thumbnails/%Y/%m/',
        null=True,
        blank=True
    )
    
    # إعدادات اللعبة
    difficulty = models.CharField(
        _("مستوى الصعوبة"),
        max_length=20,
        choices=[
            ('easy', 'سهل (3×3)'),
            ('medium', 'متوسط (4×4)'),
            ('hard', 'صعب (5×5)'),
            ('expert', 'خبير (6×6)'),
        ],
        default='medium'
    )
    grid_size = models.IntegerField(_("حجم الشبكة"), default=4)
    time_limit = models.IntegerField(
        _("الحد الزمني"),
        default=300,
        help_text="بالثواني (0 = بدون حد زمني)"
    )
    
    # الجوائز
    points_reward = models.IntegerField(_("نقاط المكافأة"), default=10)
    bonus_time_threshold = models.IntegerField(
        _("حد الوقت للمكافأة الإضافية"),
        default=60,
        help_text="إكمال في أقل من هذا الوقت للحصول على مكافأة"
    )
    bonus_points = models.IntegerField(_("نقاط المكافأة الإضافية"), default=5)
    
    # الحالة
    is_active = models.BooleanField(_("نشط"), default=True)
    is_daily = models.BooleanField(_("لعبة اليوم"), default=False)
    active_date = models.DateField(_("تاريخ التفعيل"), null=True, blank=True)
    
    # الإحصائيات
    total_plays = models.IntegerField(_("إجمالي مرات اللعب"), default=0)
    total_completions = models.IntegerField(_("إجمالي الإكمالات"), default=0)
    average_time = models.FloatField(_("متوسط الوقت"), default=0)
    best_time = models.FloatField(_("أفضل وقت"), null=True, blank=True)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("أنشئ بواسطة")
    )
    
    class Meta:
        verbose_name = _("لعبة بازل")
        verbose_name_plural = _("ألعاب البازل")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_grid_size(self):
        """الحصول على حجم الشبكة بناءً على الصعوبة"""
        difficulty_map = {
            'easy': 3,
            'medium': 4,
            'hard': 5,
            'expert': 6,
        }
        return difficulty_map.get(self.difficulty, 4)
    
    def update_statistics(self, completion_time=None):
        """تحديث إحصائيات اللعبة"""
        self.total_plays += 1
        
        if completion_time is not None:
            self.total_completions += 1
            
            # Update average time
            if self.average_time == 0:
                self.average_time = completion_time
            else:
                self.average_time = (
                    (self.average_time * (self.total_completions - 1) + completion_time)
                    / self.total_completions
                )
            
            # Update best time
            if self.best_time is None or completion_time < self.best_time:
                self.best_time = completion_time
        
        self.save(update_fields=[
            'total_plays',
            'total_completions',
            'average_time',
            'best_time'
        ])


class PuzzleAttempt(models.Model):
    """محاولات حل البازل"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    puzzle = models.ForeignKey(
        PuzzleGame,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_("اللعبة")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='puzzle_attempts',
        verbose_name=_("المستخدم")
    )
    
    # التقدم
    started_at = models.DateTimeField(_("وقت البداية"), auto_now_add=True)
    completed_at = models.DateTimeField(_("وقت الإكمال"), null=True, blank=True)
    completion_time = models.FloatField(_("وقت الإكمال"), null=True, blank=True, help_text="بالثواني")
    moves_count = models.IntegerField(_("عدد الحركات"), default=0)
    
    # النتيجة
    is_completed = models.BooleanField(_("مكتمل"), default=False)
    points_earned = models.IntegerField(_("النقاط المكتسبة"), default=0)
    bonus_earned = models.BooleanField(_("حصل على مكافأة"), default=False)
    
    # البيانات
    game_state = models.JSONField(
        _("حالة اللعبة"),
        default=dict,
        blank=True,
        help_text="حفظ حالة اللعبة للاستكمال لاحقاً"
    )
    
    class Meta:
        verbose_name = _("محاولة بازل")
        verbose_name_plural = _("محاولات البازل")
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['puzzle', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.puzzle.title} - {self.started_at}"
    
    def complete(self):
        """إكمال المحاولة"""
        if not self.is_completed:
            self.completed_at = timezone.now()
            self.completion_time = (self.completed_at - self.started_at).total_seconds()
            self.is_completed = True
            
            # Calculate points
            self.points_earned = self.puzzle.points_reward
            
            # Check for bonus
            if (self.puzzle.bonus_time_threshold > 0 and 
                self.completion_time <= self.puzzle.bonus_time_threshold):
                self.points_earned += self.puzzle.bonus_points
                self.bonus_earned = True
            
            # Update user points
            self.user.points += self.points_earned
            self.user.save(update_fields=['points'])
            
            # Update puzzle statistics
            self.puzzle.update_statistics(self.completion_time)
            
            self.save(update_fields=[
                'completed_at',
                'completion_time',
                'is_completed',
                'points_earned',
                'bonus_earned'
            ])
            
            return True
        return False


class Leaderboard(models.Model):
    """لوحة المتصدرين"""
    
    GAME_TYPE_CHOICES = [
        ('wheel', 'عجلة الحظ'),
        ('puzzle', 'البازل'),
        ('overall', 'الإجمالي'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
        ('yearly', 'سنوي'),
        ('alltime', 'دائم'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries',
        verbose_name=_("المستخدم")
    )
    
    game_type = models.CharField(
        _("نوع اللعبة"),
        max_length=20,
        choices=GAME_TYPE_CHOICES
    )
    period = models.CharField(
        _("الفترة"),
        max_length=20,
        choices=PERIOD_CHOICES
    )
    
    # النقاط والترتيب
    score = models.IntegerField(_("النقاط"), default=0)
    rank = models.IntegerField(_("الترتيب"), default=0)
    games_played = models.IntegerField(_("عدد الألعاب"), default=0)
    best_time = models.FloatField(_("أفضل وقت"), null=True, blank=True)
    
    # الفترة الزمنية
    period_start = models.DateTimeField(_("بداية الفترة"))
    period_end = models.DateTimeField(_("نهاية الفترة"))
    
    # التحديث
    last_updated = models.DateTimeField(_("آخر تحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("لوحة متصدرين")
        verbose_name_plural = _("لوحات المتصدرين")
        ordering = ['game_type', 'period', 'rank']
        unique_together = [['user', 'game_type', 'period', 'period_start']]
        indexes = [
            models.Index(fields=['game_type', 'period', 'rank']),
            models.Index(fields=['user', 'game_type', 'period']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.get_game_type_display()} - الترتيب {self.rank}"
    
    @classmethod
    def update_leaderboard(cls, game_type='overall', period='daily'):
        """تحديث لوحة المتصدرين"""
        from django.db.models import Sum, Count, Min
        from datetime import timedelta
        
        now = timezone.now()
        
        # Determine period boundaries
        if period == 'daily':
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif period == 'weekly':
            period_start = now - timedelta(days=now.weekday())
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=7)
        elif period == 'monthly':
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
        elif period == 'yearly':
            period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start.replace(year=now.year + 1)
        else:  # alltime
            period_start = timezone.datetime(2000, 1, 1, tzinfo=timezone.utc)
            period_end = now + timedelta(days=365 * 100)
        
        # Get user scores based on game type
        if game_type == 'puzzle':
            user_scores = PuzzleAttempt.objects.filter(
                started_at__gte=period_start,
                started_at__lt=period_end,
                is_completed=True
            ).values('user').annotate(
                total_score=Sum('points_earned'),
                games_count=Count('id'),
                min_time=Min('completion_time')
            )
        elif game_type == 'wheel':
            user_scores = WheelSpin.objects.filter(
                spin_date__gte=period_start,
                spin_date__lt=period_end
            ).values('user').annotate(
                total_score=Count('id') * 10,  # 10 points per spin for example
                games_count=Count('id')
            )
        else:  # overall
            # Combine all game scores
            puzzle_scores = PuzzleAttempt.objects.filter(
                started_at__gte=period_start,
                started_at__lt=period_end,
                is_completed=True
            ).values('user').annotate(
                score=Sum('points_earned')
            )
            
            # Calculate combined scores
            user_scores = []
            # This would need more complex logic to combine different game types
        
        # Update leaderboard entries
        for idx, user_data in enumerate(user_scores, 1):
            cls.objects.update_or_create(
                user_id=user_data['user'],
                game_type=game_type,
                period=period,
                period_start=period_start,
                defaults={
                    'score': user_data.get('total_score', 0),
                    'rank': idx,
                    'games_played': user_data.get('games_count', 0),
                    'best_time': user_data.get('min_time'),
                    'period_end': period_end,
                }
            )
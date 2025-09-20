"""
Management command to seed initial data
إنشاء البيانات الأولية للتطبيق
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from accounts.models import Grade, Subject, DesignerProfile
from designs.models import DesignCategory, DesignSize, PriceSetting
from games.models import WheelOfFortune, PuzzleGame
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial data including admin user and sample data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Starting data seeding...")
        
        # Create admin user
        self.create_admin_user()
        
        # Create grades and subjects
        self.create_grades()
        self.create_subjects()
        
        # Create design categories and sizes
        self.create_design_categories()
        
        # Create sample users
        self.create_sample_users()
        
        # Create games
        self.create_games()
        
        self.stdout.write(self.style.SUCCESS("✅ Data seeding completed successfully!"))
    
    def create_admin_user(self):
        """Create admin user with credentials admin/admin123"""
        admin_username = settings.ADMIN_USERNAME
        admin_email = settings.ADMIN_EMAIL
        admin_password = settings.ADMIN_PASSWORD
        
        if not User.objects.filter(username=admin_username).exists():
            admin = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                name="مدير النظام",
                role="ADMIN"
            )
            self.stdout.write(f"✅ Admin user created: {admin_username}/{admin_password}")
        else:
            self.stdout.write("⚠️ Admin user already exists")
    
    def create_grades(self):
        """Create educational grades"""
        grades = [
            # Primary
            {"name": "الأول الابتدائي", "level": "primary", "order": 1},
            {"name": "الثاني الابتدائي", "level": "primary", "order": 2},
            {"name": "الثالث الابتدائي", "level": "primary", "order": 3},
            {"name": "الرابع الابتدائي", "level": "primary", "order": 4},
            {"name": "الخامس الابتدائي", "level": "primary", "order": 5},
            {"name": "السادس الابتدائي", "level": "primary", "order": 6},
            # Middle
            {"name": "الأول الإعدادي", "level": "middle", "order": 7},
            {"name": "الثاني الإعدادي", "level": "middle", "order": 8},
            {"name": "الثالث الإعدادي", "level": "middle", "order": 9},
            # Secondary
            {"name": "الأول الثانوي", "level": "secondary", "order": 10},
            {"name": "الثاني الثانوي", "level": "secondary", "order": 11},
            {"name": "الثالث الثانوي", "level": "secondary", "order": 12},
        ]
        
        for grade_data in grades:
            Grade.objects.get_or_create(**grade_data)
        
        self.stdout.write(f"✅ Created {len(grades)} grades")
    
    def create_subjects(self):
        """Create educational subjects"""
        subjects = [
            {"name": "اللغة العربية", "code": "AR", "icon": "📚"},
            {"name": "الرياضيات", "code": "MATH", "icon": "🔢"},
            {"name": "العلوم", "code": "SCI", "icon": "🔬"},
            {"name": "اللغة الإنجليزية", "code": "EN", "icon": "🌐"},
            {"name": "التاريخ", "code": "HIST", "icon": "📜"},
            {"name": "الجغرافيا", "code": "GEO", "icon": "🌍"},
            {"name": "التربية الإسلامية", "code": "ISL", "icon": "🕌"},
            {"name": "الفيزياء", "code": "PHY", "icon": "⚛️"},
            {"name": "الكيمياء", "code": "CHEM", "icon": "🧪"},
            {"name": "الأحياء", "code": "BIO", "icon": "🧬"},
            {"name": "الحاسوب", "code": "CS", "icon": "💻"},
        ]
        
        for subject_data in subjects:
            Subject.objects.get_or_create(**subject_data)
        
        self.stdout.write(f"✅ Created {len(subjects)} subjects")
    
    def create_design_categories(self):
        """Create design categories with sizes and pricing"""
        categories_data = [
            {
                "name": "منشورات وسائل التواصل",
                "slug": "social-media",
                "description": "تصاميم مخصصة لمنصات التواصل الاجتماعي",
                "icon": "📱",
                "color": "#1DA1F2",
                "sizes": [
                    {"name": "Facebook Post", "width": 1200, "height": 630, "platform": "facebook"},
                    {"name": "Instagram Post", "width": 1080, "height": 1080, "platform": "instagram"},
                    {"name": "Instagram Story", "width": 1080, "height": 1920, "platform": "instagram"},
                    {"name": "YouTube Thumbnail", "width": 1280, "height": 720, "platform": "youtube"},
                    {"name": "WhatsApp Status", "width": 1080, "height": 1920, "platform": "whatsapp"},
                ],
                "base_price": 50000
            },
            {
                "name": "بطاقات تعليمية",
                "slug": "educational-cards",
                "description": "بطاقات ومواد تعليمية",
                "icon": "🎓",
                "color": "#4CAF50",
                "sizes": [
                    {"name": "A4", "width": 2480, "height": 3508, "platform": "print"},
                    {"name": "A3", "width": 3508, "height": 4960, "platform": "print"},
                    {"name": "Letter", "width": 2550, "height": 3300, "platform": "print"},
                ],
                "base_price": 75000
            },
            {
                "name": "إعلانات وبوسترات",
                "slug": "posters",
                "description": "تصاميم إعلانية وبوسترات",
                "icon": "🎯",
                "color": "#FF5722",
                "sizes": [
                    {"name": "Poster A2", "width": 4960, "height": 7016, "platform": "print"},
                    {"name": "Banner", "width": 2000, "height": 800, "platform": "general"},
                    {"name": "Flyer", "width": 2480, "height": 3508, "platform": "print"},
                ],
                "base_price": 100000
            },
            {
                "name": "شعارات وهوية بصرية",
                "slug": "logos",
                "description": "تصميم الشعارات والهوية البصرية",
                "icon": "✨",
                "color": "#9C27B0",
                "sizes": [
                    {"name": "Logo Square", "width": 1000, "height": 1000, "platform": "general"},
                    {"name": "Logo Wide", "width": 2000, "height": 1000, "platform": "general"},
                ],
                "base_price": 150000
            },
            {
                "name": "عروض تقديمية",
                "slug": "presentations",
                "description": "قوالب وشرائح العروض التقديمية",
                "icon": "📊",
                "color": "#FF9800",
                "sizes": [
                    {"name": "16:9", "width": 1920, "height": 1080, "platform": "general"},
                    {"name": "4:3", "width": 1024, "height": 768, "platform": "general"},
                ],
                "base_price": 80000
            }
        ]
        
        for cat_data in categories_data:
            sizes = cat_data.pop("sizes", [])
            base_price = cat_data.pop("base_price", 50000)
            
            category, created = DesignCategory.objects.get_or_create(
                slug=cat_data["slug"],
                defaults=cat_data
            )
            
            # Create sizes for category
            for size_data in sizes:
                size_data["category"] = category
                DesignSize.objects.get_or_create(
                    name=size_data["name"],
                    category=category,
                    defaults=size_data
                )
            
            # Create price settings
            PriceSetting.objects.get_or_create(
                category=category,
                defaults={
                    "base_price": base_price,
                    "quality_multiplier_standard": 1.0,
                    "quality_multiplier_professional": 1.5,
                    "quality_multiplier_premium": 2.0,
                    "urgency_multiplier_normal": 1.0,
                    "urgency_multiplier_medium": 1.5,
                    "urgency_multiplier_urgent": 2.0,
                    "bulk_discount_threshold": 5,
                    "bulk_discount_percentage": 10
                }
            )
        
        self.stdout.write(f"✅ Created {len(categories_data)} design categories with sizes and pricing")
    
    def create_sample_users(self):
        """Create sample users for testing"""
        users_data = [
            {
                "username": "designer1",
                "email": "designer1@skydesign.com",
                "password": "designer123",
                "name": "أحمد المصمم",
                "role": "DESIGNER",
                "is_designer": True
            },
            {
                "username": "designer2",
                "email": "designer2@skydesign.com",
                "password": "designer123",
                "name": "فاطمة المبدعة",
                "role": "DESIGNER",
                "gender": "female",
                "is_designer": True
            },
            {
                "username": "manager1",
                "email": "manager@skydesign.com",
                "password": "manager123",
                "name": "محمد المدير",
                "role": "MANAGER"
            },
            {
                "username": "teacher1",
                "email": "teacher1@school.com",
                "password": "teacher123",
                "name": "علي المدرس",
                "role": "CLIENT",
                "user_type": "teacher",
                "school_name": "مدرسة النور"
            },
            {
                "username": "shop1",
                "email": "shop1@business.com",
                "password": "shop123",
                "name": "محل الأمل للطباعة",
                "role": "CLIENT",
                "user_type": "shop",
                "region": "بغداد - الكرادة"
            },
            {
                "username": "mustafa",
                "email": "mustafa@skydesign.com",
                "password": "mustafa123",
                "name": "مصطفى",
                "role": "CLIENT",
                "points": 100,
                "is_premium": True
            }
        ]
        
        for user_data in users_data:
            is_designer = user_data.pop("is_designer", False)
            
            if not User.objects.filter(username=user_data["username"]).exists():
                password = user_data.pop("password")
                user = User.objects.create_user(**user_data)
                user.set_password(password)
                user.save()
                
                # Create designer profile if needed
                if is_designer:
                    DesignerProfile.objects.create(
                        user=user,
                        bio=f"مصمم جرافيك محترف مع خبرة في التصميم التعليمي",
                        skills=["Photoshop", "Illustrator", "After Effects"],
                        skill_level="advanced",
                        rating=4.5,
                        is_available=True
                    )
                
                self.stdout.write(f"✅ Created user: {user.username}")
            else:
                self.stdout.write(f"⚠️ User {user_data['username']} already exists")
    
    def create_games(self):
        """Create initial games"""
        
        # Create Wheel of Fortune
        wheel_segments = [
            {"id": 1, "text": "خصم 10%", "color": "#FF6B6B", "weight": 30, "prize_type": "discount", "prize_value": "10"},
            {"id": 2, "text": "تصميم مجاني", "color": "#4ECDC4", "weight": 5, "prize_type": "free_design", "prize_value": "1"},
            {"id": 3, "text": "50 نقطة", "color": "#45B7D1", "weight": 20, "prize_type": "points", "prize_value": "50"},
            {"id": 4, "text": "100 نقطة", "color": "#FFA500", "weight": 10, "prize_type": "points", "prize_value": "100"},
            {"id": 5, "text": "خصم 5%", "color": "#9B59B6", "weight": 25, "prize_type": "discount", "prize_value": "5"},
            {"id": 6, "text": "حظ أوفر", "color": "#95A5A6", "weight": 10, "prize_type": "nothing", "prize_value": "0"}
        ]
        
        wheel, created = WheelOfFortune.objects.get_or_create(
            title="عجلة الحظ اليومية",
            defaults={
                "description": "أدر العجلة واحصل على جوائز يومية!",
                "segments": wheel_segments,
                "is_active": True,
                "max_spins_per_day": 1
            }
        )
        
        if created:
            self.stdout.write("✅ Created Wheel of Fortune game")
        
        # Note: PuzzleGame requires image, so we'll create a placeholder
        self.stdout.write("ℹ️ Puzzle games require images - please upload images via admin panel")
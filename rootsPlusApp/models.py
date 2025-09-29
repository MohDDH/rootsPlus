from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db import models
import re
import bcrypt


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PHONE_REGEX = re.compile(r'^\+\d{1,3}-\d{4,15}$')

# Password must be at least 8 chars, contain letters, numbers, and symbols
PASSWORD_REGEX = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&^_\-])[A-Za-z\d@$!%*#?&^_\-]{8,}$'
)

class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}

        # Name
        if len(postData.get('name', '').strip()) < 2:
            errors['name'] = "Name must be at least 2 characters."

        # Email
        email = postData.get('email', '').strip()
        if not EMAIL_REGEX.match(email):
            errors['email'] = "Invalid email format."
        elif self.model.objects.filter(email=email).exists():
            errors['email'] = "Email already in use."

        # Phone
        phone = postData.get('phone', '').strip()
        if not PHONE_REGEX.match(phone):
            errors['phone'] = "Phone must be in the format +<country_code>-<number>. ex: +20-12345678"
        elif self.model.objects.filter(phone=phone).exists():
            errors['phone'] = "Phone number already in use."

        # City
        
        city = postData.get('city', '').strip()
        if len(city) < 2:
            errors['city'] = "City must be at least 2 characters."
        elif not city.isalpha():
            errors['city'] = "City must contain only letters."

        # Password
        password = postData.get('password', '')
        confirm_password = postData.get('confirm_password', '')

        if not PASSWORD_REGEX.match(password):
            errors['password'] = (
                "Password must be at least 8 characters long, "
                "contain letters, numbers, and at least one special character."
            )

        if password != confirm_password:
            errors['confirm_password'] = "Passwords do not match."

        return errors

    def login_validator(self, postData):
        errors = {}
        email = postData.get('email', '').strip()
        password = postData.get('password', '')
        phone = postData.get('phone', '').strip()  
        role = postData.get('role', '').strip().lower()  

        user_qs = self.model.objects.filter(email=email)
        if not user_qs.exists():
            errors['email'] = "Email not found."
        else:
            user = user_qs.first()

            
            if role == 'agronomist':
                if phone != user.phone:
                    errors['phone'] = "Phone number does not match."

            
            if not bcrypt.checkpw(password.encode(), user.password.encode()):
                errors['password'] = "Incorrect password."

        return errors
    
    
class User(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    password = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __str__(self):
        return self.name or f"User {self.id} - {self.name}"


class Agronomist(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    specialization = models.CharField(max_length=60, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    password = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __str__(self):
        return self.name or f"Agronomist {self.id} - {self.name}"


class Farm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=60, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    total_area = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, help_text="Total Area of Farm in dunum")
    agronomists = models.ManyToManyField(Agronomist, related_name='managed_farms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_crops_count(self):
        """Number of crops planted in the farm"""
        return self.crops.count()

    def get_total_farm_yield(self):
        """Total yield of the farm (in tons)"""
        total_yield_sum = sum(crop.total_yield if crop.total_yield is not None else 0 for crop in self.crops.all())
        return total_yield_sum

    def get_average_yield_per_dunum(self):
        """Average yield per dunum at the farm level"""
        total_yield = self.get_total_farm_yield()
        if self.total_area and self.total_area > 0:
            return round(total_yield / self.total_area, 2)
        return None
    
    def __str__(self):
        return self.name or f"Farm {self.id}"


class Crop(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='crops')
    crop_name = models.CharField(max_length=60, null=True, blank=True)
    crop_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Crop Area in dunum")
    planting_date = models.DateField(null=True, blank=True)
    yield_per_dunum = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Yield per dunum (tons/dunum)")
    status = models.CharField(max_length=100, null=True, blank=True)
    total_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total yield in tons")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # حساب الإنتاج الكلي تلقائيًا إذا كانت البيانات متوفرة
        if self.yield_per_dunum and self.crop_area:
            self.total_yield = round(self.yield_per_dunum * self.crop_area, 2)
        super().save(*args, **kwargs)

    def clean(self):
        if not self.crop_area or not self.farm.total_area:
            return

        total_with_current = (
            self.farm.crops.exclude(id=self.id).aggregate(total=Sum('crop_area'))['total'] or 0
        ) + self.crop_area

        if self.crop_area > self.farm.total_area:
            raise ValidationError("The crop area is larger than the farm's total area.")

        if total_with_current > self.farm.total_area:
            raise ValidationError("The total area of all crops exceeds the farm's total area.")
    
    def __str__(self):
        return f"Crop {self.id} - {self.crop_name}"


class Activity(models.Model):
    ACTIVITY_TYPES = [
    ('irrigation', 'Irrigation'),
    ('fertilization', 'Fertilization'),
    ('harvest', 'Harvest'),
    ('inspection', 'Inspection'),
    ('pest_control', 'Pest Control'),
    ('planting', 'Planting'),
    ('other', 'other')
]
    activity_type = models.CharField(max_length=60, choices=ACTIVITY_TYPES, null=True, blank=True)
    agronomist = models.ForeignKey(Agronomist, on_delete=models.CASCADE, related_name='activities')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='activities')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='activities')
    date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.activity_type or f"Activity {self.id}"


class Evaluation(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='evaluations')
    agronomist = models.ForeignKey(Agronomist, on_delete=models.CASCADE, related_name='evaluations')
    season = models.CharField(max_length=60, null=True, blank=True)

    # بيانات الإنتاج
    yield_amount = models.FloatField(null=True, blank=True, help_text="Total yield in tons")
    crops_count = models.IntegerField(null=True, blank=True, help_text="Number of crops in the farm")
    average_yield_per_dunum = models.FloatField(null=True, blank=True, help_text="Average yield per dunum (tons/dunum)")

    # بيانات التقييم
    activity_score = models.FloatField(null=True, blank=True)
    cost_efficiency = models.FloatField(null=True, blank=True)
    total_cost = models.FloatField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)
    overall_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self):
    # إذا في مزرعة مرتبطة بالتقييم
        if self.farm:
        # إذا ما في قيمة للإنتاج الكلي، نحسبها من المزرعة
            if self.yield_amount is None:
                self.yield_amount = self.farm.get_total_farm_yield()

            # إذا ما في قيمة لعدد المحاصيل، نحسبها من المزرعة
            if self.crops_count is None:
                self.crops_count = self.farm.get_crops_count()

            # إذا ما في قيمة لمتوسط الإنتاجية لكل دونم، نحسبها من المزرعة
            if self.average_yield_per_dunum is None:
                self.average_yield_per_dunum = self.farm.get_average_yield_per_dunum()

    # حفظ البيانات في قاعدة البيانات
        super(Evaluation, self).save()

    def __str__(self):
        return f"Evaluation {self.id} - {self.season}"


class FarmReport(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='reports')
    season = models.CharField(max_length=60, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    # بيانات التقرير
    summary = models.TextField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)
    overall_score = models.FloatField(null=True, blank=True)

    # إضافات
    author = models.ForeignKey(Agronomist, on_delete=models.CASCADE, related_name='theReports',null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="Draft")

    def build_summary(self):
        """ملخص ثابت من بيانات المزرعة"""
        supervisors = ", ".join([agro.name for agro in self.farm.agronomists.all()])
        return (
            f"Farm: {self.farm.name}\n"
            f"Location: {self.farm.location}\n"
            f"Area: {self.farm.total_area} dunums\n"
            f"Crops Count: {self.farm.get_crops_count()}\n"
            f"Supervising Agronomists: {supervisors or 'N/A'}\n"
        )

    def save(self, *args, **kwargs):
        # إذا ما في ملخص، ابنيه تلقائيًا
        if not self.summary and self.farm:
            self.summary = self.build_summary()
        super().save(*args, **kwargs)
    


class Analysis(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='analyses')
    soil_type = models.CharField(max_length=50, null=True, blank=True, help_text="Soil type (e.g., Clay, Sandy, Loamy)")
    soil_salinity = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,help_text="Soil salinity (dS/m)")
    soil_ph = models.DecimalField(max_digits=4,decimal_places=2,null=True,blank=True,help_text="Soil pH") 
    water_salinity = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True,help_text="Water salinity (dS/m)")
    analysis_date = models.DateField(null=True,blank=True,help_text="Date of analysis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.farm.name} on {self.analysis_date}"    

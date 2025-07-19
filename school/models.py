from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

TZ_PHONE_RE = r'^\+255\d{9}$'
tz_phone_validator = RegexValidator(TZ_PHONE_RE, "Use +255XXXXXXXXX format (Tanzanian mobile).")

class AcademicYear(models.Model):
    year = models.PositiveSmallIntegerField(unique=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year"]

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.year)

class SchoolClass(models.Model):
    name = models.CharField(max_length=40)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="classes")

    class Meta:
        unique_together = ("name", "academic_year")
        ordering = ["academic_year__year", "name"]

    def __str__(self):
        return f"{self.name} – {self.academic_year.year}"

class StudentClassAssignment(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="class_assignments")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="assignments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="assignments")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "academic_year")
        ordering = ["-academic_year__year"]

    def __str__(self):
        return f"{self.student} in {self.school_class} ({self.academic_year.year})"

class Student(models.Model):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=6,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        default='Male'
    )
    guardian1_phone = models.CharField(validators=[tz_phone_validator], max_length=13)
    guardian2_phone = models.CharField(validators=[tz_phone_validator], max_length=13, blank=True, null=True)
    admission_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.CheckConstraint(check=models.Q(guardian1_phone__regex=TZ_PHONE_RE), name="guardian1_format_ok"),
            models.CheckConstraint(check=models.Q(guardian2_phone__isnull=True) | models.Q(guardian2_phone__regex=TZ_PHONE_RE), name="guardian2_format_ok"),
        ]

    def __str__(self):
        full_name = f"{self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        full_name += f" {self.last_name}"
        return full_name

    def get_current_class(self):
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            assignment = self.class_assignments.filter(academic_year=current_year).first()
            return assignment.school_class if assignment else None
        return None

class Staff(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(validators=[tz_phone_validator], max_length=13, unique=True)
    email = models.EmailField(blank=True, null=True)
    hire_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
from django import forms
from django.core.exceptions import ValidationError
from .models import AcademicYear, SchoolClass, Student, Staff, StudentClassAssignment, tz_phone_validator

def current_year_or_none():
    """Return the AcademicYear flagged is_current=True (or None)."""
    return AcademicYear.objects.filter(is_current=True).first()

class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['year', 'is_current']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2025'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2100:
            raise ValidationError("Year must be between 2000 and 2100.")
        return year

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'academic_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Grade 1'}),
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['academic_year'].queryset = AcademicYear.objects.all()



class StudentForm(forms.ModelForm):
    current_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Current Class",
        required=False
    )
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Gender",
        initial='Male'
    )

    class Meta:
        model = Student
        fields = [
            'first_name', 'middle_name', 'last_name', 'gender',
            'guardian1_phone', 'guardian2_phone',
            'admission_date',          # ← here
            'is_active'
        ]
        widgets = {
            'first_name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'middle_name':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle name (optional)'}),
            'last_name':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'gender':          forms.Select(attrs={'class': 'form-select'}),
            'guardian1_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+2557XXXXXXXX'}),
            'guardian2_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+2557XXXXXXXX (optional)'}),
            'admission_date':  forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),  # ← widget
            'is_active':       forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = current_year_or_none()
        if current_year:
            self.fields["current_class"].queryset = SchoolClass.objects.filter(academic_year=current_year)
        else:
            self.fields["current_class"].queryset = SchoolClass.objects.none()
            self.fields["current_class"].disabled = True
            self.fields["current_class"].help_text = "⚠️ First create an Academic Year and mark it as ‘current’."
        if self.instance.pk:
            current_class = self.instance.get_current_class()
            if current_class:
                self.initial['current_class'] = current_class
            self.initial['gender'] = self.instance.gender

    def clean(self):
        cleaned_data = super().clean()
        if not current_year_or_none() and 'current_class' in cleaned_data and cleaned_data['current_class']:
            raise ValidationError("No current Academic Year defined — cannot assign a class yet.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            current_year = current_year_or_none()
            if current_year and 'current_class' in self.cleaned_data and self.cleaned_data['current_class']:
                StudentClassAssignment.objects.update_or_create(
                    student=instance,
                    academic_year=current_year,
                    defaults={'school_class': self.cleaned_data['current_class']}
                )
        return instance

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'phone', 'email', 'hire_date', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+2557XXXXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'optional@example.com'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        tz_phone_validator(phone)
        return phone
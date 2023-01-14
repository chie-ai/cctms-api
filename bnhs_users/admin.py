from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from .models import *
from covid19_case_records.models import CovidCaseRecord, VaccinationRecord


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = BNHSUser
        fields = ['username', 'first_name', 'middle_name', 'last_name', 'sex', 'address', 'contact_number', 'email', 'usertype']
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = BNHSUser
        fields = ['username', 'first_name', 'middle_name', 'last_name', 'sex', 'address', 'contact_number', 'email', 'usertype', 'is_admin']

    def clean_password(self):
        return self.initial['password']

@admin.register(BNHSUser)
class BNHSUserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ['id', 'username', 'first_name', 'middle_name', 'last_name', 'sex', 'address', 'contact_number', 'email', 'usertype', 'is_admin']
    search_fields = ('username', 'first_name', 'middle_name', 'last_name', 'email')
    empty_value_display = '-empty-'
    ordering = ('id',)
    filter_horizontal = ()

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'middle_name', 'sex', 'address', 'contact_number', 'email', 'usertype')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_admin',
                )
        }),
        # ('Important dates', {
        #     'fields': ('last_login', 'date_joined')
        # }),
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password', 'password2')
        }),
        ('Personal info', { 
            'fields': ('first_name', 'last_name', 'middle_name', 'sex', 'address', 'contact_number', 'email', 'usertype')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_admin'
            )
        }),
        # ('Important dates', {
        #     'fields': ('last_login', 'date_joined')
        # }),
    )

@admin.register(UserNumber)
class UserNumberAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'user_number']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_id', 'level']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'profile_file']

@admin.register(CovidCaseRecord)
class CovidCaseRecordAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'classification', 'severity', 'created_at']

@admin.register(HealthCareService)
class HealthCareServiceAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'health_care_service']

@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'vaccine_brand', 'vaccine_description', 'vaccinated_at']

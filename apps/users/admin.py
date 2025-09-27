from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSession, DailyAttendance


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'date_creation')
    list_filter = ('role', 'is_staff', 'is_superuser', 'date_creation')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_creation',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('telephone', 'role')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('email', 'telephone', 'role')
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'duration_display', 'is_active', 'ip_address')
    list_filter = ('is_active', 'login_time', 'user__role')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('login_time', 'logout_time', 'duration_display')
    date_hierarchy = 'login_time'
    
    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"
        return "En cours"
    duration_display.short_description = "Durée"


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'first_login', 'last_logout', 'total_hours_display')
    list_filter = ('date', 'user__role')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'
    
    def total_hours_display(self, obj):
        if obj.total_hours:
            hours = obj.total_hours.total_seconds() // 3600
            minutes = (obj.total_hours.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"
        return "N/A"
    total_hours_display.short_description = "Heures totales"
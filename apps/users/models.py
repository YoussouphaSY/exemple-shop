from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with additional fields."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Gestionnaire'),
        ('cashier', 'Caissier'),
    ]
    
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Administrateur')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        """Assign user to appropriate group based on role."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Create groups if they don't exist and assign permissions
            self.assign_role_permissions()
    
    def assign_role_permissions(self):
        """Assign permissions based on user role."""
        # Remove from all groups first
        self.groups.clear()
        
        # Create groups if they don't exist
        admin_group, _ = Group.objects.get_or_create(name='Administrateurs')
        manager_group, _ = Group.objects.get_or_create(name='Gestionnaires')
        cashier_group, _ = Group.objects.get_or_create(name='Caissiers')
        
        if self.role == 'admin':
            self.groups.add(admin_group)
            self.is_staff = True
            self.is_superuser = True
        elif self.role == 'manager':
            self.groups.add(manager_group)
            self.is_staff = True
        elif self.role == 'cashier':
            self.groups.add(cashier_group)
class UserSession(models.Model):
    """Track user login/logout sessions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Session utilisateur"
        verbose_name_plural = "Sessions utilisateurs"
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duration(self):
        """Calculate session duration."""
        if self.logout_time:
            return self.logout_time - self.login_time
        return timezone.now() - self.login_time
    
    def close_session(self):
        """Close the session."""
        self.logout_time = timezone.now()
        self.is_active = False
        self.save()
        
        # self.save(update_fields=['is_staff', 'is_superuser'])
class DailyAttendance(models.Model):
    """Daily attendance summary for admin alerts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    first_login = models.TimeField()
    last_logout = models.TimeField(null=True, blank=True)
    total_hours = models.DurationField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Présence quotidienne"
        verbose_name_plural = "Présences quotidiennes"
        unique_together = ['user', 'date']
        ordering = ['-date', 'user__username']
    
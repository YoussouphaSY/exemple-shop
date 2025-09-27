from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import UserSession, DailyAttendance

User = get_user_model()


@receiver(user_logged_in)
def create_user_session(sender, request, user, **kwargs):
    """Create session when user logs in."""
    # Get client info
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Create session
    session = UserSession.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Store session ID in request session
    request.session['user_session_id'] = session.id
    
    # Update daily attendance
    today = timezone.now().date()
    current_time = timezone.now().time()
    
    attendance, created = DailyAttendance.objects.get_or_create(
        user=user,
        date=today,
        defaults={'first_login': current_time}
    )
    
    if not created and current_time < attendance.first_login:
        attendance.first_login = current_time
        attendance.save()


@receiver(user_logged_out)
def close_user_session(sender, request, user, **kwargs):
    """Close session when user logs out."""
    session_id = request.session.get('user_session_id')
    if session_id:
        try:
            session = UserSession.objects.get(id=session_id, user=user)
            session.close_session()
            
            # Update daily attendance
            today = timezone.now().date()
            current_time = timezone.now().time()
            
            try:
                attendance = DailyAttendance.objects.get(user=user, date=today)
                attendance.last_logout = current_time
                
                # Calculate total hours
                if attendance.first_login:
                    from datetime import datetime, timedelta
                    login_dt = datetime.combine(today, attendance.first_login)
                    logout_dt = datetime.combine(today, current_time)
                    attendance.total_hours = logout_dt - login_dt
                
                attendance.save()
            except DailyAttendance.DoesNotExist:
                pass
                
        except UserSession.DoesNotExist:
            pass
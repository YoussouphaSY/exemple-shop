from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserSession

User = get_user_model()


class UserSessionMiddleware:
    """Middleware to track user sessions and update last activity."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Update last activity for authenticated users
        if request.user.is_authenticated:
            session_id = request.session.get('user_session_id')
            if session_id:
                try:
                    session = UserSession.objects.get(
                        id=session_id, 
                        user=request.user,
                        is_active=True
                    )
                    # Update last activity (you could add a last_activity field)
                    # session.last_activity = timezone.now()
                    # session.save(update_fields=['last_activity'])
                except UserSession.DoesNotExist:
                    pass
        
        response = self.get_response(request)
        return response
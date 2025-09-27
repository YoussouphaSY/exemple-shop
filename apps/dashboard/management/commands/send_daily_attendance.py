from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.users.models import DailyAttendance
from apps.dashboard.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Send daily attendance summary to admin'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date for attendance report (YYYY-MM-DD)',
        )
    
    def handle(self, *args, **options):
        if options['date']:
            from datetime import datetime
            date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        # Get attendance for the date
        attendances = DailyAttendance.objects.filter(date=date).select_related('user')
        
        if not attendances.exists():
            self.stdout.write(
                self.style.WARNING(f'No attendance records found for {date}')
            )
            return
        
        # Prepare summary
        summary_lines = [f"📊 Résumé de présence du {date.strftime('%d/%m/%Y')}:\n"]
        
        for attendance in attendances:
            user = attendance.user
            first_login = attendance.first_login.strftime('%H:%M') if attendance.first_login else 'N/A'
            last_logout = attendance.last_logout.strftime('%H:%M') if attendance.last_logout else 'En ligne'
            
            total_hours = "N/A"
            if attendance.total_hours:
                hours = attendance.total_hours.total_seconds() // 3600
                minutes = (attendance.total_hours.total_seconds() % 3600) // 60
                total_hours = f"{int(hours)}h {int(minutes)}m"
            
            summary_lines.append(
                f"👤 {user.get_full_name() or user.username} ({user.get_role_display()})\n"
                f"   🕐 Arrivée: {first_login}\n"
                f"   🕐 Départ: {last_logout}\n"
                f"   ⏱️ Durée: {total_hours}\n"
            )
        
        summary_text = "\n".join(summary_lines)
        
        # Send notification to all admins
        admins = User.objects.filter(role='admin', is_active=True)
        
        for admin in admins:
            Notification.objects.create(
                titre=f"Résumé de présence - {date.strftime('%d/%m/%Y')}",
                message=summary_text,
                type="info",
                utilisateur=admin,
                url="/admin/attendance/"
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Daily attendance summary sent for {date}')
        )
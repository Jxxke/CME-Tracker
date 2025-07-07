from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from tracker.models import MedicalLicense
from datetime import timedelta

class Command(BaseCommand):
    help = "Send license expiration reminder emails"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        for license in MedicalLicense.objects.select_related("user").all():
            if not license.expiration_date:
                continue

            days_left = (license.expiration_date - today).days

            if days_left in [60, 30, 15]:
                subject = f"Your medical license expires in {days_left} days"
                message = (
                    f"Hi {license.user.first_name},\n\n"
                    f"Your license ({license.profession} — {license.state}) "
                    f"is set to expire on {license.expiration_date}.\n\n"
                    f"Make sure you have uploaded enough CME to remain compliant."
                )
                send_mail(
                    subject,
                    message,
                    "Jake Stone <jakelawrencestone@gmail.com>",
                    [license.user.email],
                    fail_silently=False,
                )

        self.stdout.write(self.style.SUCCESS("✅ License expiration reminders sent."))

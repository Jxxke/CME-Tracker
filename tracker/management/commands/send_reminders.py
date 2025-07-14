from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from tracker.models import MedicalLicense, ReminderLog
from datetime import timedelta


class Command(BaseCommand):
    help = "Send license expiration reminder emails"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        days_list = [15, 30, 60]
        reminders_sent = 0

        for license in MedicalLicense.objects.select_related("user"):
            if not license.expiration_date:
                continue

            days_until_expiration = (license.expiration_date - today).days
            print(f"⏱ {license.user.email}: {days_until_expiration} days until expiration")

            if days_until_expiration in days_list:
                already_sent = ReminderLog.objects.filter(
                    user=license.user,
                    license=license,
                    days_before=days_until_expiration
                ).exists()

                if already_sent:
                    continue

                subject = f"⏰ Your license expires in {days_until_expiration} days"
                message = (
                    f"Hi {license.user.first_name},\n\n"
                    f"Your {license.profession} license in {license.state} is expiring on {license.expiration_date}.\n"
                    f"Log in to CME Tracker to upload CME hours and ensure compliance.\n\n"
                    f"https://cme-tracker.onrender.com/"
                )

                send_mail(
                    subject,
                    message,
                    "CME Tracker <jakelawrencestone@gmail.com>",
                    [license.user.email],
                    fail_silently=False,
                )

                ReminderLog.objects.create(
                    user=license.user,
                    license=license,
                    days_before=days_until_expiration
                )
                reminders_sent += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Sent {reminders_sent} reminders."))

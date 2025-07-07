from django.core.management.base import BaseCommand
from tracker.models import CMERule
import re


class Command(BaseCommand):
    help = 'Loads CME rules into the database'

    def handle(self, *args, **kwargs):
        rules = [
            ("AL", "MD", 50, 2, "controlled", "2 hrs controlled substances"),
            ("AK", "MD", 50, 2, "opioid", "2 hrs pain/opioid"),
            ("AZ", "MD", 40, 2, "opioid", "3 hrs opioid-related CME"),
            ("AR", "MD", 20, 1, "opioid", "1 hr opioids; 3 hrs first 2 yrs"),
            ("CA", "MD", 50, 2, "pain", "12 hrs pain/terminal care"),
            ("CO", "MD", 30, 2, "opioid", "2 hrs opioid prescribing"),
            ("CT", "MD", 50, 2, "controlled", "Controlled substances"),
            ("DE", "MD", 40, 2, "controlled", "2 hrs controlled substances"),
            ("DC", "MD", 50, 2, "public_health", "10% public health"),
            ("FL", "MD", 40, 2, "opioid", "2 hrs medical errors; 2 hrs opioids"),
            ("GA", "MD", 40, 2, "opioid", "3 hrs opioid CME"),
            ("HI", "MD", 40, 2, "general", "Cat 1 only"),
            ("ID", "MD", 40, 2, "pain", "Pain/opioids"),
            ("IL", "MD", 150, 3, "bias", "60 hrs Cat 1; 1 hr harassment/bias"),
            ("IA", "MD", 40, 2, "opioid", "Abuse, opioid, dementia topics"),
            ("KS", "MD", 50, 1, "pain", "Pain/practice topics"),
            ("KY", "MD", 60, 3, "controlled", "30 hrs Cat 1; drug diversion"),
            ("LA", "MD", 20, 1, "controlled", "3 hrs drug diversion"),
            ("ME", "MD", 40, 2, "opioid", "3 hrs opioid"),
            ("MD", "MD", 50, 2, "opioid", "2 hrs opioid/bias"),
            ("MA", "MD", 50, 2, "opioid", "Opioid, EHR, bias, risk mgmt"),
            ("MI", "MD", 150, 3, "pain", "3 hrs pain & ethics"),
            ("MN", "MD", 75, 3, "general", "Cat 1 only"),
            ("MS", "MD", 40, 2, "controlled", "5 hrs controlled substances"),
            ("MO", "MD", 50, 2, "general", "Cat 1 only"),
            ("MT", "MD", 60, 3, "general", "No specific requirements"),
            ("NE", "MD", 50, 2, "general", "No specific requirements"),
            ("NV", "MD", 40, 2, "suicide", "2 hrs suicide; 4 hrs controlled substances"),
            ("NH", "MD", 100, 2, "opioid", "3 hrs opioids"),
            ("NJ", "MD", 100, 2, "opioid", "Opioid topics required"),
            ("NM", "MD", 75, 3, "pain", "5 hrs pain management Yr 1"),
            ("NY", "MD", 0, 2, "child_abuse", "Child abuse, infections, 3 hrs pain if DEA"),
            ("NC", "MD", 60, 3, "controlled", "3 hrs controlled substances"),
            ("ND", "MD", 40, 2, "general", "Cat 1 only"),
            ("OH", "MD", 50, 2, "ethics", "1 hr reporting duty"),
            ("OK", "MD", 60, 3, "pain", "1 hr pain annually"),
            ("OR", "MD", 60, 2, "pain", "6 hrs pain management"),
            ("PA", "MD", 100, 2, "opioid", "2 hrs opioids; 2 hrs child abuse"),
            ("RI", "MD", 40, 2, "opioid", "Opioids and risk topics"),
            ("SC", "MD", 40, 2, "ethics", "Opioid and ethics"),
            ("SD", "MD", 0, 2, "general", "No CME required"),
            ("TN", "MD", 40, 2, "opioid", "Opioids & prescribing practices"),
            ("TX", "MD", 48, 2, "ethics", "2 hrs ethics + pain/human trafficking"),
            ("UT", "MD", 40, 2, "controlled", "3.5 hrs controlled + suicide"),
            ("VT", "MD", 30, 2, "controlled", "1 hr palliative; controlled subs"),
            ("VA", "MD", 60, 2, "general", "30 hrs Cat 1"),
            ("WA", "MD", 200, 4, "suicide", "6 hrs suicide; 2 hrs equity"),
            ("WV", "MD", 50, 2, "controlled", "3 hrs controlled substances"),
            ("WI", "MD", 30, 2, "opioid", "2 hrs opioid"),
            ("WY", "MD", 60, 3, "controlled", "Controlled substances"),
        ]

        for state, profession, hours, years, special_category, notes in rules:
            match = re.search(r"(\d+(\.\d+)?)\s*hrs?", notes.lower())
            special_hours = float(match.group(1)) if match else 0.0

            CMERule.objects.update_or_create(
                state=state,
                profession=profession,
                defaults={
                    'hours_required': hours,
                    'renewal_period': years,
                    'special_category': special_category,
                    'special_hours_required': special_hours,
                    'notes': notes
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ CME rules with special requirements loaded successfully!"))

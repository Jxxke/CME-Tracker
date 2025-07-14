### models.py

from django.db import models
from django.contrib.auth.models import User

CME_CATEGORIES = [
    ('opioid', 'Opioid Education'),
    ('ethics', 'Ethics'),
    ('bias', 'Bias and Harassment'),
    ('controlled', 'Controlled Substances'),
    ('pain', 'Pain Management'),
    ('suicide', 'Suicide Prevention'),
    ('child_abuse', 'Child Abuse'),
    ('public_health', 'Public Health'),
    ('medical_errors', 'Medical Errors'),
    ('general', 'General'),
]

class CMERule(models.Model):
    state = models.CharField(max_length=2)
    profession = models.CharField(max_length=100)
    hours_required = models.PositiveIntegerField()
    renewal_period = models.PositiveIntegerField()
    special_category = models.CharField(max_length=100, blank=True, null=True)
    special_hours_required = models.FloatField(default=0.0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.state} - {self.profession} ({self.hours_required} hrs, every {self.renewal_period} yrs)"

LICENSE_STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
    ('Expired', 'Expired'),
]

class MedicalLicense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    license_number = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=LICENSE_STATUS_CHOICES)
    issue_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    rule = models.ForeignKey(CMERule, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.profession} — {self.state} — {self.license_number}"




class CMEEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    hours = models.FloatField()
    date_completed = models.DateField()
    category = models.CharField(max_length=50, choices=CME_CATEGORIES)
    pdf_file = models.FileField(upload_to='cme_pdfs/', null=True, blank=True)  # ✅ Add this
    certificate = models.FileField(upload_to='cme_certificates/', null=True, blank=True)

    def __str__(self):
        return f"{self.topic} - {self.hours} hrs"

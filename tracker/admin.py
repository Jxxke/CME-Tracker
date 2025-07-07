from django.contrib import admin

# Register your models here.
from .models import CMERule, MedicalLicense, CMEEntry

admin.site.register(CMERule)
admin.site.register(MedicalLicense)
admin.site.register(CMEEntry)

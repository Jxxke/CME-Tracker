from django import forms
from .models import MedicalLicense, CMEEntry

class MedicalLicenseForm(forms.ModelForm):
    class Meta:
        model = MedicalLicense
        fields = [
            'license_number',
            'state',
            'profession',
            'issue_date',
            'expiration_date',
            'status',
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from .models import CMEEntry, CME_CATEGORIES

class CMEEntryForm(forms.ModelForm):
    category = forms.ChoiceField(choices=CME_CATEGORIES)

    class Meta:
        model = CMEEntry
        fields = ['topic', 'hours', 'date_completed', 'category']



from django import forms

class CMEUploadPDFForm(forms.Form):
    pdf_file = forms.FileField(label="Upload CME Certificate PDF")



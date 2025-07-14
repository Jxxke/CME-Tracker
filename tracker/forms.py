from django import forms
from .models import MedicalLicense, CMERule, CME_CATEGORIES

CUSTOM_RULE_SENTINEL = 'custom'

class MedicalLicenseForm(forms.ModelForm):
    rule_selector = forms.ChoiceField(label="CME Rule", required=False)

    # Custom rule fields
    custom_renewal_period = forms.IntegerField(required=False, min_value=1)
    custom_total_cme_hours = forms.FloatField(required=False, min_value=0)
    custom_special_category = forms.ChoiceField(choices=[('', 'None')] + CME_CATEGORIES, required=False)
    custom_special_hours_required = forms.FloatField(required=False, min_value=0)

    class Meta:
        model = MedicalLicense
        fields = ['state', 'license_number', 'status', 'issue_date', 'expiration_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rules = CMERule.objects.filter(profession='MD')
        choices = [('', 'Select a state rule'), (CUSTOM_RULE_SENTINEL, 'Custom CME Rule')]
        choices += [(str(rule.pk), str(rule)) for rule in rules]
        self.fields['rule_selector'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('rule_selector') == CUSTOM_RULE_SENTINEL:
            if not cleaned_data.get('custom_renewal_period') or not cleaned_data.get('custom_total_cme_hours'):
                self.add_error('custom_renewal_period', 'Required for custom rule.')
                self.add_error('custom_total_cme_hours', 'Required for custom rule.')
        return cleaned_data



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



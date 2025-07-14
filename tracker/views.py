from django.shortcuts import render, redirect
from .models import MedicalLicense, CMERule
from .forms import MedicalLicenseForm
from django.contrib.auth.decorators import login_required
from .models import CMEEntry
from .forms import CMEEntryForm
from .utils import check_cme_compliance
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import CMERule
from django.http import HttpResponse
from .forms import CUSTOM_RULE_SENTINEL



@login_required
def upload_cme(request):
    if request.method == 'POST':
        if 'topic' in request.POST and 'hours' in request.POST and 'category' in request.POST:
            # This is a parsed PDF submission
            topic = request.POST['topic']
            hours = float(request.POST['hours'])
            category = request.POST['category']
            date_completed = request.POST.get('date_completed')

            cme = CMEEntry(
                user=request.user,
                topic=topic,
                hours=hours,
                category=category,
                date_completed=date_completed,
            )
            cme.save()
            return redirect('view_cme')

        else:
            # This is a regular form submission
            form = CMEEntryForm(request.POST)
            if form.is_valid():
                cme = form.save(commit=False)
                cme.user = request.user
                cme.save()
                return redirect('view_cme')
    else:
        form = CMEEntryForm()
    return render(request, 'tracker/upload_cme.html', {'form': form})



@login_required
def view_cme(request):
    entries = CMEEntry.objects.filter(user=request.user).order_by('-date_completed')
    return render(request, 'tracker/view_cme.html', {'entries': entries})

from .forms import MedicalLicenseForm, CUSTOM_RULE_SENTINEL

@login_required
def upload_license(request):
    if request.method == 'POST':
        form = MedicalLicenseForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            license.user = request.user
            license.profession = "MD"

            rule_choice = form.cleaned_data['rule_selector']

            if rule_choice == CUSTOM_RULE_SENTINEL:
                new_rule = CMERule.objects.create(
                    state='ZZ',
                    profession='MD',
                    hours_required=form.cleaned_data['custom_total_cme_hours'],
                    renewal_period=form.cleaned_data['custom_renewal_period'],
                    special_category=form.cleaned_data['custom_special_category'],
                    special_hours_required=form.cleaned_data['custom_special_hours_required'],
                    notes='User-defined custom rule'
                )
                license.rule = new_rule
            elif rule_choice:
                license.rule = CMERule.objects.get(pk=int(rule_choice))
            else:
                license.rule = None

            license.save()
            return redirect('view_licenses')
        else:
            print("❌ Invalid form:", form.errors)
    else:
        form = MedicalLicenseForm()

    return render(request, 'tracker/upload_license.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MedicalLicense, CMEEntry
from dateutil.relativedelta import relativedelta
from datetime import date

@login_required
def view_licenses(request):
    licenses = MedicalLicense.objects.filter(user=request.user)
    display_data = []

    for license in licenses:
        rule = license.rule

        # Handle renewal years and cutoff date
        if rule and license.expiration_date:
            renewal_years = rule.renewal_period
            cutoff_date = license.expiration_date - relativedelta(years=renewal_years)
        else:
            cutoff_date = None

        # Filter CME entries after cutoff date
        if cutoff_date:
            cme_entries = CMEEntry.objects.filter(user=request.user, date_completed__gte=cutoff_date)
        else:
            cme_entries = CMEEntry.objects.filter(user=request.user)

        # Total general CME hours
        total_hours = sum(entry.hours for entry in cme_entries)

        # Pull rule requirements
        required = rule.hours_required if rule else 0
        special_category = rule.special_category if rule else None
        special_required = rule.special_hours_required if rule else 0

        # Special CME hours
        if special_category:
            special_entries = cme_entries.filter(category=special_category)
            special_completed = sum(entry.hours for entry in special_entries)
        else:
            special_completed = 0

        display_data.append({
            'license': license,
            'completed': total_hours,
            'required': required,
            'compliant': total_hours >= required,
            'missing': max(0, required - total_hours),

            'special_category': special_category,
            'special_required': special_required,
            'special_completed': special_completed,
            'special_compliant': special_completed >= special_required,
            'cutoff_date': cutoff_date,
        })

    return render(request, 'tracker/view_licenses.html', {'licenses': display_data})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redirects to /accounts/login/
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.shortcuts import get_object_or_404

@login_required
def delete_license(request, license_id):
    license = get_object_or_404(MedicalLicense, id=license_id, user=request.user)

    if request.method == 'POST':
        license.delete()
        return redirect('view_licenses')

    return render(request, 'tracker/delete_license.html', {'license': license})


@login_required
def delete_cme(request, cme_id):
    cme = get_object_or_404(CMEEntry, id=cme_id, user=request.user)
    
    if request.method == 'POST':
        cme.delete()
        return redirect('view_cme')

    return render(request, 'tracker/delete_cme.html', {'cme': cme})



from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CMEUploadPDFForm
from .models import CMEEntry, CME_CATEGORIES
from .utils import parse_cme_pdf  # your parsing function
import re

@login_required
def upload_pdf_cme(request):
    # STEP 4: Final confirmation step (form POST after preview)
    if request.method == 'POST' and 'hours' in request.POST:
        path = request.session.get('uploaded_pdf_path')
        cme = CMEEntry(
            user=request.user,
            topic=request.POST['topic'],
            hours=float(request.POST['hours']),
            category=request.POST['category'],
            date_completed=request.POST['date_completed'],
        )
        if path:
            with default_storage.open(path, 'rb') as f:
                cme.certificate.save(path.split('/')[-1], f)
            del request.session['uploaded_pdf_path']
        cme.save()
        return redirect('view_cme')

    # STEP 1: Initial file upload
    elif request.method == 'POST':
        form = CMEUploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['pdf_file']

            # Save file temporarily
            temp_path = default_storage.save(f'temp/{file.name}', ContentFile(file.read()))
            request.session['uploaded_pdf_path'] = temp_path

            # Parse the uploaded file
            parsed = parse_cme_pdf(file)

            return render(request, 'tracker/confirm_parsed_cme.html', {
                'topic': parsed['topic'],
                'hours': parsed['hours'],
                'category': parsed['category'],
                'date_completed': parsed['date_completed'],
            })
    else:
        form = CMEUploadPDFForm()

    return render(request, 'tracker/upload_pdf.html', {'form': form})


from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

@login_required
def view_cme_pdf(request, cme_id):
    entry = get_object_or_404(CMEEntry, id=cme_id, user=request.user)
    if not entry.certificate:
        raise Http404("No certificate attached.")

    response = HttpResponse(entry.certificate, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="certificate.pdf"'
    return response


from django.shortcuts import render

def home(request):
    return render(request, "tracker/home.html")


from django.http import JsonResponse
from .models import CMERule

def get_cme_defaults(request):
    state = request.GET.get('state')
    license_type = request.GET.get('license_type')
    try:
        rule = CMERule.objects.get(state=state, profession=license_type)
        data = {
            'renewal_period_years': rule.renewal_period,
            'total_cme_required': rule.hours_required,
            'special_cme_category': rule.special_category,
            'special_cme_hours_required': rule.special_hours_required
        }
        return JsonResponse(data)
    except CMERule.DoesNotExist:
        return JsonResponse({}, status=404)
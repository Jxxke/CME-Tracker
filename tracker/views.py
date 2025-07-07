from django.shortcuts import render, redirect
from .models import MedicalLicense, CMERule
from .forms import MedicalLicenseForm
from django.contrib.auth.decorators import login_required
from .models import CMEEntry
from .forms import CMEEntryForm
from .utils import check_cme_compliance
from django.contrib.auth.forms import UserCreationForm

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


@login_required
def upload_license(request):
    if request.method == 'POST':
        form = MedicalLicenseForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)

            # Try to match a CME rule
            try:
                matched_rule = CMERule.objects.get(
                    state=license.state.upper(),
                    profession=license.profession.upper()
                )
                license.rule = matched_rule
            except CMERule.DoesNotExist:
                license.rule = None  # No rule found

            license.user = request.user
            license.save()
            return redirect('view_licenses')
    else:
        form = MedicalLicenseForm()
    return render(request, 'tracker/upload_license.html', {'form': form})


from django.shortcuts import render
from .models import MedicalLicense, CMEEntry
from django.contrib.auth.decorators import login_required
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta

@login_required
def view_licenses(request):
    licenses = MedicalLicense.objects.filter(user=request.user)
    display_data = []

    for license in licenses:
        renewal_date = license.expiration_date or date.min

        rule = license.rule
        # Calculate cutoff date
        cutoff_date = license.expiration_date - relativedelta(years=rule.renewal_period)

        # Filter CME after cutoff only
        cme_entries = CMEEntry.objects.filter(user=request.user, date_completed__gte=cutoff_date)

        # General CME hours
        total_hours = sum(entry.hours for entry in cme_entries)

        # Get rule for this license
        if rule:
            required = rule.hours_required
            special_category = rule.special_category
            special_required = rule.special_hours_required or 0
        else:
            required = 0
            special_category = None
            special_required = 0

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

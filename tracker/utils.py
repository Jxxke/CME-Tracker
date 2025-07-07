from datetime import timedelta, date
from .models import CMEEntry

from datetime import timedelta, date
from .models import CMEEntry

def check_cme_compliance(license):
    rule = license.rule
    if not rule:
        return (None, 0, 0)

    # Only count CME within the renewal period
    cutoff_date = date.today() - timedelta(days=365 * rule.renewal_period)
    entries = CMEEntry.objects.filter(
        license=license,
        date_completed__gte=cutoff_date
    )

    total_hours = sum(entry.hours for entry in entries)
    is_compliant = total_hours >= rule.hours_required

    return (is_compliant, total_hours, rule.hours_required)


from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
import fitz  # PyMuPDF
import re
from .forms import CMEUploadPDFForm
from .models import CME_CATEGORIES
from PyPDF2 import PdfReader
from datetime import datetime
from .models import CME_CATEGORIES
from pdf2image import convert_from_bytes
import pytesseract

def parse_cme_pdf(file):
    file_bytes = file.read()
    reader = PdfReader(file)
    first_page = reader.pages[0]
    text = first_page.extract_text()

    # ✅ OCR fallback if PyPDF can't read text
    if not text or text.strip() == "":
        image = convert_from_bytes(file_bytes, dpi=300)[0]  # just first page
        text = pytesseract.image_to_string(image)

    # ✅ Topic from first line
    lines = text.strip().splitlines()
    topic = lines[0][:100] if lines else "Untitled CME"

    # ✅ Match "is awarded 5 AMA PRA Category 1 Credit(s)"
    award_matches = re.findall(
        r'(?i)is awarded\s+(\d+(?:\.\d+)?)\s+(?:AMA PRA)?\s*Category\s*\d+\s*Credit\(s\)?',
        text
    )

    # ✅ Match "Credits / Hours of Participation: | 1*" (with optional symbols)
    part_matches = re.findall(
        r'(?i)credits\s*/\s*hours\s+of\s+participation\s*[:|]*\s*[*]*\s*(\d+(?:\.\d+)?)',
        text
    )

    all_hours = [float(h) for h in award_matches + part_matches]
    hours = sum(all_hours)

    # ✅ Detect category
    category = "general"
    for key, label in CME_CATEGORIES:
        if re.search(key.replace("_", " "), text, re.IGNORECASE):
            category = key
            break
    if "risk management" in text.lower():
        category = "ethics"

    # ✅ Detect date
    date_match = re.search(r'(?i)(March \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})', text)
    try:
        if date_match:
            date_str = date_match.group(1)
            if ',' in date_str:
                date_completed = datetime.strptime(date_str, "%B %d, %Y").date()
            else:
                date_completed = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date_completed = datetime.today().date()
    except Exception:
        date_completed = datetime.today().date()

    return {
        'topic': topic,
        'hours': hours,
        'category': category,
        'text': text,
        'date_completed': date_completed
    }
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

import fitz  # PyMuPDF
import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', '', text)  # dates
    text = re.sub(r'page\s+\d+\s+(of\s+\d+)?', '', text)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '', text)  # phone numbers
    text = re.sub(r'(certificate\s?(id|number)?[:\s]*\d+)', '', text)
    return text

def extract_cme_hours(text):
    results = []
    patterns = [
        r'\b(\d+(\.\d{1,2})?)\s*(hr|hrs|hour|hours|credit|credits)\b',
        r'(?:cme|ce)[^\d]{0,10}(\d+(\.\d{1,2})?)',
        r'earned[^\d]{0,10}(\d+(\.\d{1,2})?)',
        r'\(\s*(\d+(\.\d{1,2})?)\s*\)\s*(hours?|credits?)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            try:
                value = float(match[0])
                if 0 < value < 100:
                    results.append(value)
            except ValueError:
                continue
    return results




import fitz  # PyMuPDF
import re
from datetime import datetime
import tempfile
import subprocess
import os

import fitz
import tempfile
import subprocess
import os
import re
from datetime import datetime

def parse_cme_pdf(file_bytes):
    try:
        # Save uploaded file to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in.flush()
            input_path = tmp_in.name

        # Output path
        output_fd, output_path = tempfile.mkstemp(suffix=".pdf")
        os.close(output_fd)

        # OCR the file
        import shutil

        ocr_cmd = shutil.which("ocrmypdf") or "/usr/local/bin/ocrmypdf"
        if not os.path.exists(ocr_cmd):
            raise FileNotFoundError(f"OCRmyPDF binary not found at {ocr_cmd}")
        print(f"[USING OCR COMMAND]: {ocr_cmd}")

        result = subprocess.run(
            [ocr_cmd, "--force-ocr", input_path, output_path],
            capture_output=True,
            text=True
        )



        if result.returncode != 0:
            print(f"[OCR ERROR] {result.stderr}")
            raise Exception("OCR failed")

        # Read OCR'd text
        doc = fitz.open(output_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()

        os.remove(input_path)
        os.remove(output_path)

        # ------------------
        # ------------------
        # Parse CME hours (strict, context-aware)
        hours = 0.0

        # Match phrases like "4.0 AMA PRA Category 1 Credit(s)" or "4 hours"
        matches = re.findall(
            r'(?<!\d)(\d{1,2}(?:\.\d+)?)\s+(AMA PRA\s+Category\s+1\s+Credits?|Credits?|Hours?|Hrs?)(?!\s*\d)',
            text,
            re.IGNORECASE
        )

        # Pick first reasonable match
        for match in matches:
            try:
                value = float(match[0])
                if 0.0 < value < 100:  # sanity check
                    hours = value
                    break
            except:
                continue



        # Parse date
        date_match = re.search(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
            text
        )
        if date_match:
            try:
                date_completed = datetime.strptime(date_match.group(), "%B %d, %Y").date()
            except:
                date_completed = datetime.today().date()
        else:
            date_completed = datetime.today().date()

        # Category guess
        if "AMA PRA Category 1" in text:
            category = "AMA Category 1"
        elif "opioid" in text.lower():
            category = "Opioid Training"
        else:
            category = "General"

        return {
            "topic": "Auto-parsed CME",
            "hours": hours or 0.0,
            "date_completed": date_completed,
            "category": category
        }

    except Exception as e:
        print(f"[ERROR in parse_cme_pdf]: {e}")
        return {
            "topic": "Auto-parsed CME",
            "hours": 0.0,
            "date_completed": datetime.today().date(),
            "category": "Unknown"
        }



import openai
import tempfile
import subprocess
import fitz  # PyMuPDF
import re
import json
import os
from datetime import datetime
from django.conf import settings


def parse_cme_pdf_ai(file_bytes):
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
            tmp_in.write(file_bytes)
            input_path = tmp_in.name

        # Prepare output OCR path
        output_fd, output_path = tempfile.mkstemp(suffix=".pdf")
        os.close(output_fd)

        import shutil

        ocr_cmd = shutil.which("ocrmypdf") or "/usr/local/bin/ocrmypdf"
        if not os.path.exists(ocr_cmd):
            raise FileNotFoundError(f"OCRmyPDF binary not found at {ocr_cmd}")
        print(f"[USING OCR COMMAND]: {ocr_cmd}")

        result = subprocess.run(
            [ocr_cmd, "--force-ocr", input_path, output_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"[OCR ERROR]: {result.stderr}")
            raise Exception("OCR failed")

        # Extract text from OCR'd PDF
        doc = fitz.open(output_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        os.remove(input_path)
        os.remove(output_path)

        if not text.strip():
            raise ValueError("Empty text extracted from PDF")

        # GPT prompt (enforce JSON)
        prompt = f"""
You are a medical compliance assistant. Given the text of a CME certificate, extract the following fields in valid JSON format:

{{
  "topic": string,
  "hours": number,
  "category": string,  // Must be one of the following exactly:
    "Opioid Education",
    "Ethics",
    "Bias and Harassment",
    "Controlled Substances",
    "Pain Management",
    "Suicide Prevention",
    "Child Abuse",
    "Public Health",
    "Medical Errors",
    "General"
    "Geriatrics/End of Life"
  "date_completed": "YYYY-MM-DD"
}}

Instructions:
- Carefully analyze the content of the certificate.
- Assign the most appropriate category from the list above. Use your best judgment.
- If none of the categories clearly apply, default to "General".
- Return only valid JSON with no extra explanation or formatting.

Certificate text:
{text}
"""

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract structured CME data from certificate text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        ai_output = response.choices[0].message.content.strip()
        ai_output = re.sub(r"^```(?:json)?\s*|```$", "", ai_output.strip(), flags=re.IGNORECASE)

        print(f"[AI RESPONSE]: {ai_output}")

        # Parse as JSON
        result = json.loads(ai_output)

        return {
            "topic": result.get("topic", "Auto-parsed CME"),
            "hours": float(result.get("hours", 0.0)),
            "date_completed": datetime.strptime(result.get("date_completed"), "%Y-%m-%d").date(),
            "category": result.get("category", "General")
        }

    except Exception as e:
        print("[AI Parse Failed]:", e)
        import traceback
        traceback.print_exc()  # <-- this will show the exact line that crashed
        return {
            "topic": "Auto-parsed CME",
            "hours": 0.0,
            "date_completed": datetime.today().date(),
            "category": "Unknown"
        }

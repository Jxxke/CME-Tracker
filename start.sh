#!/bin/bash
set -e

echo "OCRmyPDF path: $(which ocrmypdf)"
ocrmypdf --version

python manage.py migrate
gunicorn cme_tracker.wsgi:application --bind 0.0.0.0:10000 --timeout 120 --workers 1

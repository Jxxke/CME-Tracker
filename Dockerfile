FROM python:3.11-slim

# Install system dependencies including ocrmypdf via apt, NOT pip
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ghostscript \
    libjpeg-dev \
    libpng-dev \
    unpaper \
    qpdf \
    curl \
    ocrmypdf \
    && which ocrmypdf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD sh -c "python manage.py migrate && gunicorn cme_tracker.wsgi:application --bind 0.0.0.0:10000"

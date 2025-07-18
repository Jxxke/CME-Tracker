# Use official Python image
FROM python:3.11-slim

# Install system dependencies for ocrmypdf and general tools
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    ghostscript \
    tesseract-ocr \
    poppler-utils \
    qpdf \
    unpaper \
    ocrmypdf \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files (optional for Django)
RUN python manage.py collectstatic --noinput

# Run DB migrations
RUN python manage.py migrate

# Default start command
CMD ["gunicorn", "cme_tracker.wsgi:application", "--bind", "0.0.0.0:8000"]

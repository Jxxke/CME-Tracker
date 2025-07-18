# Base Python image with minimal OS
FROM python:3.11-slim

# Install system packages needed by ocrmypdf
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ghostscript \
    qpdf \
    libjpeg-dev \
    zlib1g-dev \
    ocrmypdf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy dependency file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Set environment variable for Django to find settings
ENV DJANGO_SETTINGS_MODULE=cme_tracker.settings

# Collect static files (optional if you use Django staticfiles)
RUN python manage.py collectstatic --noinput

# Expose the port for Render
ENV PORT=8000
EXPOSE 8000

# Start Gunicorn web server
CMD ["gunicorn", "cme_tracker.wsgi:application", "--bind", "0.0.0.0:8000"]

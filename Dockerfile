# Use an official Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ghostscript \
    libjpeg-dev \
    libpng-dev \
    unpaper \
    qpdf \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Force pip to install ocrmypdf system-wide and link it into a PATH directory
RUN pip install --no-cache-dir ocrmypdf && \
    ln -sf $(which ocrmypdf) /usr/bin/ocrmypdf

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install project dependencies
RUN pip install -r requirements.txt

# Set env vars
ENV PYTHONUNBUFFERED=1

# Run migrations and start app
CMD sh -c "python manage.py migrate && gunicorn cme_tracker.wsgi:application --bind 0.0.0.0:10000"

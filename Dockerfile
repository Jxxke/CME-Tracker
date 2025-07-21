# Use an official Python base image
FROM python:3.11-slim

# Install OS-level dependencies (for ocrmypdf + Tesseract + Ghostscript)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ghostscript \
    libjpeg-dev \
    libpng-dev \
    unpaper \
    qpdf \
    curl \
    && pip install --upgrade pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ocrmypdf
RUN pip install ocrmypdf
ENV PATH="/root/.local/bin:$PATH"


# Set work directory
WORKDIR /app

# Copy code
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run migrations and start app (fixed line)
CMD sh -c "python manage.py migrate && gunicorn cme_tracker.wsgi:application --bind 0.0.0.0:10000"

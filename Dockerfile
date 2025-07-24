FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ocrmypdf \
    tesseract-ocr \
    ghostscript \
    qpdf \
    unpaper \
    libjpeg-dev \
    libpng-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Log where ocrmypdf is installed
RUN which ocrmypdf && ocrmypdf --version

CMD ["gunicorn", "cme_tracker.wsgi:application", "--bind", "0.0.0.0:10000"]

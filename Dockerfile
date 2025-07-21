FROM python:3.11-slim

# Install ocrmypdf and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ghostscript \
    libjpeg-dev \
    libpng-dev \
    unpaper \
    qpdf \
    curl \
    ocrmypdf \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Ensure the PATH is correctly set (important for subprocess and shutil.which)
ENV PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Debugging: ensure ocrmypdf is actually present and log its location
RUN which ocrmypdf && ocrmypdf --version

# ENTRYPOINT preserves the environment correctly
ENTRYPOINT ["bash", "-c"]
CMD ["python manage.py migrate && gunicorn cme_tracker.wsgi:application --bind 0.0.0.0:10000"]

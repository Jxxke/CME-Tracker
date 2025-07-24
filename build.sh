#!/usr/bin/env bash
apt-get update && apt-get install -y \
  ocrmypdf \
  tesseract-ocr \
  ghostscript \
  libjpeg-dev \
  libpng-dev \
  qpdf \
  unpaper

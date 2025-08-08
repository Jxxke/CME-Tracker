#!/usr/bin/env bash

apt-get update && apt-get install -y \
  ocrmypdf \
  tesseract-ocr \
  poppler-utils \
  ghostscript \
  libjpeg-dev \
  libpng-dev \
  qpdf \
  unpaper

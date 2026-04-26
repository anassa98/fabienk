FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=upa_backend.settings

# Native deps for django.contrib.gis and pyogrio:
#   gdal-bin / libgdal-dev — GDAL/OGR
#   libgeos-dev            — GEOS (geometry ops)
#   libproj-dev / proj-bin — PROJ (reprojection)
#   binutils               — required by gdal-bin postinst
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev libgeos-dev libproj-dev proj-bin proj-data \
    binutils build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collect static for whitenoise (admin assets).
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Render sets $PORT. Default to 8000 locally.
CMD ["sh", "-c", "gunicorn upa_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120"]

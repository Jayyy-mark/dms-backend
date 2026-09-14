# ================================
# Base image
# ================================
FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# ================================
# System dependencies
# ================================
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# ================================
# Python dependencies
# ================================
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ================================
# Copy application
# ================================
COPY . .

# ================================
# Collect static files
# ================================
RUN python manage.py collectstatic --noinput

# ================================
# Expose application port
# ================================
EXPOSE 8000

# ================================
# Run Django with Gunicorn
# ================================
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "config.wsgi:application"]
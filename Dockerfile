# Use Python 3.11 slim as the base image for production
FROM python:3.11-slim

# Set environment variables for production
# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required by Django and PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files to the container
COPY . /app/

# Create a non-root user for improved security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create static files directory and set permissions
RUN mkdir -p /app/staticfiles && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Collect static files for production
RUN python manage.py collectstatic --noinput

# Expose port 8000 for the Django application
EXPOSE 8000

# Run the Django app in production using gunicorn
# Replace 'letsgetcrypto_django' with the actual Django project folder name containing settings.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "letsgetcrypto_django.wsgi:application"]
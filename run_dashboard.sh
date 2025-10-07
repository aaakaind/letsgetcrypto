#!/bin/bash
# Script to start the LetsGetCrypto web dashboard

echo "=========================================="
echo "LetsGetCrypto - Web Dashboard"
echo "=========================================="
echo ""

# Set debug mode for development
export DJANGO_DEBUG=true

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import django" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Django not found. Installing dependencies..."
    pip install -q Django dj-database-url
fi

# Run migrations if needed
echo "Running database migrations..."
python3 manage.py migrate --no-input

# Start the server
echo ""
echo "Starting Django development server..."
echo ""
echo "Dashboard will be available at:"
echo "  http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 manage.py runserver 0.0.0.0:8000

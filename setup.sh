#!/bin/bash

# LetsGetCrypto Setup Script
# This script sets up the complete environment for running the application from a fresh GitHub clone

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
cat << "EOF"
  _          _       ____       _    ____                  _        
 | |    __ _| |_ ___/ ___| ___ | |_ / ___|_ __ _   _ _ __ | |_ ___  
 | |   / _` | __/ __| |  _ / _ \| __| |   | '__| | | | '_ \| __/ _ \ 
 | |__| (_| | |_\__ \ |_| | (_) | |_| |___| |  | |_| | |_) | || (_) |
 |_____\__,_|\__|___/\____|\___/ \__|\____|_|   \__, | .__/ \__\___/ 
                                                 |___/|_|             
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 LetsGetCrypto Setup Script${NC}"
echo -e "${GREEN}==============================${NC}\n"

# Function to print step
print_step() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running from the repository root
if [ ! -f "manage.py" ] || [ ! -f "main.py" ]; then
    print_error "This script must be run from the repository root directory"
    exit 1
fi

# Step 1: Check Python version
print_step "Checking Python version..."
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python"
else
    print_error "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Step 2: Check if pip is installed
print_step "Checking pip installation..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip is not installed. Please install pip."
    exit 1
fi
print_success "pip is installed"

# Step 3: Ask about virtual environment
print_step "Setting up Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_success "Removed existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "Virtual environment activated"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    print_success "Virtual environment activated (Windows)"
else
    print_error "Could not find virtual environment activation script"
    exit 1
fi

# Step 4: Upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Step 5: Install dependencies
print_step "Installing Python dependencies (this may take several minutes)..."
echo -e "${YELLOW}Installing core dependencies...${NC}"

# Install dependencies one by one to handle potential failures
pip install -r requirements.txt

print_success "Dependencies installed"

# Step 6: Create necessary directories
print_step "Creating necessary directories..."
mkdir -p model_weights
mkdir -p data_cache
mkdir -p staticfiles
mkdir -p media
print_success "Directories created"

# Step 7: Setup environment file
print_step "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from .env.example"
        print_warning "Please edit .env file to add your API keys"
    else
        # Create a basic .env file
        cat > .env << 'ENVEOF'
# LetsGetCrypto Environment Configuration
# Add your API keys here (optional but recommended for full functionality)

# Anthropic Claude API Key (optional - for AI-powered insights)
# Get your key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=

# Django Settings
DJANGO_SECRET_KEY=django-insecure-$(openssl rand -base64 32 | tr -d '/+=' | head -c 50)
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
# DATABASE_URL=

# CoinGecko API (optional - uses free tier by default)
# COINGECKO_API_KEY=
ENVEOF
        print_success ".env file created with defaults"
    fi
else
    print_success ".env file already exists"
fi

# Step 8: Run Django migrations
print_step "Running database migrations..."
python manage.py migrate --noinput
print_success "Database migrations completed"

# Step 9: Collect static files
print_step "Collecting static files..."
python manage.py collectstatic --noinput --clear > /dev/null 2>&1 || true
print_success "Static files collected"

# Step 10: Ask about initial ML model training
print_step "Machine Learning Environment Setup..."
read -p "Do you want to train initial ML models now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Training initial models (this may take 5-10 minutes)..."
    if [ -f "init_ml_environment.sh" ]; then
        bash init_ml_environment.sh
    else
        print_warning "ML initialization script not found. You can train models later from the GUI."
    fi
else
    print_warning "Skipping ML model training. You can train models later from the GUI or run: ./init_ml_environment.sh"
fi

# Final instructions
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "1. Activate the virtual environment (if not already active):"
echo -e "   ${YELLOW}source venv/bin/activate${NC}  # Linux/Mac"
echo -e "   ${YELLOW}venv\\Scripts\\activate${NC}     # Windows"
echo ""
echo -e "2. (Optional) Edit .env file to add API keys:"
echo -e "   ${YELLOW}nano .env${NC}  # or use your preferred editor"
echo ""
echo -e "3. Start the application:"
echo ""
echo -e "   ${BLUE}Option A - Web Dashboard (Recommended):${NC}"
echo -e "   ${YELLOW}python manage.py runserver${NC}"
echo -e "   Then open: ${YELLOW}http://localhost:8000/${NC}"
echo ""
echo -e "   ${BLUE}Option B - Desktop GUI:${NC}"
echo -e "   ${YELLOW}python main.py${NC}"
echo ""
echo -e "   ${BLUE}Option C - Quick Start Script:${NC}"
echo -e "   ${YELLOW}./quick-start.sh${NC}"
echo ""
echo -e "4. To deploy GitHub Pages frontend:"
echo -e "   See ${YELLOW}GITHUB_PAGES.md${NC} for instructions"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  - Full User Guide: ${YELLOW}README_APP.md${NC}"
echo -e "  - Web Dashboard: ${YELLOW}DASHBOARD_GUIDE.md${NC}"
echo -e "  - ML Training: ${YELLOW}FEEDBACK_LOOP.md${NC}"
echo -e "  - Deployment: ${YELLOW}DEPLOYMENT_GUIDE.md${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  Important: This is educational software. See risk disclaimers in documentation.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

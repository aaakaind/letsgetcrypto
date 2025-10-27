#!/bin/bash

# LetsGetCrypto Deployment Validation Script
# This script validates that the deployment is ready for production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo "🚀 LetsGetCrypto Deployment Validation"
echo "======================================="
echo ""

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

# Function to print failure
print_failure() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# Function to check environment variable
check_env_var() {
    local var_name=$1
    local required=${2:-false}
    
    if [ -z "${!var_name}" ]; then
        if [ "$required" = true ]; then
            print_failure "$var_name is not set (REQUIRED)"
        else
            print_warning "$var_name is not set (optional)"
        fi
        return 1
    else
        print_success "$var_name is set"
        return 0
    fi
}

# Function to check if command exists
check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_failure "$1 is not installed"
        return 1
    fi
}

# ============================================================================
# 1. Environment Variables Check
# ============================================================================
echo "📋 Checking Environment Variables..."
echo "-----------------------------------"

check_env_var "DJANGO_SECRET_KEY" true
check_env_var "DJANGO_DEBUG" true
check_env_var "DJANGO_ALLOWED_HOSTS" true
check_env_var "DATABASE_URL" false

# Check DEBUG is False
if [ "${DJANGO_DEBUG,,}" = "false" ]; then
    print_success "DJANGO_DEBUG is False (production mode)"
elif [ "${DJANGO_DEBUG,,}" = "true" ]; then
    print_failure "DJANGO_DEBUG is True (NEVER use in production!)"
else
    print_warning "DJANGO_DEBUG value is unclear: $DJANGO_DEBUG"
fi

# Check SECRET_KEY strength
if [ ! -z "$DJANGO_SECRET_KEY" ]; then
    KEY_LENGTH=${#DJANGO_SECRET_KEY}
    if [ $KEY_LENGTH -ge 50 ]; then
        print_success "SECRET_KEY length is adequate ($KEY_LENGTH characters)"
    else
        print_failure "SECRET_KEY is too short ($KEY_LENGTH characters, should be 50+)"
    fi
fi

echo ""

# ============================================================================
# 2. Required Tools Check
# ============================================================================
echo "🔧 Checking Required Tools..."
echo "-----------------------------"

check_command "python3"
check_command "docker"
check_command "git"

echo ""

# ============================================================================
# 3. Python Dependencies Check
# ============================================================================
echo "📦 Checking Python Dependencies..."
echo "----------------------------------"

if [ -f "requirements.txt" ]; then
    print_success "requirements.txt found"
    
    # Try to check if key packages are importable
    if python3 -c "import django" 2>/dev/null; then
        print_success "Django is installed"
    else
        print_failure "Django is not installed"
    fi
    
    if python3 -c "import requests" 2>/dev/null; then
        print_success "requests is installed"
    else
        print_failure "requests is not installed"
    fi
else
    print_failure "requirements.txt not found"
fi

echo ""

# ============================================================================
# 4. Django Configuration Check
# ============================================================================
echo "⚙️  Checking Django Configuration..."
echo "------------------------------------"

if [ -f "manage.py" ]; then
    print_success "manage.py found"
    
    # Check Django settings
    if python3 manage.py check --deploy 2>&1 | grep -q "System check identified no issues"; then
        print_success "Django deployment checks passed"
    else
        print_warning "Django deployment checks found issues (run: python manage.py check --deploy)"
    fi
else
    print_failure "manage.py not found"
fi

echo ""

# ============================================================================
# 5. Docker Configuration Check
# ============================================================================
echo "🐳 Checking Docker Configuration..."
echo "-----------------------------------"

if [ -f "Dockerfile" ]; then
    print_success "Dockerfile found"
    
    # Check if Docker image can be built
    if docker build -t letsgetcrypto:validation-test . >/dev/null 2>&1; then
        print_success "Docker image builds successfully"
        # Clean up test image
        docker rmi letsgetcrypto:validation-test >/dev/null 2>&1 || true
    else
        print_failure "Docker image build failed"
    fi
else
    print_failure "Dockerfile not found"
fi

if [ -f "docker-compose.yml" ]; then
    print_success "docker-compose.yml found"
else
    print_warning "docker-compose.yml not found (optional)"
fi

echo ""

# ============================================================================
# 6. AWS Deployment Files Check
# ============================================================================
echo "☁️  Checking AWS Deployment Files..."
echo "------------------------------------"

if [ -d "aws" ]; then
    print_success "aws/ directory found"
    
    if [ -f "aws/cloudformation-template.yaml" ]; then
        print_success "CloudFormation template found"
    else
        print_failure "CloudFormation template not found"
    fi
    
    if [ -f "aws/ecs-task-definition.json" ]; then
        print_success "ECS task definition found"
    else
        print_failure "ECS task definition not found"
    fi
else
    print_warning "aws/ directory not found (only needed for AWS deployment)"
fi

if [ -f "deploy-aws.sh" ]; then
    print_success "deploy-aws.sh script found"
    if [ -x "deploy-aws.sh" ]; then
        print_success "deploy-aws.sh is executable"
    else
        print_warning "deploy-aws.sh is not executable (run: chmod +x deploy-aws.sh)"
    fi
else
    print_warning "deploy-aws.sh not found"
fi

echo ""

# ============================================================================
# 7. Security Files Check
# ============================================================================
echo "🔒 Checking Security Configuration..."
echo "-------------------------------------"

if [ -f ".gitignore" ]; then
    print_success ".gitignore found"
    
    # Check if .env is in gitignore
    if grep -q "^\.env$" .gitignore; then
        print_success ".env is in .gitignore"
    else
        print_failure ".env is NOT in .gitignore (security risk!)"
    fi
else
    print_failure ".gitignore not found"
fi

# Check if .env file exists (it shouldn't in repo)
if [ -f ".env" ]; then
    print_warning ".env file exists (should not be committed to repo)"
else
    print_success ".env file not in repository (good)"
fi

echo ""

# ============================================================================
# 8. Documentation Check
# ============================================================================
echo "📚 Checking Documentation..."
echo "---------------------------"

if [ -f "README.md" ]; then
    print_success "README.md found"
else
    print_failure "README.md not found"
fi

if [ -f "AWS_DEPLOYMENT.md" ]; then
    print_success "AWS_DEPLOYMENT.md found"
else
    print_warning "AWS_DEPLOYMENT.md not found"
fi

if [ -f "RELEASE_CHECKLIST.md" ]; then
    print_success "RELEASE_CHECKLIST.md found"
else
    print_warning "RELEASE_CHECKLIST.md not found"
fi

echo ""

# ============================================================================
# 9. Version Information
# ============================================================================
echo "📌 Version Information..."
echo "------------------------"

if [ -f "VERSION" ]; then
    VERSION=$(cat VERSION)
    print_success "VERSION file found: v$VERSION"
else
    print_warning "VERSION file not found"
fi

echo ""

# ============================================================================
# 10. Test Suite Check
# ============================================================================
echo "🧪 Checking Test Suite..."
echo "-------------------------"

if [ -f "test_all.py" ]; then
    print_success "test_all.py found"
else
    print_warning "test_all.py not found"
fi

if [ -f "test_integration.py" ]; then
    print_success "test_integration.py found"
else
    print_warning "test_integration.py not found"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "======================================="
echo "📊 Validation Summary"
echo "======================================="
echo -e "${GREEN}Passed:  $PASSED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Failed:  $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ All checks passed! Ready for deployment.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  All critical checks passed, but there are warnings.${NC}"
        echo -e "${YELLOW}Review warnings before deploying to production.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Validation failed! Fix the issues before deploying.${NC}"
    exit 1
fi

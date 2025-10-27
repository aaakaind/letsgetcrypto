#!/bin/bash

# Quick Start Deployment Script
# This script helps you quickly deploy LetsGetCrypto

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

echo -e "${GREEN}🚀 Quick Start Deployment Script${NC}"
echo -e "${GREEN}=================================${NC}\n"

# Get version
VERSION=$(cat VERSION 2>/dev/null || echo "1.0.0")
echo -e "Version: ${BLUE}${VERSION}${NC}\n"

# Function to print section header
print_section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Function to prompt user
prompt_choice() {
    echo -e "${YELLOW}$1${NC}"
    read -p "> " choice
    echo "$choice"
}

# Main menu
print_section "Choose Your Deployment Method"

echo "1) 🐳 Docker Compose (Local Development)"
echo "   → Fast, easy, runs locally"
echo "   → Best for: Development, testing"
echo "   → Time: 5 minutes"
echo ""
echo "2) ☁️  AWS Elastic Beanstalk (Simple Cloud)"
echo "   → Easy cloud deployment"
echo "   → Best for: Small production apps"
echo "   → Time: 10 minutes | Cost: ~\$30-50/month"
echo ""
echo "3) 🚀 AWS ECS Fargate (Production Cloud)"
echo "   → Full production deployment"
echo "   → Best for: Production, scalability"
echo "   → Time: 15 minutes | Cost: ~\$50-100/month"
echo ""
echo "4) 📄 GitHub Pages (Static Dashboard)"
echo "   → Free static hosting"
echo "   → Best for: Demo, documentation"
echo "   → Time: 5 minutes | Cost: Free"
echo ""
echo "5) 🧪 Validate Deployment (Run Checks)"
echo "   → Check if ready for deployment"
echo ""
echo "6) 📚 View Documentation"
echo "   → Read deployment guides"
echo ""

choice=$(prompt_choice "Enter your choice (1-6):")

case $choice in
    1)
        print_section "🐳 Docker Compose Deployment"
        
        echo "Step 1: Configure environment"
        if [ ! -f .env ]; then
            echo "Creating .env file..."
            cp .env.example .env 2>/dev/null || cp .env.production.template .env
            echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
            read -p "Press Enter after editing .env..."
        else
            echo "✅ .env file exists"
        fi
        
        echo ""
        echo "Step 2: Starting Docker Compose..."
        docker-compose up -d
        
        echo ""
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo ""
        echo "Access your application:"
        echo "  Dashboard: http://localhost:8000/api/dashboard/"
        echo "  Health Check: http://localhost:8000/api/health/"
        echo "  API: http://localhost:8000/api/"
        echo ""
        echo "View logs: docker-compose logs -f"
        echo "Stop: docker-compose down"
        ;;
        
    2)
        print_section "☁️  AWS Elastic Beanstalk Deployment"
        
        echo "Step 1: Create deployment package"
        ./package-for-aws.sh $VERSION
        
        echo ""
        echo "Step 2: Upload to AWS"
        echo ""
        echo -e "${GREEN}Package created in: aws-packages/${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Go to AWS Elastic Beanstalk Console"
        echo "   https://console.aws.amazon.com/elasticbeanstalk"
        echo "2. Click 'Create Application'"
        echo "3. Upload: aws-packages/letsgetcrypto-beanstalk-*.zip"
        echo "4. Platform: Python 3.11"
        echo "5. Configure environment variables (see .env.production.template)"
        echo "6. Click 'Create Environment'"
        echo ""
        echo "See DEPLOYMENT_GUIDE.md for detailed instructions"
        ;;
        
    3)
        print_section "🚀 AWS ECS Fargate Deployment"
        
        echo "Prerequisites check..."
        if ! command -v aws &> /dev/null; then
            echo -e "${YELLOW}⚠️  AWS CLI not found. Please install it first.${NC}"
            exit 1
        fi
        
        if ! command -v docker &> /dev/null; then
            echo -e "${YELLOW}⚠️  Docker not found. Please install it first.${NC}"
            exit 1
        fi
        
        echo "✅ AWS CLI and Docker found"
        echo ""
        
        run_validation=$(prompt_choice "Run validation checks first? (y/n)")
        if [[ $run_validation == "y" ]]; then
            ./validate-deployment.sh
        fi
        
        echo ""
        echo "Starting AWS deployment..."
        ./deploy-aws.sh
        
        echo ""
        echo -e "${GREEN}✅ Check AWS console for deployment status${NC}"
        ;;
        
    4)
        print_section "📄 GitHub Pages Deployment"
        
        echo "GitHub Pages setup:"
        echo ""
        echo "1. Go to your repository settings"
        echo "2. Navigate to: Settings → Pages"
        echo "3. Source: Deploy from branch"
        echo "4. Branch: main"
        echo "5. Folder: /docs"
        echo "6. Save"
        echo ""
        echo "Your dashboard will be available at:"
        echo "https://yourusername.github.io/letsgetcrypto/"
        echo ""
        echo "See GITHUB_PAGES.md for detailed instructions"
        ;;
        
    5)
        print_section "🧪 Validation Checks"
        
        echo "Running validation script..."
        echo ""
        ./validate-deployment.sh
        
        echo ""
        echo "Running pre-deployment tests..."
        echo ""
        python3 test-deployment.py
        
        echo ""
        echo "Review RELEASE_CHECKLIST.md for complete checklist:"
        echo "  cat RELEASE_CHECKLIST.md"
        ;;
        
    6)
        print_section "📚 Documentation"
        
        echo "Available documentation:"
        echo ""
        echo "🚀 DEPLOYMENT_GUIDE.md - Complete deployment guide"
        echo "✅ RELEASE_CHECKLIST.md - Pre-deployment checklist"
        echo "📦 QUICK_DEPLOY.md - Quick deployment guide"
        echo "☁️  AWS_DEPLOYMENT.md - AWS deployment details"
        echo "🔄 CICD_GUIDE.md - CI/CD pipeline setup"
        echo "📄 GITHUB_PAGES.md - GitHub Pages setup"
        echo "📖 README.md - Project overview"
        echo ""
        echo "Open with: cat DEPLOYMENT_GUIDE.md"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Need help? See DEPLOYMENT_GUIDE.md${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

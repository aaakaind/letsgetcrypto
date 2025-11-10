#!/bin/bash

# LetsGetCrypto - One Command Run Script
# Starts the complete application stack

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

echo -e "${GREEN}🚀 Starting LetsGetCrypto...${NC}\n"

# Check if setup has been run
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo -e "${YELLOW}   Running setup first...${NC}\n"
    ./setup.sh
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo -e "${YELLOW}⚠️  Could not activate virtual environment${NC}"
    echo -e "${YELLOW}   Please run: ./setup.sh${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo -e "${YELLOW}   Creating from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
    fi
fi

# Ask which interface to start
echo -e "${BLUE}Choose interface:${NC}"
echo -e "1) 🌐 Web Dashboard (http://localhost:8000)"
echo -e "2) 🖥️  Desktop GUI"
echo -e "3) 📊 Both (Web + Desktop)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting Web Dashboard...${NC}"
        echo -e "${BLUE}Access at: http://localhost:8000${NC}\n"
        python manage.py runserver
        ;;
    2)
        echo -e "\n${GREEN}Starting Desktop GUI...${NC}\n"
        python main.py
        ;;
    3)
        echo -e "\n${GREEN}Starting both interfaces...${NC}"
        echo -e "${BLUE}Web: http://localhost:8000${NC}"
        echo -e "${BLUE}Desktop: Will open in separate window${NC}\n"
        
        # Start web server in background
        python manage.py runserver &
        WEB_PID=$!
        
        # Wait a moment for server to start
        sleep 2
        
        # Start desktop GUI
        python main.py
        
        # When GUI closes, stop web server
        kill $WEB_PID 2>/dev/null || true
        ;;
    *)
        echo -e "${YELLOW}Invalid choice${NC}"
        exit 1
        ;;
esac

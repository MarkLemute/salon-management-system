#!/bin/bash
# Salon MS Setup Script for Linux/Mac
# Run this script from the project root directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}\n========================================"
echo "  SALON MS - PROJECT SETUP"
echo -e "========================================\n${NC}"

# 1. Check Python
echo -e "${YELLOW}[1/6] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found. Install Python 3.8+ from python.org${NC}"
    exit 1
fi
PY_VERSION=$(python3 --version)
echo -e "${GREEN}    Found: $PY_VERSION${NC}"

# 2. Create venv
echo -e "${YELLOW}\n[2/6] Setting up virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}    Virtual environment already exists${NC}"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}    Created venv/${NC}"
fi

# 3. Install packages
echo -e "${YELLOW}\n[3/6] Installing Python packages...${NC}"
echo -e "    This may take a few minutes..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Package installation failed${NC}"
    exit 1
fi
echo -e "${GREEN}    Django, MySQL client, and REST framework installed${NC}"

# 4. Setup .env
echo -e "${YELLOW}\n[4/6] Configuring environment...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}    .env already exists${NC}"
else
    cp .env.example .env
    echo -e "${GREEN}    Created .env file${NC}"
    echo -e "${CYAN}    ACTION REQUIRED: Edit .env with your MySQL password!${NC}"
fi

# 5. Database check
echo -e "${YELLOW}\n[5/6] Database setup...${NC}"
if grep -q "DB_PASSWORD=your_password_here" .env || grep -q "DB_PASSWORD=$" .env; then
    echo -e "${RED}    WARNING: Database password not configured in .env${NC}"
    echo -e "${YELLOW}    Open .env and set DB_PASSWORD before running migrations${NC}"
else
    echo -e "${GREEN}    Database credentials configured${NC}"
fi

# 6. Next steps
echo -e "${GREEN}\n[6/6] Setup complete!${NC}"
echo -e "${CYAN}\n========================================"
echo "  NEXT STEPS"
echo -e "========================================\n${NC}"

echo -e "${NC}1. Edit .env with your MySQL credentials:"
echo -e "   ${CYAN}nano .env${NC}\n"

echo -e "2. Create MySQL database:"
echo -e "   ${CYAN}mysql -u root -p"
echo -e "   CREATE DATABASE salon_db;${NC}\n"

echo -e "3. Activate virtual environment:"
echo -e "   ${CYAN}source venv/bin/activate${NC}\n"

echo -e "4. Run Django migrations:"
echo -e "   ${CYAN}python manage.py makemigrations"
echo -e "   python manage.py migrate${NC}\n"

echo -e "5. Create admin user:"
echo -e "   ${CYAN}python manage.py createsuperuser${NC}\n"

echo -e "6. Start the server:"
echo -e "   ${CYAN}python manage.py runserver${NC}\n"

echo -e "${CYAN}========================================\n${NC}"

# Offer to activate venv
read -p "Activate virtual environment now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}Activating venv... Run 'deactivate' to exit venv${NC}\n"
    exec bash --init-file <(echo ". venv/bin/activate")
fi

#!/bin/bash
# Camoro - Setup Script for Termux & Linux
# Author: Camoro Team

clear

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${RED}"
echo "   ▄████████  ▄████████    ▄▄▄▄███▄▄▄▄   ▄██████▄   ████████▄     ▄████████ "
echo "  ███    ███ ███    ███  ▄██▀▀▀███▀▀▀██▄ ███    ███  ███   ▀███   ███    ███ "
echo "  ███    █▀  ███    ███  ███   ███   ███ ███    ███  ███    ███   ███    █▀  "
echo "  ███        ███    ███  ███   ███   ███ ███    ███  ███    ███  ▄███▄▄▄     "
echo "  ███        ███    ███  ███   ███   ███ ███    ███  ███    ███ ▀▀███▀▀▀     "
echo "  ███    █▄  ███    ███  ███   ███   ███ ███    ███  ███    ███   ███    █▄  "
echo "  ███    ███ ███    ███  ███   ███   ███ ███    ███  ███   ▄███   ███    ███ "
echo "  ████████▀  ████████▀    ▀█   ███   █▀   ▀██████▀   ████████▀    ██████████ "
echo -e "${NC}"
echo -e "${YELLOW}[*] Installing Camoro Dependencies...${NC}"
echo ""

# Detect environment
if [ -d "/data/data/com.termux" ]; then
    echo -e "${CYAN}[+] Termux detected${NC}"
    pkg update -y && pkg upgrade -y
    pkg install python python-pip git curl wget -y
    pip install --upgrade pip
else
    echo -e "${CYAN}[+] Linux detected${NC}"
    sudo apt-get update -y
    sudo apt-get install python3 python3-pip git curl -y
    pip3 install --upgrade pip
fi

echo ""
echo -e "${YELLOW}[*] Installing Python packages...${NC}"
pip install -r requirements.txt

echo ""
echo -e "${GREEN}[+] Installation completed successfully!${NC}"
echo -e "${GREEN}[+] Run: python camoro.py${NC}"

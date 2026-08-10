#!/bin/bash

echo -ne "\033]0;Installing Packages from Pip Freeze\007"
cd "$(dirname "$0")"

echo "Upgrading pip first..."
python3 -m pip install --upgrade pip

echo ""
echo "Installing libraries from your pip freeze file..."
pip3 install -r requirements.txt

echo ""

if [ $? -eq 0 ]; then
    echo "[SUCCESS] All libraries installed perfectly!"
else
    echo "[ERROR] Something went wrong during installation. Check the messages above."
fi

echo ""
read -p "Press Enter to continue..."

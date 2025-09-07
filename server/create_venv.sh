#!/bin/bash
# This script creates a virtual environment for the project.
# It checks if the virtual environment already exists, and if not, it creates one.
# It also installs the required packages from requirements.txt.
# Usage: ./create_venv.sh

# Check if the virtual environment directory exists
if [ ! -d "../venv" ]; then
    python3 -m venv ../venv
fi

# Activate the virtual environment
source ../venv/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install the required packages from requirements.txt
pip install -r requirements.txt

# Deactivate the virtual environment
deactivate
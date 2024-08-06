#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Install Python 3.10 or 3.11
apt-get update
apt-get install -y python3.11 python3-pip

# Verify Python installation
if ! command -v python3 &> /dev/null
then
    echo "Python 3.10 or 3.11 could not be found"
    exit 1
fi

# Install portaudio19-dev and python-all-dev
apt-get install -y portaudio19-dev python-all-dev

# Install Python dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "Setup completed successfully."

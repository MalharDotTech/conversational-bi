#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Install portaudio19-dev and python-all-dev
sudo apt-get install -y portaudio19-dev python-all-dev

# Install Python dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "Setup completed successfully."

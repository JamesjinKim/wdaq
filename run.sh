#!/bin/bash
# ADS8668 ADC Monitor - Run script with virtual environment

# Activate virtual environment
source venv/bin/activate

# Run the application
python3 main.py

# Deactivate when done (only if not terminated)
deactivate 2>/dev/null || true

#!/bin/bash
# Wrapper script to generate QR code with virtual environment

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the Python script
python3 generate_qr.py "$@"


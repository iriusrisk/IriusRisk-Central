#!/bin/bash

# IriusRisk V1/V2 Migration Tool - Streamlit App Launcher
# This script sets up and runs the Streamlit web interface

echo "🌅 IriusRisk V1/V2 Migration Tool"
echo "=================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install requirements if needed
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Run Streamlit app
echo "🚀 Starting Streamlit application..."
echo "📱 The app will open in your default browser at http://localhost:8501"
echo ""

streamlit run app.py
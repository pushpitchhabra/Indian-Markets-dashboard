#!/bin/bash

# Pre-Market Dashboard Startup Script
# This script activates the virtual environment and runs the Streamlit dashboard
# with all required dependencies properly installed.

echo "🚀 Starting Pre-Market Dashboard..."
echo "📦 Activating virtual environment..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python3 -c "
import pandas, yfinance, ta, streamlit, plotly
print('✅ All dependencies are available!')
print('📊 pandas:', pandas.__version__)
print('📈 yfinance: Available')
print('📉 ta: Available')
print('🌐 streamlit:', streamlit.__version__)
"

echo "🌅 Launching Pre-Market Technical Analysis Dashboard..."
echo "📱 Dashboard will open at: http://localhost:8501"
echo "🔧 Use Ctrl+C to stop the dashboard"
echo ""

# Run Streamlit dashboard
streamlit run indian_stock_market_dashboard_main.py

echo "👋 Dashboard stopped."

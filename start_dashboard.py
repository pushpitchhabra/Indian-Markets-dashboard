#!/usr/bin/env python3
"""
Dashboard Startup Script
========================
Quick startup script for the optimized Indian Stock Market Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = [
        'streamlit', 'yfinance', 'pandas', 'numpy', 
        'plotly', 'ta', 'kiteconnect'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are installed!")
    return True

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("🚀 Starting Indian Stock Market Dashboard...")
    print("📊 Features: Market Indices, Pre-Market Analysis, F&O Analytics, Technical Analysis")
    print("⚡ Optimized: Fast data loading with intelligent caching")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "="*60)
    
    # Change to the correct directory
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "indian_stock_market_dashboard_main.py",
            "--server.port=8501",
            "--server.headless=false",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    print("🎯 Indian Stock Market Dashboard - Startup Script")
    print("=" * 50)
    
    if check_requirements():
        start_dashboard()
    else:
        print("\n❌ Cannot start dashboard due to missing requirements.")
        sys.exit(1)

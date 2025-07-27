#!/usr/bin/env python3
"""
Setup script for Indian Stock Market Dashboard
This script helps users set up the project environment quickly.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Output: {e.output}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip is not available. Please install pip first.")
        return False
    
    # Install requirements
    return run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages")

def create_virtual_environment():
    """Create a virtual environment."""
    if os.path.exists("venv") or os.path.exists(".venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")

def setup_git_repository():
    """Initialize Git repository if not already done."""
    if os.path.exists(".git"):
        print("✅ Git repository already initialized")
        return True
    
    commands = [
        ("git init", "Initializing Git repository"),
        ("git add .", "Adding files to Git"),
        ("git commit -m 'Initial commit: Indian Stock Market Dashboard'", "Creating initial commit")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Indian Stock Market Dashboard")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment (optional)
    print("\n📁 Setting up virtual environment...")
    create_virtual_environment()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check the error messages above.")
        sys.exit(1)
    
    # Setup Git repository
    print("\n📚 Setting up Git repository...")
    setup_git_repository()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Get your Zerodha API credentials from https://developers.kite.trade/")
    print("2. Run the dashboard:")
    print("   python start_dashboard.py")
    print("   OR")
    print("   streamlit run indian_stock_market_dashboard_main.py")
    print("\n📖 For detailed instructions, see README.md")
    print("🔗 For troubleshooting, check the troubleshooting section in README.md")

if __name__ == "__main__":
    main()

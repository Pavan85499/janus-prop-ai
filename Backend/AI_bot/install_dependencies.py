#!/usr/bin/env python3
"""
Quick dependency installer for Janus Prop AI Backend
Run this script to install all required dependencies
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running '{command}': {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Installing Janus Prop AI Backend Dependencies...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found!")
        print("Please run this script from the Backend/AI_bot directory")
        return False
    
    # Upgrade pip first
    print("\n📦 Upgrading pip...")
    if not run_command(f"{sys.executable} -m pip install --upgrade pip"):
        print("⚠️  Warning: Failed to upgrade pip, continuing...")
    
    # Install core dependencies
    print("\n🔧 Installing core dependencies...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        print("❌ Failed to install from requirements.txt")
        return False
    
    # Install specific packages that might be missing
    print("\n🔑 Installing specific API packages...")
    specific_packages = [
        "google-generativeai",
        "langchain-google-genai",
        "httpx",
        "structlog"
    ]
    
    for package in specific_packages:
        if not run_command(f"{sys.executable} -m pip install {package}"):
            print(f"⚠️  Warning: Failed to install {package}")
    
    print("\n" + "=" * 50)
    print("🎉 Dependency installation completed!")
    print("\n📋 Next steps:")
    print("1. Create a .env file with your API keys")
    print("2. Run: python api_server.py")
    print("\n🔑 Required API keys:")
    print("- GEMINI_API_KEY (from Google AI Studio)")
    print("- ATTOM_API_KEY (from ATTOM Data Solutions)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ All done! You can now start the backend server.")

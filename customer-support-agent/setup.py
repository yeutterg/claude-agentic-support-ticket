#!/usr/bin/env python3
"""
Setup script for Customer Support Agent System
"""

import os
import shutil
import subprocess
import sys


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")


def setup_environment():
    """Set up the .env file"""
    env_example = ".env.example"
    env_file = ".env"
    
    if not os.path.exists(env_example):
        print(f"Error: {env_example} not found")
        return False
    
    if os.path.exists(env_file):
        response = input(f"{env_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print(f"✓ Keeping existing {env_file}")
            return True
    
    shutil.copy(env_example, env_file)
    print(f"✓ Created {env_file} from {env_example}")
    print(f"Please edit {env_file} and add your ANTHROPIC_API_KEY")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def generate_sample_data():
    """Generate sample data for testing"""
    print("Generating sample data...")
    try:
        subprocess.check_call([sys.executable, "utils/simple_data_generator.py"])
        print("✓ Sample data generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating sample data: {e}")
        return False


def main():
    print("Customer Support Agent System - Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Set up environment file
    if not setup_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\nSetup failed. Please install dependencies manually:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Generate sample data
    if not generate_sample_data():
        print("\nWarning: Could not generate sample data")
        print("You can generate it manually with:")
        print("python utils/simple_data_generator.py")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your ANTHROPIC_API_KEY")
    print("2. Run the demo: python main.py")
    print("3. Try examples: python example_usage.py")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
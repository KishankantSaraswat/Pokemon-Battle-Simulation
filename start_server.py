#!/usr/bin/env python3
"""
Startup script for Pokemon Battle MCP Server
Handles environment setup and server launch with proper error handling.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'flask-cors', 'requests', 
        'cachetools', 'pydantic', 'typing-extensions'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'server.py',
        'pokemon_resource.py', 
        'battle_simulator.py'
    ]
    
    missing_files = []
    current_dir = Path(__file__).parent
    
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 Pokemon Battle MCP Server Startup")
    print("="*50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        return 1
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check required files
    print("📁 Checking required files...")
    if not check_files():
        return 1
    print("✅ All required files present")
    
    # Check requirements
    print("📦 Checking dependencies...")
    if not check_requirements():
        print("\n🔧 To install requirements:")
        print("   pip install -r requirements.txt")
        return 1
    print("✅ All dependencies satisfied")
    
    # Start server
    print("\n🌟 Starting MCP Server...")
    print("   Server URL: http://localhost:8080")
    print("   MCP Info: http://localhost:8080/mcp/info")
    print("   Press Ctrl+C to stop")
    print("="*50)
    
    try:
        # Change to script directory
        os.chdir(Path(__file__).parent)
        
        # Start the server
        subprocess.run([sys.executable, "server.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        return 0
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

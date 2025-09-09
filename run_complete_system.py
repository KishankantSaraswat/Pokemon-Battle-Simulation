#!/usr/bin/env python3
"""
Complete Pokemon Battle System Startup Script
Starts MCP server and Streamlit frontend together
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
import requests

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def start_mcp_server():
    """Start the MCP server"""
    print("🚀 Starting MCP Server...")
    server_process = subprocess.Popen([
        sys.executable, "server.py"
    ], cwd=Path(__file__).parent)
    
    # Wait for server to start
    for i in range(10):
        try:
            response = requests.get("http://localhost:8080/mcp/info", timeout=2)
            if response.status_code == 200:
                print("✅ MCP Server started successfully!")
                return server_process
        except:
            pass
        time.sleep(1)
    
    print("❌ MCP Server failed to start")
    return server_process

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎮 Starting Streamlit Frontend...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py", 
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ], cwd=Path(__file__).parent / "frontend")
    
    return frontend_process

def main():
    """Main startup function"""
    print("🎤 Pokemon Battle System - Complete Startup")
    print("="*50)
    
    processes = []
    
    try:
        # Check if ports are available
        if check_port(8080):
            print("⚠️  Port 8080 is already in use (MCP Server)")
            choice = input("Continue anyway? (y/n): ")
            if choice.lower() != 'y':
                return
        
        if check_port(8501):
            print("⚠️  Port 8501 is already in use (Streamlit)")
            choice = input("Continue anyway? (y/n): ")
            if choice.lower() != 'y':
                return
        
        # Start MCP server
        mcp_process = start_mcp_server()
        processes.append(mcp_process)
        
        # Wait a bit for server to fully initialize
        time.sleep(2)
        
        # Start frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        print("\n🎉 System Started Successfully!")
        print("="*50)
        print("📡 MCP Server: http://localhost:8080")
        print("🎮 Frontend:   http://localhost:8501")
        print("="*50)
        print("\n🎤 **Voice Commands Available!**")
        print("Try saying: 'Battle Pikachu against Charizard'")
        print("\nPress Ctrl+C to stop all services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"❌ Process {proc.pid} has stopped")
    
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Pokemon Battle System...")
        
        # Terminate all processes
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        
        print("✅ All services stopped")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Cleanup
        for proc in processes:
            try:
                proc.terminate()
            except:
                pass

if __name__ == "__main__":
    main()

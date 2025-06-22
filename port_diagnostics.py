#!/usr/bin/env python3
"""
Voyager Port Diagnostics Tool
This script helps diagnose port conflicts and Mineflayer startup issues.
"""

import subprocess
import sys
import time
import psutil

def check_port_usage(port):
    """Check if a port is in use and what processes are using it."""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Port {port} is in use by processes: {pids}")
            
            # Get process details
            for pid in pids:
                try:
                    process = psutil.Process(int(pid))
                    print(f"  PID {pid}: {process.name()} - {' '.join(process.cmdline())}")
                except (psutil.NoSuchProcess, ValueError):
                    print(f"  PID {pid}: Process not found or invalid")
            return True
        else:
            print(f"Port {port} is free")
            return False
    except Exception as e:
        print(f"Error checking port {port}: {e}")
        return False

def kill_port_processes(port):
    """Kill processes using a specific port."""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Killing processes on port {port}: {pids}")
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid], check=True)
                    print(f"Killed process {pid}")
                except Exception as e:
                    print(f"Failed to kill process {pid}: {e}")
            return True
        else:
            print(f"No processes found on port {port}")
            return False
    except Exception as e:
        print(f"Error killing processes on port {port}: {e}")
        return False

def main():
    port = 3000
    print("=== Voyager Port Diagnostics ===")
    print(f"Checking port {port}...")
    
    if check_port_usage(port):
        response = input(f"Port {port} is in use. Kill processes? (y/N): ")
        if response.lower() == 'y':
            kill_port_processes(port)
            time.sleep(1)
            print("After cleanup:")
            check_port_usage(port)
    
    print("\n=== Node.js processes ===")
    # Check for any node processes
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and 'node' in proc.info['name'].lower():
                print(f"PID {proc.info['pid']}: {' '.join(proc.info['cmdline'] or [])}")
    except Exception as e:
        print(f"Error listing node processes: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Voyager Recovery Tool
This script helps recover from common Voyager issues and restart cleanly.
"""

import os
import sys
import time
import subprocess
import psutil
import json

# Add voyager to path
sys.path.insert(0, '/Users/dmitry/Developer/Voyager')
import voyager.utils as U

def kill_mineflayer_processes():
    """Kill all Mineflayer-related processes."""
    killed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info['cmdline'] or []
            cmdline_str = ' '.join(cmdline)
            
            # Check for mineflayer processes
            if ('mineflayer/index.js' in cmdline_str or 
                'bridge.js' in cmdline_str or
                (proc.info['name'] == 'node' and '3000' in cmdline_str)):
                try:
                    print(f"Killing process {proc.info['pid']}: {cmdline_str}")
                    proc.kill()
                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"Could not kill process {proc.info['pid']}: {e}")
    except Exception as e:
        print(f"Error scanning processes: {e}")
    
    if killed_count > 0:
        print(f"Killed {killed_count} processes")
        time.sleep(2)  # Allow processes to clean up
    else:
        print("No Mineflayer processes found")
    
    return killed_count

def check_data_consistency():
    """Check for data consistency issues."""
    print("=== Checking Data Consistency ===")
    
    # Check vectordb vs qa_cache sync
    vectordb_path = "/Users/dmitry/Developer/Voyager/ckpt/curriculum/vectordb"
    qa_cache_path = "/Users/dmitry/Developer/Voyager/ckpt/curriculum/qa_cache.json"
    
    try:
        if os.path.exists(vectordb_path) and os.path.exists(qa_cache_path):
            # Count vectordb entries (rough approximation)
            vectordb_files = []
            for root, dirs, files in os.walk(vectordb_path):
                vectordb_files.extend(files)
            vectordb_count = len([f for f in vectordb_files if not f.startswith('.')])
            
            # Count qa_cache entries
            with open(qa_cache_path, 'r') as f:
                qa_cache = json.load(f)
                qa_cache_count = len(qa_cache)
            
            print(f"VectorDB files: {vectordb_count}")
            print(f"QA Cache entries: {qa_cache_count}")
            
            if abs(vectordb_count - qa_cache_count) > 10:  # Allow some variance
                print("⚠️  Potential vectordb/qa_cache sync issue detected")
                return False
            else:
                print("✓ VectorDB and QA cache appear synchronized")
                return True
        else:
            print("Missing vectordb or qa_cache files")
            return True  # Not an error if files don't exist yet
    except Exception as e:
        print(f"Error checking data consistency: {e}")
        return True  # Don't fail on consistency check errors

def cleanup_logs():
    """Clean up old log files to prevent disk space issues."""
    print("=== Cleaning Old Logs ===")
    
    log_dirs = [
        "/Users/dmitry/Developer/Voyager/logs/mineflayer",
        "/Users/dmitry/Developer/Voyager/logs/minecraft"
    ]
    
    for log_dir in log_dirs:
        if not os.path.exists(log_dir):
            continue
            
        try:
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            log_files.sort(reverse=True)  # Newest first
            
            # Keep only the 10 most recent log files
            to_delete = log_files[10:]
            
            for log_file in to_delete:
                log_path = os.path.join(log_dir, log_file)
                os.remove(log_path)
                print(f"Deleted old log: {log_file}")
                
            if to_delete:
                print(f"Cleaned {len(to_delete)} old log files from {log_dir}")
            else:
                print(f"No old logs to clean in {log_dir}")
                
        except Exception as e:
            print(f"Error cleaning logs in {log_dir}: {e}")

def main():
    print("=== Voyager Recovery Tool ===")
    
    # Step 1: Kill existing processes
    print("\n1. Killing existing Mineflayer processes...")
    kill_mineflayer_processes() 
    
    # Step 2: Check port availability
    print("\n2. Checking port 3000...")
    try:
        result = subprocess.run(['lsof', '-ti', ':3000'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("Port 3000 still in use, attempting to free...")
            subprocess.run(['kill', '-9'] + result.stdout.strip().split('\n'), 
                         capture_output=True)
            time.sleep(1)
        
        # Check again
        result = subprocess.run(['lsof', '-ti', ':3000'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  Warning: Port 3000 is still in use")
        else:
            print("✓ Port 3000 is now free")
    except Exception as e:
        print(f"Error checking port: {e}")
    
    # Step 3: Check data consistency
    print("\n3. Checking data consistency...")
    check_data_consistency()
    
    # Step 4: Clean old logs
    print("\n4. Cleaning old logs...")
    cleanup_logs()
    
    print("\n=== Recovery Complete ===")
    print("You can now safely restart Voyager.")

if __name__ == "__main__":
    main()

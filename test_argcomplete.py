#!/usr/bin/env python3
"""Test script to verify argcomplete functionality."""

import os
import subprocess
import sys

def main():
    """Test argcomplete functionality for vl command."""
    print("Testing argcomplete functionality for vl command...")
    
    # Set up environment variables for argcomplete testing
    env = os.environ.copy()
    env["_ARGCOMPLETE"] = "1"
    env["_ARGCOMPLETE_SHELL"] = "bash"
    env["COMP_LINE"] = "vl -s "
    env["COMP_POINT"] = "5"
    
    # Run the vl command with argcomplete environment variables
    try:
        result = subprocess.run(
            ["vl"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Completion results for 'vl -s ':")
        if result.stdout:
            print(f"stdout: {result.stdout}")
        else:
            print("No completion results found in stdout")
            
        if result.stderr:
            print(f"stderr: {result.stderr}")
            
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
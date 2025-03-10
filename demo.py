#!/usr/bin/env python3
"""Demo script for the VL CSV viewer."""

import os
import sys
from vl.formatter import view_csv

def main():
    """Run a demonstration of the VL CSV viewer."""
    # Get the path to the sample data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file = os.path.join(script_dir, 'sample_data.csv')
    
    if not os.path.exists(sample_file):
        print(f"Error: Sample data file not found at {sample_file}")
        return 1
    
    print(f"Viewing sample CSV file: {sample_file}")
    print("="*60)
    
    # Start the CSV viewer with different styles
    print("\nDEMO 1: Default grid style")
    print("="*60)
    view_csv(
        file_path=sample_file,
        delimiter=',',
        header=True,
        min_col_width=5,
        max_col_width=20,
        border_style='grid'
    )
    
    print("\n\nDEMO 2: Simple style with larger max column width")
    print("="*60)
    view_csv(
        file_path=sample_file,
        delimiter=',',
        header=True,
        min_col_width=5,
        max_col_width=30,
        border_style='simple'
    )
    
    print("\n\nDEMO 3: Minimal style without header")
    print("="*60)
    view_csv(
        file_path=sample_file,
        delimiter=',',
        header=False,
        min_col_width=5,
        max_col_width=15,
        border_style='minimal'
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
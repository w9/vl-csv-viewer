#!/usr/bin/env python3
"""Demo script showing the color column mode for the VL CSV viewer."""

import os
import sys
from vl.formatter import view_csv

def main():
    """Run a demonstration of the VL CSV viewer with colored columns."""
    # Get the path to the test fixture
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(script_dir, 'tests')
    fixtures_dir = os.path.join(tests_dir, 'fixtures')
    small_csv = os.path.join(fixtures_dir, 'small.csv')
    large_csv = os.path.join(fixtures_dir, 'large.csv')
    
    if not os.path.exists(small_csv) or not os.path.exists(large_csv):
        print(f"Error: Test fixture files not found")
        return 1
    
    print("\nDemo 1: Small CSV with alternating cyan/white background colors")
    print("="*60)
    view_csv(
        file_path=small_csv,
        delimiter=',',
        header=True,
        border_style='simple',
        use_colors=True,
        column_colors=['bg_cyan', 'bg_white']
    )
    
    print("\nDemo 2: Small CSV with alternating text colors")
    print("="*60)
    view_csv(
        file_path=small_csv,
        delimiter=',',
        header=True,
        border_style='grid',
        use_colors=True,
        column_colors=['red', 'green', 'blue', 'yellow']
    )
    
    print("\nDemo 3: Large CSV with alternating background colors")
    print("="*60)
    view_csv(
        file_path=large_csv,
        delimiter=',',
        header=True,
        border_style='simple',
        use_colors=True,
        column_colors=['bg_green', 'bg_white', 'bg_yellow']
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
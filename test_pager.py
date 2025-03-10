#!/usr/bin/env python3
"""Test script for the VLL pager command."""

import os
import sys
from vl.pager import main

if __name__ == "__main__":
    # Pass through any command line arguments
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
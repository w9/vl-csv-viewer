#!/bin/bash

# Source the completion scripts
eval "$(register-python-argcomplete vl)"
eval "$(register-python-argcomplete vll)"

# Test the completion by showing available options
echo "Testing vl command completion..."
echo "Available options for vl command:"
vl --help

echo -e "\nAvailable styles for -s/--style option:"
echo "simple, grid, minimal, none"

echo -e "\nAvailable colors for --color-list option:"
echo "black, red, green, yellow, blue, magenta, cyan, white"
echo "bg_black, bg_red, bg_green, bg_yellow, bg_blue, bg_magenta, bg_cyan, bg_white"

echo -e "\nShell completion is now enabled for vl and vll commands in this shell."
echo "To enable it permanently, add the following to your ~/.bashrc or ~/.zshrc:"
echo 'eval "$(register-python-argcomplete vl)"'
echo 'eval "$(register-python-argcomplete vll)"'
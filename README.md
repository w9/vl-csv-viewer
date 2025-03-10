# VL - View Large

An ultrafast CSV viewer in terminals. VL (View Large) is designed to handle very large CSV files efficiently by reading them line-by-line and rendering output immediately.

## Features

- **Streaming processing**: Reads CSV files line-by-line for ultrafast performance with large files
- **Adaptive column sizing**: Automatically calculates optimal column widths based on content
- **Minimal memory usage**: Designed to handle files of any size without loading them entirely into memory
- **Multiple border styles**: Choose from different table border styles (grid, simple, minimal, none)
- **Customizable display**: Control header behavior, column widths, and more

## Installation

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install from the current directory
pip install -e .

# Or install directly
pip install .
```

## Usage

Basic usage:

```bash
# View a CSV file
vl data.csv

# Specify a different delimiter
vl -d ';' data.csv

# Don't treat the first row as a header
vl --no-header data.csv
```

### Display Options

```bash
# Use grid-style borders (default)
vl -s grid data.csv

# Use simple ASCII borders
vl -s simple data.csv

# Use minimal borders (only horizontal lines)
vl -s minimal data.csv

# No borders
vl -s none data.csv

# Set minimum column width
vl --min-width 10 data.csv

# Set maximum column width
vl --max-width 30 data.csv
```

## Performance

VL is optimized for performance with large CSV files:

1. It processes files line-by-line rather than loading the entire file into memory
2. It calculates initial column widths based on a preview of rows
3. Long cell content is truncated with ellipses when exceeding max width
4. Output is displayed immediately as data is processed

This makes VL suitable for working with CSV files of any size, even multi-gigabyte files that would be impractical to load into memory all at once.

## API Usage

You can also use VL programmatically in your Python scripts:

```python
from vl.formatter import view_csv

# View a CSV file with custom settings
view_csv(
    file_path='data.csv',
    delimiter=',',
    header=True,
    min_col_width=5,
    max_col_width=20,
    border_style='grid'
)

# You can also use the CSVViewer class directly for more control
from vl.formatter import CSVViewer

viewer = CSVViewer(
    delimiter=',',
    header=True,
    min_col_width=5,
    max_col_width=20,
    border_style='grid'
)
viewer.view_csv('data.csv')
```

## License

MIT
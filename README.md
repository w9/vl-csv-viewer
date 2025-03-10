# VL - View Large

An ultrafast CSV viewer in terminals. VL (View Large) is designed to handle very large CSV files efficiently by reading them line-by-line and rendering output immediately.

## Features

- **Streaming processing**: Reads CSV files line-by-line for ultrafast performance with large files
- **Adaptive column sizing**: Automatically calculates optimal column widths based on content
- **Minimal memory usage**: Designed to handle files of any size without loading them entirely into memory
- **Multiple border styles**: Choose from different table border styles (grid, simple, minimal, none)
- **Colored columns**: Display CSV data with alternating column colors for better readability
- **Customizable display**: Control header behavior, column widths, colors, and more

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

# Enable colored columns
vl --colors data.csv

# Use custom colors (comma-separated list)
vl --colors --color-list red,green,blue,yellow data.csv

# Combine with border style
vl --colors --color-list bg_cyan,bg_white -s grid data.csv
```

Available colors:
- Text colors: black, red, green, yellow, blue, magenta, cyan, white
- Background colors: bg_black, bg_red, bg_green, bg_yellow, bg_blue, bg_magenta, bg_cyan, bg_white

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
    border_style='grid',
    use_colors=False,  # Set to True to enable colored columns
    column_colors=['bg_cyan', 'bg_white']  # Custom colors (optional)
)

# You can also use the CSVViewer class directly for more control
from vl.formatter import CSVViewer

viewer = CSVViewer(
    delimiter=',',
    header=True,
    min_col_width=5,
    max_col_width=20,
    border_style='grid',
    use_colors=True,  # Enable colored columns
    column_colors=['red', 'green', 'blue']  # Custom colors
)
viewer.view_csv('data.csv')
```

## Testing

The VL package includes a comprehensive test suite to ensure code quality and correctness.

### Running Tests

You can run the tests using Python's unittest framework:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_formatter.py

# Run specific test case
python -m unittest tests.test_formatter.TestCSVViewer
```

Alternatively, if you have pytest installed:

```bash
# Install pytest and coverage
pip install pytest pytest-cov

# Run tests with coverage report
pytest --cov=vl

# Generate HTML coverage report
pytest --cov=vl --cov-report=html
```

### Test Organization

- `tests/fixtures/` - Contains test data files
- `tests/test_formatter.py` - Tests for the formatter module
- `tests/test_cli.py` - Tests for the command-line interface

## License

MIT
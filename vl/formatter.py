"""Core functionality for formatting CSV data as tables with streaming processing."""

import csv
import os
import shutil
import sys
from typing import List, Optional, Dict, Tuple, Iterator


class CSVViewer:
    """
    CSV viewer that processes files line-by-line for efficient handling of large files.
    Uses direct printing for output, making it compatible with all terminal environments.
    """

    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bg_black': '\033[40m',
        'bg_red': '\033[41m',
        'bg_green': '\033[42m',
        'bg_yellow': '\033[43m',
        'bg_blue': '\033[44m',
        'bg_magenta': '\033[45m',
        'bg_cyan': '\033[46m',
        'bg_white': '\033[47m',
    }
    
    # Default colors for the alternating columns mode
    DEFAULT_COLUMN_COLORS = ['bg_cyan', 'bg_white']

    def __init__(
        self,
        delimiter: str = ',',
        header: bool = True,
        min_col_width: int = 5,
        max_col_width: Optional[int] = None,
        border_style: str = 'simple',
        output_stream = None,
        use_colors: bool = False,
        column_colors: Optional[List[str]] = None,
    ):
        """
        Initialize the CSV viewer.

        Args:
            delimiter: The CSV delimiter character
            header: Whether the first row should be treated as a header
            min_col_width: Minimum width for columns
            max_col_width: Maximum width for any column (None for unlimited)
            border_style: Table border style ('simple', 'grid', 'minimal', 'none')
            output_stream: Stream to write output to (defaults to sys.stdout)
            use_colors: Whether to use alternating colors for columns
            column_colors: List of color names for alternating columns when use_colors is True
        """
        self.delimiter = delimiter
        self.header = header
        self.min_col_width = min_col_width
        self.max_col_width = max_col_width
        self.border_style = border_style
        self.output_stream = output_stream or sys.stdout
        self.term_height, self.term_width = self._get_terminal_size()
        
        # Color settings
        self.use_colors = use_colors
        self.column_colors = column_colors or self.DEFAULT_COLUMN_COLORS
        
        # Border characters for different styles
        self.border_chars = self._get_border_chars()

    def _get_terminal_size(self) -> Tuple[int, int]:
        """Get the current terminal size."""
        try:
            height, width = shutil.get_terminal_size()
            return height, width
        except Exception:
            # Fallback to reasonable defaults if we can't get terminal size
            return 24, 80

    def _get_border_chars(self) -> Dict[str, Dict[str, str]]:
        """Get the border characters based on the selected style."""
        styles = {
            'simple': {
                'h': '-', 'v': '|', 'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
                'lc': '+', 'rc': '+', 'tc': '+', 'bc': '+', 'c': '+'
            },
            'grid': {
                'h': '─', 'v': '│', 'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
                'lc': '├', 'rc': '┤', 'tc': '┬', 'bc': '┴', 'c': '┼'
            },
            'minimal': {
                'h': '─', 'v': ' ', 'tl': ' ', 'tr': ' ', 'bl': ' ', 'br': ' ',
                'lc': ' ', 'rc': ' ', 'tc': ' ', 'bc': ' ', 'c': ' '
            },
            'none': {
                'h': ' ', 'v': ' ', 'tl': ' ', 'tr': ' ', 'bl': ' ', 'br': ' ',
                'lc': ' ', 'rc': ' ', 'tc': ' ', 'bc': ' ', 'c': ' '
            }
        }
        return styles.get(self.border_style, styles['simple'])

    def _csv_reader(self, file_input) -> Iterator[List[str]]:
        """
        Create a CSV reader that processes the file line by line.
        
        Args:
            file_input: Path to the CSV file or a file-like object (e.g., stdin)
            
        Yields:
            Each row of the CSV file as a list of strings
        """
        # If file_input is a string, it's a file path
        if isinstance(file_input, str):
            with open(file_input, 'r', newline='') as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                for row in reader:
                    yield row
        # Otherwise treat it as a file-like object (e.g., stdin)
        else:
            reader = csv.reader(file_input, delimiter=self.delimiter)
            for row in reader:
                yield row

    def _calculate_initial_col_widths(self, reader: Iterator[List[str]], num_preview_rows: int = 100) -> List[int]:
        """
        Calculate column widths based on the first num_preview_rows.
        
        This allows us to start displaying data with reasonable column widths
        without reading the entire file.
        
        Args:
            reader: CSV reader iterator
            num_preview_rows: Number of rows to use for initial width calculation
            
        Returns:
            List of column widths
        """
        col_widths = []
        rows_buffer = []
        
        # Process rows for preview
        for i, row in enumerate(reader):
            if i >= num_preview_rows:
                break
                
            rows_buffer.append(row)
            
            # Update column widths based on this row
            for j, cell in enumerate(row):
                cell_str = str(cell)
                if j >= len(col_widths):
                    col_widths.append(len(cell_str))
                else:
                    col_widths[j] = max(col_widths[j], len(cell_str))
        
        # Apply min/max column width constraints
        col_widths = [max(self.min_col_width, w) for w in col_widths]
        if self.max_col_width:
            col_widths = [min(w, self.max_col_width) for w in col_widths]
            
        return col_widths, rows_buffer

    def _truncate_cell(self, cell: str, width: int) -> str:
        """Truncate a cell to the specified width if needed."""
        if not width or len(cell) <= width:
            return cell
        return cell[:width - 3] + '...'

    def _get_color(self, col_index: int) -> str:
        """Get the color code for a given column index."""
        if not self.use_colors:
            return ""
        
        # Use round-robin color selection from the user-defined array
        color_name = self.column_colors[col_index % len(self.column_colors)]
        return self.COLORS.get(color_name, "")

    def _format_row(self, row: List[str], col_widths: List[int]) -> str:
        """Format a single row of data for display."""
        border_chars = self.border_chars
        cells = []
        
        # Ensure we don't process more columns than we have widths for
        # This prevents inconsistent line lengths when rows have different numbers of columns
        process_cols = min(len(row), len(col_widths))
        
        for i in range(process_cols):
            cell = str(row[i])
            width = col_widths[i]
            
            # First truncate if needed (this ensures all cells in a column have the same effective width)
            if self.max_col_width and len(cell) > self.max_col_width:
                cell = self._truncate_cell(cell, self.max_col_width)
            
            # Ensure the cell is exactly the width specified in col_widths
            if self.use_colors:
                # Apply color to the cell
                color_code = self._get_color(i)
                formatted_cell = f"{color_code} {cell:<{width}} {self.COLORS['reset']}"
                cells.append(formatted_cell)
            else:
                # Standard formatting without colors
                cells.append(f" {cell:<{width}} ")
        
        # Add empty cells if row has fewer columns than col_widths
        for i in range(process_cols, len(col_widths)):
            if self.use_colors:
                color_code = self._get_color(i)
                formatted_cell = f"{color_code} {'':<{col_widths[i]}} {self.COLORS['reset']}"
                cells.append(formatted_cell)
            else:
                cells.append(f" {'':<{col_widths[i]}} ")
        
        # Join cells with vertical border character
        return border_chars['v'] + border_chars['v'].join(cells) + border_chars['v']

    def _format_separator(self, col_widths: List[int], position: str) -> str:
        """Format a horizontal separator line for the table."""
        if self.border_style == 'none':
            return ''
            
        border_chars = self.border_chars
        parts = []
        
        for width in col_widths:
            parts.append(border_chars['h'] * (width + 2))  # +2 for padding
        
        if position == 'top':
            return border_chars['tl'] + border_chars['tc'].join(parts) + border_chars['tr']
        elif position == 'middle':
            return border_chars['lc'] + border_chars['c'].join(parts) + border_chars['rc']
        elif position == 'bottom':
            return border_chars['bl'] + border_chars['bc'].join(parts) + border_chars['br']
        else:
            return ''

    def view_csv(self, file_input) -> None:
        """
        View a CSV file in the terminal.
        
        Args:
            file_input: Path to the CSV file or a file-like object (e.g., stdin)
        """
        reader = self._csv_reader(file_input)

        # Calculate initial column widths from preview rows
        col_widths, preview_rows = self._calculate_initial_col_widths(reader)

        # Print top border
        if self.border_style != 'none':
            top_border = self._format_separator(col_widths, 'top')
            print(top_border, file=self.output_stream)
        
        # Print header (if exists)
        if preview_rows and self.header:
            header_row = preview_rows[0]
            header_str = self._format_row(header_row, col_widths)
            print(header_str, file=self.output_stream)
            
            # Print header separator
            if self.border_style != 'none':
                separator = self._format_separator(col_widths, 'middle')
                print(separator, file=self.output_stream)
            
            # Start printing data rows from the second row
            start_idx = 1
        else:
            # No header, start from the first row
            start_idx = 0
        
        # Print preview rows
        for i in range(start_idx, len(preview_rows)):
            row_str = self._format_row(preview_rows[i], col_widths)
            print(row_str, file=self.output_stream)
        
        # Continue with the rest of the file
        row_count = len(preview_rows)
        for row in reader:
            row_str = self._format_row(row, col_widths)
            print(row_str, file=self.output_stream)
            row_count += 1
        
        # Print bottom border
        if self.border_style != 'none':
            bottom_border = self._format_separator(col_widths, 'bottom')
            print(bottom_border, file=self.output_stream)
            
        # Print summary
        print(f"\nTotal rows: {row_count}", file=self.output_stream)


def view_csv(
    file_path: Optional[str] = None,
    delimiter: str = ',',
    header: bool = True,
    min_col_width: int = 5,
    max_col_width: Optional[int] = None,
    border_style: str = 'simple',
    use_colors: bool = False,
    column_colors: Optional[List[str]] = None
) -> None:
    """
    View a CSV file in the terminal.
    
    Args:
        file_path: Path to the CSV file, '-' for stdin, or None for stdin
        delimiter: CSV delimiter character
        header: Whether to treat the first row as a header
        min_col_width: Minimum width for columns
        max_col_width: Maximum width for any column
        border_style: Table border style
        use_colors: Whether to use alternating colors for columns
        column_colors: List of color names for alternating columns
    """
    viewer = CSVViewer(
        delimiter=delimiter,
        header=header,
        min_col_width=min_col_width,
        max_col_width=max_col_width,
        border_style=border_style,
        use_colors=use_colors,
        column_colors=column_colors,
    )
    
    # Handle stdin when file_path is '-' or None
    if file_path is None or file_path == '-':
        viewer.view_csv(sys.stdin)
    else:
        viewer.view_csv(file_path)
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

    def __init__(
        self,
        delimiter: str = ',',
        header: bool = True,
        min_col_width: int = 5,
        max_col_width: Optional[int] = None,
        border_style: str = 'simple',
        output_stream = None,
    ):
        """
        Initialize the CSV viewer.

        Args:
            delimiter: The CSV delimiter character
            header: Whether the first row should be treated as a header
            min_col_width: Minimum width for columns
            max_col_width: Maximum width for any column (None for unlimited)
            border_style: Table border style ('simple', 'grid', 'minimal', or 'none')
            output_stream: Stream to write output to (defaults to sys.stdout)
        """
        self.delimiter = delimiter
        self.header = header
        self.min_col_width = min_col_width
        self.max_col_width = max_col_width
        self.border_style = border_style
        self.output_stream = output_stream or sys.stdout
        self.term_height, self.term_width = self._get_terminal_size()
        
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

    def _csv_reader(self, file_path: str) -> Iterator[List[str]]:
        """
        Create a CSV reader that processes the file line by line.
        
        Args:
            file_path: Path to the CSV file
            
        Yields:
            Each row of the CSV file as a list of strings
        """
        with open(file_path, 'r', newline='') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
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

    def _format_row(self, row: List[str], col_widths: List[int]) -> str:
        """Format a single row of data for display."""
        border_chars = self.border_chars
        cells = []
        
        for i, (cell, width) in enumerate(zip(row, col_widths)):
            cell_str = str(cell)
            if self.max_col_width:
                cell_str = self._truncate_cell(cell_str, self.max_col_width)
                
            cells.append(f" {cell_str:<{width}} ")
        
        # Add empty cells if row has fewer columns than col_widths
        for i in range(len(row), len(col_widths)):
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

    def _adjust_column_widths(self, col_widths: List[int]) -> List[int]:
        """
        Adjust column widths to fit within terminal width.
        If the total width exceeds terminal width, proportionally reduce widths.
        
        Args:
            col_widths: Original column widths
            
        Returns:
            Adjusted column widths
        """
        # Calculate total width including borders
        # Each column has its width + 2 spaces + 1 border character
        # Plus 1 more border character at the end
        total_width = sum(w + 3 for w in col_widths) + 1
        
        # If total width fits, return original widths
        if total_width <= self.term_width:
            return col_widths
            
        # Calculate how much we need to reduce
        excess = total_width - self.term_width
        
        # Reduce column widths proportionally
        # First, calculate total "reducible" width (excluding minimum widths)
        reducible_width = sum(max(0, w - self.min_col_width) for w in col_widths)
        
        # If reducible width is less than excess, we can't fit all columns
        # In that case, we'll just return minimal widths for as many columns as possible
        if reducible_width < excess:
            max_columns = (self.term_width - 1) // (self.min_col_width + 3)
            return [self.min_col_width] * max_columns
        
        # Calculate reduction factor
        reduction_factor = excess / reducible_width
        
        # Reduce each column proportionally
        adjusted_widths = []
        for w in col_widths:
            reducible = max(0, w - self.min_col_width)
            reduction = int(reducible * reduction_factor)
            adjusted_widths.append(max(self.min_col_width, w - reduction))
            
        return adjusted_widths

    def view_csv(self, file_path: str) -> None:
        """
        View a CSV file in the terminal.
        
        Args:
            file_path: Path to the CSV file
        """
        reader = self._csv_reader(file_path)
        
        # Calculate initial column widths from preview rows
        col_widths, preview_rows = self._calculate_initial_col_widths(reader)
        
        # Adjust column widths to fit terminal width
        col_widths = self._adjust_column_widths(col_widths)
        
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
    file_path: str,
    delimiter: str = ',',
    header: bool = True, 
    min_col_width: int = 5,
    max_col_width: Optional[int] = None,
    border_style: str = 'simple'
) -> None:
    """
    View a CSV file in the terminal.
    
    Args:
        file_path: Path to the CSV file
        delimiter: CSV delimiter character
        header: Whether to treat the first row as a header
        min_col_width: Minimum width for columns
        max_col_width: Maximum width for any column
        border_style: Table border style
    """
    viewer = CSVViewer(
        delimiter=delimiter,
        header=header,
        min_col_width=min_col_width,
        max_col_width=max_col_width,
        border_style=border_style,
    )
    viewer.view_csv(file_path)
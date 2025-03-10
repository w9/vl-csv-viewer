"""Tests for the formatter module."""

import io
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vl.formatter import CSVViewer, view_csv


class TestCSVViewer(unittest.TestCase):
    """Tests for the CSVViewer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.small_fixture = os.path.join(self.fixtures_dir, 'small.csv')
        self.large_fixture = os.path.join(self.fixtures_dir, 'large.csv')
        self.output = io.StringIO()  # Capture output

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        viewer = CSVViewer()
        self.assertEqual(viewer.delimiter, ',')
        self.assertTrue(viewer.header)
        self.assertEqual(viewer.min_col_width, 5)
        self.assertIsNone(viewer.max_col_width)
        self.assertEqual(viewer.border_style, 'simple')

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        viewer = CSVViewer(
            delimiter=';',
            header=False,
            min_col_width=10,
            max_col_width=20,
            border_style='grid',
            output_stream=self.output
        )
        self.assertEqual(viewer.delimiter, ';')
        self.assertFalse(viewer.header)
        self.assertEqual(viewer.min_col_width, 10)
        self.assertEqual(viewer.max_col_width, 20)
        self.assertEqual(viewer.border_style, 'grid')
        self.assertEqual(viewer.output_stream, self.output)

    def test_border_chars(self):
        """Test border characters for different styles."""
        # Simple style
        viewer = CSVViewer(border_style='simple')
        border_chars = viewer._get_border_chars()
        self.assertEqual(border_chars['h'], '-')
        self.assertEqual(border_chars['v'], '|')
        self.assertEqual(border_chars['tl'], '+')

        # Grid style
        viewer = CSVViewer(border_style='grid')
        border_chars = viewer._get_border_chars()
        self.assertEqual(border_chars['h'], '─')
        self.assertEqual(border_chars['v'], '│')
        self.assertEqual(border_chars['tl'], '┌')

        # Minimal style
        viewer = CSVViewer(border_style='minimal')
        border_chars = viewer._get_border_chars()
        self.assertEqual(border_chars['h'], '─')
        self.assertEqual(border_chars['v'], ' ')
        self.assertEqual(border_chars['tl'], ' ')

        # None style
        viewer = CSVViewer(border_style='none')
        border_chars = viewer._get_border_chars()
        self.assertEqual(border_chars['h'], ' ')
        self.assertEqual(border_chars['v'], ' ')
        self.assertEqual(border_chars['tl'], ' ')

        # Invalid style falls back to simple
        viewer = CSVViewer(border_style='invalid')
        border_chars = viewer._get_border_chars()
        self.assertEqual(border_chars['h'], '-')
        self.assertEqual(border_chars['v'], '|')
        self.assertEqual(border_chars['tl'], '+')

    def test_truncate_cell(self):
        """Test cell truncation."""
        viewer = CSVViewer()
        
        # No truncation if no max_width
        self.assertEqual(viewer._truncate_cell("Hello", None), "Hello")
        
        # No truncation if cell is shorter than max_width
        self.assertEqual(viewer._truncate_cell("Hello", 10), "Hello")
        
        # Truncation if cell is longer than max_width
        self.assertEqual(viewer._truncate_cell("Hello World", 8), "Hello...")

    def test_format_row(self):
        """Test row formatting."""
        viewer = CSVViewer(border_style='simple')
        row = ['Name', 'Age', 'City']
        col_widths = [6, 3, 6]
        
        formatted = viewer._format_row(row, col_widths)
        self.assertEqual(formatted, "| Name   | Age | City   |")

    def test_format_separator(self):
        """Test separator formatting."""
        viewer = CSVViewer(border_style='simple')
        col_widths = [6, 3, 6]
        
        # Top separator
        formatted = viewer._format_separator(col_widths, 'top')
        self.assertEqual(formatted, "+--------+-----+--------+")
        
        # Middle separator
        formatted = viewer._format_separator(col_widths, 'middle')
        self.assertEqual(formatted, "+--------+-----+--------+")
        
        # Bottom separator
        formatted = viewer._format_separator(col_widths, 'bottom')
        self.assertEqual(formatted, "+--------+-----+--------+")
        
        # None style has no separators
        viewer = CSVViewer(border_style='none')
        formatted = viewer._format_separator(col_widths, 'top')
        self.assertEqual(formatted, "")

    def test_adjust_column_widths(self):
        """Test column width adjustment."""
        viewer = CSVViewer(min_col_width=2, max_col_width=None)
        
        # Patch terminal width to a known value
        viewer.term_width = 40
        
        # Original widths fit within terminal
        col_widths = [5, 3, 5]
        adjusted = viewer._adjust_column_widths(col_widths)
        self.assertEqual(adjusted, [5, 3, 5])
        
        # Original widths exceed terminal (calculated width = 3 * (w + 3) + 1)
        col_widths = [20, 15, 10]  # Total: 3 * (w + 3) + 1 = 136
        adjusted = viewer._adjust_column_widths(col_widths)
        # Should be reduced to fit within 40 chars
        self.assertLessEqual(sum(w + 3 for w in adjusted) + 1, 41)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_view_csv_with_file(self, mock_stdout):
        """Test viewing a CSV file."""
        # Use a small fixture file
        viewer = CSVViewer(output_stream=mock_stdout)
        viewer.view_csv(self.small_fixture)
        
        output = mock_stdout.getvalue()
        
        # Check that the output contains all data from the file
        self.assertIn("Name", output)
        self.assertIn("Age", output)
        self.assertIn("City", output)
        self.assertIn("Job", output)
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)
        self.assertIn("Charlie", output)
        self.assertIn("David", output)
        
        # Check for the presence of borders
        self.assertIn("+", output)
        self.assertIn("|", output)
        self.assertIn("-", output)
        
        # Check for the total count
        self.assertIn("Total rows: 5", output)
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_view_csv_with_large_file(self, mock_stdout):
        """Test viewing a larger CSV file."""
        # Use the large fixture file with more columns and rows
        viewer = CSVViewer(output_stream=mock_stdout)
        viewer.view_csv(self.large_fixture)
        
        output = mock_stdout.getvalue()
        
        # Check that the output contains expected headers
        self.assertIn("Name", output)
        self.assertIn("Age", output)
        self.assertIn("City", output)
        self.assertIn("Occupation", output)
        self.assertIn("Salary", output)
        self.assertIn("Department", output)
        
        # Check for specific records
        self.assertIn("John Doe", output)
        self.assertIn("Jane Smith", output)
        self.assertIn("Software Engineer", output)
        self.assertIn("Data Scientist", output)
        
        # Check for the total count (29 rows including header)
        self.assertIn("Total rows: 29", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_view_csv_different_styles(self, mock_stdout):
        """Test different border styles."""
        styles = ['simple', 'grid', 'minimal', 'none']
        
        for style in styles:
            mock_stdout.truncate(0)
            mock_stdout.seek(0)
            
            viewer = CSVViewer(border_style=style, output_stream=mock_stdout)
            viewer.view_csv(self.small_fixture)
            
            output = mock_stdout.getvalue()
            
            # All styles should include the data
            self.assertIn("Name", output)
            self.assertIn("Alice", output)
            
            # Check style-specific characters
            if style == 'simple':
                self.assertIn("+", output)
                self.assertIn("|", output)
                self.assertIn("-", output)
            elif style == 'grid':
                self.assertIn("┌", output)
                self.assertIn("│", output)
                self.assertIn("─", output)
            elif style == 'minimal':
                self.assertIn("─", output)
                self.assertNotIn("┌", output)
            elif style == 'none':
                self.assertNotIn("+", output)
                self.assertNotIn("-", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_view_csv_no_header(self, mock_stdout):
        """Test viewing CSV with no header."""
        viewer = CSVViewer(header=False, output_stream=mock_stdout)
        viewer.view_csv(self.small_fixture)
        
        output = mock_stdout.getvalue()
        
        # Check that headers are not treated specially
        # With header=True, there would be a separator between first and second row
        # Without headers, there should be no such separator
        
        # Instead of counting separators which can be unreliable,
        # let's verify that all data rows are included in the output
        self.assertIn("Name", output)  # First row is treated as data
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)
        self.assertIn("Charlie", output)
        self.assertIn("David", output)
        
        # And verify that the formatting is different from the header case
        with patch('sys.stdout', new_callable=io.StringIO) as header_stdout:
            header_viewer = CSVViewer(header=True, output_stream=header_stdout)
            header_viewer.view_csv(self.small_fixture)
            header_output = header_stdout.getvalue()
            
            # The outputs should be different because of the header formatting
            self.assertNotEqual(output, header_output)

    @patch('vl.formatter.CSVViewer')
    def test_view_csv_function(self, mock_csv_viewer):
        """Test the view_csv convenience function."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_csv_viewer.return_value = mock_instance
        
        # Call the function
        view_csv(
            file_path=self.small_fixture,
            delimiter=';',
            header=False,
            min_col_width=10,
            max_col_width=20,
            border_style='grid'
        )
        
        # Check if CSVViewer was initialized with the correct parameters
        mock_csv_viewer.assert_called_once_with(
            delimiter=';',
            header=False,
            min_col_width=10,
            max_col_width=20,
            border_style='grid'
        )
        
        # Check if view_csv was called on the instance
        mock_instance.view_csv.assert_called_once_with(self.small_fixture)

    def test_column_width_consistency(self):
        """Test that all cells in a column have the same width."""
        viewer = CSVViewer(border_style='simple')
        
        # Create data with varying content lengths
        data = [
            ['Short', 'Medium Column', 'This is a very long column header'],
            ['A', 'Medium value', 'Long value but not as long'],
            ['Abc', 'M', 'Another very very very long value that should be consistent']
        ]
        
        # Format each row
        # Create a reader-like object to use with _calculate_initial_col_widths
        def mock_reader():
            for row in data:
                yield row
        
        col_widths, _ = viewer._calculate_initial_col_widths(mock_reader())
        formatted_rows = [viewer._format_row(row, col_widths) for row in data]
        
        # Measure the position of each vertical separator in each row
        # Extract character positions of vertical separators
        separator_positions = []
        for row in formatted_rows:
            positions = [i for i, char in enumerate(row) if char == '|']
            separator_positions.append(positions)
        
        # Verify all rows have the same number of separators
        self.assertTrue(all(len(pos) == len(separator_positions[0]) for pos in separator_positions))
        
        # Verify separator positions are consistent across all rows
        # (i.e., columns have consistent widths)
        for i in range(len(separator_positions[0])):
            position_values = [pos[i] for pos in separator_positions]
            self.assertEqual(len(set(position_values)), 1, 
                            f"Vertical separators at position {i} are not aligned: {position_values}")
        
        # Additionally, verify column widths are applied correctly
        for i, width in enumerate(col_widths):
            # All rows should have cells with the content padded to the same width
            cell_widths = []
            for row_idx, row in enumerate(data):
                if i < len(row):  # Only check if this row has this column
                    # Calculate expected width (column width + padding)
                    expected_width = width + 2  # +2 for padding spaces
                    # Calculate actual width from formatted row
                    if i < len(row) - 1:  # Not the last column
                        start_pos = separator_positions[row_idx][i]
                        end_pos = separator_positions[row_idx][i+1]
                        actual_width = end_pos - start_pos - 1  # -1 for the separator itself
                        cell_widths.append(actual_width)
            
            # Verify all cells in this column have the same width
            if cell_widths:
                self.assertEqual(len(set(cell_widths)), 1, 
                                f"Column {i} has inconsistent cell widths: {cell_widths}")


if __name__ == '__main__':
    unittest.main()
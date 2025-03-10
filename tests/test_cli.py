"""Tests for the CLI module."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vl.cli import parse_args, main


class TestCLI(unittest.TestCase):
    """Tests for the CLI module."""

    def setUp(self):
        """Set up test fixtures."""
        self.fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'small.csv')

    def test_parse_args_defaults(self):
        """Test argument parsing with default values."""
        args = parse_args([self.fixture_path])
        
        self.assertEqual(args.file, self.fixture_path)
        self.assertEqual(args.delimiter, ',')
        self.assertFalse(args.no_header)
        self.assertEqual(args.min_width, 5)
        self.assertIsNone(args.max_width)
        self.assertEqual(args.style, 'grid')

    def test_parse_args_custom(self):
        """Test argument parsing with custom values."""
        args = parse_args([
            self.fixture_path,
            '-d', ';',
            '--no-header',
            '--min-width', '10',
            '--max-width', '20',
            '-s', 'simple'
        ])
        
        self.assertEqual(args.file, self.fixture_path)
        self.assertEqual(args.delimiter, ';')
        self.assertTrue(args.no_header)
        self.assertEqual(args.min_width, 10)
        self.assertEqual(args.max_width, 20)
        self.assertEqual(args.style, 'simple')

    def test_parse_args_style_choices(self):
        """Test style argument choices."""
        # Valid styles should be accepted
        for style in ['simple', 'grid', 'minimal', 'none']:
            args = parse_args([self.fixture_path, '-s', style])
            self.assertEqual(args.style, style)
        
        # Invalid style should raise an error
        with self.assertRaises(SystemExit):
            parse_args([self.fixture_path, '-s', 'invalid'])

    @patch('vl.cli.view_csv')
    def test_main_success(self, mock_view_csv):
        """Test successful execution of main function."""
        result = main([self.fixture_path])
        
        # Check if view_csv was called with the correct parameters
        mock_view_csv.assert_called_once_with(
            file_path=self.fixture_path,
            delimiter=',',
            header=True,  # no_header is False by default
            min_col_width=5,
            max_col_width=None,
            border_style='grid'
        )
        
        # Should return 0 on success
        self.assertEqual(result, 0)

    @patch('vl.cli.view_csv')
    def test_main_custom_args(self, mock_view_csv):
        """Test main function with custom arguments."""
        args = [
            self.fixture_path,
            '-d', ';',
            '--no-header',
            '--min-width', '10',
            '--max-width', '20',
            '-s', 'simple'
        ]
        
        result = main(args)
        
        # Check if view_csv was called with the correct parameters
        mock_view_csv.assert_called_once_with(
            file_path=self.fixture_path,
            delimiter=';',
            header=False,  # no_header is True
            min_col_width=10,
            max_col_width=20,
            border_style='simple'
        )
        
        # Should return 0 on success
        self.assertEqual(result, 0)

    @patch('vl.cli.view_csv')
    @patch('sys.stderr')
    def test_main_file_not_found(self, mock_stderr, mock_view_csv):
        """Test main function with file not found error."""
        # Set up view_csv to raise FileNotFoundError
        mock_view_csv.side_effect = FileNotFoundError("No such file")
        
        result = main(['nonexistent.csv'])
        
        # Should return 1 on error
        self.assertEqual(result, 1)

    @patch('vl.cli.view_csv')
    @patch('sys.stderr')
    def test_main_permission_error(self, mock_stderr, mock_view_csv):
        """Test main function with permission error."""
        # Set up view_csv to raise PermissionError
        mock_view_csv.side_effect = PermissionError("Permission denied")
        
        result = main([self.fixture_path])
        
        # Should return 1 on error
        self.assertEqual(result, 1)

    @patch('vl.cli.view_csv')
    @patch('sys.stderr')
    def test_main_generic_error(self, mock_stderr, mock_view_csv):
        """Test main function with generic error."""
        # Set up view_csv to raise a generic exception
        mock_view_csv.side_effect = Exception("Something went wrong")
        
        result = main([self.fixture_path])
        
        # Should return 1 on error
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
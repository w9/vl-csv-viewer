"""Command-line interface for the VL CSV viewer."""

import argparse
import sys
from typing import List, Optional

from .formatter import view_csv


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='An ultrafast CSV viewer in terminals',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        'file',
        type=str,
        nargs='?',
        default='-',
        help='CSV file to view (use - for stdin)',
    )
    
    parser.add_argument(
        '-d', '--delimiter',
        type=str,
        default=None,  # Default will be determined based on file extension
        help='CSV delimiter character (default: "," for .csv files, "\\t" for others)',
    )
    
    parser.add_argument(
        '--no-header',
        action='store_true',
        help='Do not treat the first row as a header',
    )
    
    parser.add_argument(
        '--min-width',
        type=int,
        default=5,
        help='Minimum column width',
    )
    
    parser.add_argument(
        '--max-width',
        type=int,
        default=None,
        help='Maximum column width',
    )
    
    parser.add_argument(
        '-s', '--style',
        type=str,
        choices=['simple', 'grid', 'minimal', 'none'],
        default='grid',
        help='Table border style',
    )
    
    parser.add_argument(
        '--colors',
        action='store_true',
        help='Use alternating colors for columns',
    )
    
    parser.add_argument(
        '--color-list',
        type=str,
        default='bg_cyan,bg_white',
        help='Comma-separated list of color names for alternating columns',
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the VL CSV viewer CLI."""
    try:
        parsed_args = parse_args(args)
        
        # If file is stdin ('-') and stdin is a TTY (interactive terminal),
        # we can't read from it, so show error
        if parsed_args.file == '-' and sys.stdin.isatty():
            print("Error: No input file specified and no data piped to stdin.", file=sys.stderr)
            print("Usage: cat data.csv | vl  # or use vl filename.csv", file=sys.stderr)
            return 1
            
        # Determine the delimiter based on file extension if not explicitly provided
        delimiter = parsed_args.delimiter
        if delimiter is None:
            # For stdin or files not ending with .csv, use tab as the default delimiter
            if parsed_args.file == '-' or not parsed_args.file.lower().endswith('.csv'):
                delimiter = '\t'
            else:
                # For .csv files, use comma as the default delimiter
                delimiter = ','
        
        # Only use colors if the --colors flag is set
        if parsed_args.colors:
            # Convert the color list string to a list
            color_list = parsed_args.color_list.split(',') if parsed_args.color_list else None
            
            view_csv(
                file_path=parsed_args.file,
                delimiter=delimiter,
                header=not parsed_args.no_header,
                min_col_width=parsed_args.min_width,
                max_col_width=parsed_args.max_width,
                border_style=parsed_args.style,
                use_colors=True,
                column_colors=color_list,
            )
        else:
            # Don't pass color options if --colors is not set
            view_csv(
                file_path=parsed_args.file,
                delimiter=delimiter,
                header=not parsed_args.no_header,
                min_col_width=parsed_args.min_width,
                max_col_width=parsed_args.max_width,
                border_style=parsed_args.style,
            )
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
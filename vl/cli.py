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
        help='CSV file to view',
    )
    
    parser.add_argument(
        '-d', '--delimiter',
        type=str,
        default=',',
        help='CSV delimiter character',
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
        
        # Only use colors if the --colors flag is set
        if parsed_args.colors:
            # Convert the color list string to a list
            color_list = parsed_args.color_list.split(',') if parsed_args.color_list else None
            
            view_csv(
                file_path=parsed_args.file,
                delimiter=parsed_args.delimiter,
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
                delimiter=parsed_args.delimiter,
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
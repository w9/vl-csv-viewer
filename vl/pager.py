"""Command-line interface for the VL CSV viewer with pager support."""

import os
import sys
import subprocess
from . import cli

def main(args=None):
    """Run the VL CSV viewer and pipe the output through less pager."""
    # Create a pipe to less
    try:
        # Use the less pager with -S (chop long lines) and -R (interpret ANSI colors)
        less_cmd = ['less', '-SR']
        
        # Open the less process
        less_proc = subprocess.Popen(less_cmd, stdin=subprocess.PIPE, universal_newlines=True)
        
        # Capture the output to a StringIO buffer
        from io import StringIO
        buffer = StringIO()
        
        # Redirect stdout to our buffer
        old_stdout = sys.stdout
        sys.stdout = buffer
        
        # When stdin has data piped to it and we're using the 'vll' command alone
        # or with '-' as the first argument, we need to preserve stdin
        stdin_data = None
        if not sys.stdin.isatty():
            # Only read from stdin if necessary: when args is None or
            # it's ['-'] or an empty list (meaning user typed just 'vll')
            args_list = args if args is not None else []
            if not args_list or args_list[0] == '-':
                # Read all stdin data
                stdin_data = sys.stdin.read()
                
                # Create a new stdin for the CLI to use
                import io
                old_stdin = sys.stdin
                sys.stdin = io.StringIO(stdin_data)
        
        # Run the CLI with the provided arguments
        exit_code = cli.main(args)
        
        # If we replaced stdin, restore it
        if stdin_data is not None:
            sys.stdin = old_stdin
        
        # Get the output and write it to less
        output = buffer.getvalue()
        less_proc.stdin.write(output)
        
        # Restore stdout and close the pipe
        sys.stdout = old_stdout
        less_proc.stdin.close()
        
        # Wait for less to exit
        less_proc.wait()
        
        return exit_code
    except (BrokenPipeError, IOError):
        # Less was closed by the user
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
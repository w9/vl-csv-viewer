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
        
        # Run the CLI with the provided arguments
        exit_code = cli.main(args)
        
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
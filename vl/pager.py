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
        
        # Save the original stdout
        old_stdout = sys.stdout
        
        # Redirect stdout to the less process
        sys.stdout = less_proc.stdin
        
        # This ensures errors go to the terminal directly and not through less
        sys.stderr = old_stdout
        
        # Run the CLI with the provided arguments
        try:
            exit_code = cli.main(args)
            
            # If we get here, CLI ran successfully
            # Restore stdout and close the pipe
            sys.stdout.flush()
            sys.stdout = old_stdout
            less_proc.stdin.close()
            
            # Wait for less to exit
            less_proc.wait()
            
            return exit_code
            
        except SystemExit as e:
            # Argument parsing error or other exit, restore stdout and propagate
            sys.stdout = old_stdout
            less_proc.stdin.close()
            less_proc.terminate()
            return e.code
        
    except (BrokenPipeError, IOError):
        # Less was closed by the user
        sys.stdout = old_stdout if 'old_stdout' in locals() else sys.stdout
        return 0
    except Exception as e:
        # Make sure we restore stdout
        sys.stdout = old_stdout if 'old_stdout' in locals() else sys.stdout
        print(f"Error: {e}", file=sys.stderr)
        return 1
        
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
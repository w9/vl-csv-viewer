"""Command-line interface for the VL CSV viewer with pager support."""

import os
import sys
import subprocess
from . import cli

# Set up signal handler for broken pipes
import signal

# Original SIGPIPE handler
original_sigpipe = signal.getsignal(signal.SIGPIPE)

def sigpipe_handler(signum, frame):
    # Just exit silently when pipe is broken
    sys.exit(0)

def main(args=None):
    """Run the VL CSV viewer and pipe the output through less pager."""
    # Create a pipe to less
    old_stdout = sys.stdout
    less_proc = None
    
    try:
        # Set up SIGPIPE handler to prevent broken pipe errors
        signal.signal(signal.SIGPIPE, sigpipe_handler)
        
        # Use the less pager with -S (chop long lines) and -R (interpret ANSI colors)
        less_cmd = ['less', '-SR']
        
        # Open the less process
        less_proc = subprocess.Popen(less_cmd, stdin=subprocess.PIPE, universal_newlines=True)
        
        # Redirect stdout to the less process
        sys.stdout = less_proc.stdin
        
        # Run the CLI with the provided arguments
        try:
            exit_code = cli.main(args)
            
            # If we get here, CLI ran successfully
            # Close the pipe properly
            try:
                sys.stdout.flush()
            except (BrokenPipeError, IOError):
                pass
                
            # Restore stdout
            sys.stdout = old_stdout
            
            try:
                less_proc.stdin.close()
            except (BrokenPipeError, IOError):
                pass
                
            # Wait for less to exit
            less_proc.wait()
            
            return exit_code
            
        except SystemExit as e:
            # Restore stdout for argument parsing errors
            sys.stdout = old_stdout
            return e.code
            
        except (BrokenPipeError, IOError):
            # Less was closed by the user - handle silently
            sys.stdout = old_stdout
            return 0
            
    except (BrokenPipeError, IOError):
        # Less was closed by the user
        sys.stdout = old_stdout
        return 0
        
    except Exception as e:
        # Make sure we restore stdout
        sys.stdout = old_stdout
        
        # Don't show broken pipe errors
        if not isinstance(e, (BrokenPipeError, IOError)) and "Broken pipe" not in str(e):
            print(f"Error: {e}", file=sys.stderr)
        return 1
        
    finally:
        # Restore original signal handler
        signal.signal(signal.SIGPIPE, original_sigpipe)
        
        # Ensure stdout is restored
        sys.stdout = old_stdout
        
        # Close the less process if it was created
        if less_proc is not None:
            try:
                less_proc.stdin.close()
            except (BrokenPipeError, IOError, AttributeError):
                pass
                
            try:
                less_proc.wait()
            except:
                pass

if __name__ == "__main__":
    sys.exit(main())
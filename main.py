"""
Main entry point for the AI Resume Matcher
Supports both CLI and Web UI modes
"""

import sys
from ui.cli import main as cli_main


if __name__ == "__main__":
    # Check if web mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # Remove 'web' from argv before passing to Flask
        sys.argv.pop(1)
        from ui.web_app import app
        from config import Config
        app.run(debug=Config.FLASK_DEBUG, port=Config.FLASK_PORT)
    else:
        # Default to CLI
        sys.exit(cli_main())

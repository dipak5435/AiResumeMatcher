"""
Main entry point for the AI Resume Matcher
Supports both CLI and Web UI modes
"""

import sys
from ui.cli import main as cli_main


if __name__ == "__main__":
    # Check if web mode is requested (before CLI parser)
    if len(sys.argv) > 1 and (sys.argv[1] == "--web" or sys.argv[1] == "web"):
        # Remove '--web' or 'web' from argv before passing to Flask
        sys.argv.pop(1)
        from ui.web_app import app
        from config import Config
        print("🚀 Starting Web Server...")
        print(f"📱 Open browser: http://127.0.0.1:{Config.FLASK_PORT}")
        app.run(debug=Config.FLASK_DEBUG, port=Config.FLASK_PORT)
    else:
        # Default to CLI
        sys.exit(cli_main())

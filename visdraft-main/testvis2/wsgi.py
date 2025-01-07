# wsgi.py
import os
from pathlib import Path
from core.app import create_app

# Ensure required directories exist
required_dirs = [
    'data/raw/uploaded',
    'data/raw/sources',
    'data/processed/intermediate',
    'data/processed/final',
    'data/archived',
    'static/exports'
]

for dir_path in required_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# Create application instance
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5006,
        debug=True  # Set to False in production
    )
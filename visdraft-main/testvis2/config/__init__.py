# config/__init__.py

from pathlib import Path

# Create necessary directories if they don't exist
REQUIRED_DIRS = [
    'uploads',
    'uploads/data',
    'uploads/templates',
    'static/exports'
]

for directory in REQUIRED_DIRS:
    Path(directory).mkdir(parents=True, exist_ok=True)
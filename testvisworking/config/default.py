# config/default.py

# Basic Flask configuration
DEBUG = True
SECRET_KEY = "your_secret_key_here"

# File handling settings
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}

# Plotly configuration
PLOTLY_CONFIG = {
    'responsive': True,
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['sendDataToCloud'],
    'showLink': False,
    'displaylogo': False
}

# Default visualization settings
DEFAULT_VIZ_SETTINGS = {
    'theme': 'plotly_white',
    'color_sequence': [
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd'   # purple
    ],
    'default_height': 500,
    'default_margins': {
        't': 50,
        'r': 20,
        'b': 50,
        'l': 50
    }
}


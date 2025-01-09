# config/default.py
DEBUG = True
SECRET_KEY = "your_secret_key"

# API Registry Configuration
API_REGISTRY_CONFIG = {
    'data_transformation': {
        'name': 'Data Transformation',
        'description': 'Transform and process tabular data',
        'version': '1.0.0',
        'routes': ['/', '/upload', '/process'],
        'url_prefix': '/api/data-transformation',
        'interface': {
            'icon': 'database',
            'accepted_files': '.csv, .xlsx, .json',
            'parameter_fields': ['delimiter', 'encoding', 'transformationType'],
            'result_display': 'table',
        }
    },
    'text_extraction': {
        'name': 'Text Extraction Interface',
        'description': 'Interface for viewing and extracting text from large HTML documents',
        'version': '1.0.0',
        'routes': ['/', '/volumes', '/content/<volume>', '/save-delimiters', '/process-document'],
        'url_prefix': '/api/text-extraction',
        'interface': {
            'icon': 'file-text',
            'accepted_files': '.html',
            'parameter_fields': ['document', 'startDelimiter', 'endDelimiter'],
            'result_display': 'text',
        }
    },
    'document_processing': {
        'name': 'Document Processing',
        'description': 'Process and organize documents from local database',
        'version': '1.0.0',
        'routes': ['/', '/process', '/volume/<title>'],
        'url_prefix': '/api/document-processing',
        'interface': {
            'icon': 'book',
            'parameter_fields': ['volume_key', 'volume'],
            'result_display': 'json',
        }
    }
}

# Additional configuration settings
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
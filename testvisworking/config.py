"""Configuration settings for the application"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # SQLAlchemy config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance/plotlyvis.db')
    
    # File upload config
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Redis config (if using Redis for session/cache)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    # Plotly config
    PLOTLY_CONFIG = {
        'displayModeBar': True,
        'scrollZoom': True,
        'showLink': False,
        'responsive': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'sendDataToCloud',
            'autoScale2d',
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'lasso2d',
            'select2d'
        ]
    }
    
    # Template categories (for organizing visualization templates)
    TEMPLATE_CATEGORIES = [
        {
            'id': 'basic',
            'name': 'Basic Charts',
            'description': 'Simple, commonly used chart types',
            'templates': ['line', 'bar', 'scatter', 'pie']
        },
        {
            'id': 'statistical',
            'name': 'Statistical',
            'description': 'Charts for statistical analysis',
            'templates': ['box', 'violin', 'histogram', 'heatmap']
        },
        {
            'id': 'financial',
            'name': 'Financial',
            'description': 'Charts for financial data',
            'templates': ['candlestick', 'ohlc', 'waterfall']
        },
        {
            'id': 'comparison',
            'name': 'Comparison',
            'description': 'Charts for comparing values',
            'templates': ['bar', 'radar', 'parallel']
        }
    ]
    
    # Chart type configurations
    CHART_TYPES = {
        'line': {
            'name': 'Line Chart',
            'description': 'Show trends over time or ordered categories',
            'required_fields': ['x', 'y'],
            'optional_fields': ['color', 'line_dash', 'hover_data'],
            'aggregations': ['sum', 'average', 'count', 'min', 'max']
        },
        'bar': {
            'name': 'Bar Chart',
            'description': 'Compare values across categories',
            'required_fields': ['x', 'y'],
            'optional_fields': ['color', 'pattern', 'hover_data'],
            'aggregations': ['sum', 'average', 'count', 'min', 'max']
        },
        'scatter': {
            'name': 'Scatter Plot',
            'description': 'Show relationship between two variables',
            'required_fields': ['x', 'y'],
            'optional_fields': ['size', 'color', 'hover_data', 'text'],
            'aggregations': []
        },
        'pie': {
            'name': 'Pie Chart',
            'description': 'Show composition of a whole',
            'required_fields': ['values', 'names'],
            'optional_fields': ['hover_data', 'text'],
            'aggregations': ['sum', 'count']
        },
        'box': {
            'name': 'Box Plot',
            'description': 'Show distribution of values',
            'required_fields': ['y'],
            'optional_fields': ['x', 'color', 'hover_data'],
            'aggregations': []
        },
        'violin': {
            'name': 'Violin Plot',
            'description': 'Show probability density of data',
            'required_fields': ['y'],
            'optional_fields': ['x', 'color', 'hover_data'],
            'aggregations': []
        },
        'histogram': {
            'name': 'Histogram',
            'description': 'Show distribution of a single variable',
            'required_fields': ['x'],
            'optional_fields': ['color', 'hover_data'],
            'aggregations': ['count']
        },
        'heatmap': {
            'name': 'Heatmap',
            'description': 'Show patterns in a matrix of values',
            'required_fields': ['x', 'y', 'z'],
            'optional_fields': ['hover_data', 'text'],
            'aggregations': ['sum', 'average', 'count', 'min', 'max']
        }
    }
    
    # Default chart layout settings
    DEFAULT_LAYOUT = {
        'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50},
        'showlegend': True,
        'hovermode': 'closest',
        'dragmode': 'zoom',
        'font': {
            'family': 'Arial, sans-serif',
            'size': 12,
            'color': '#2D3748'
        },
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'colorway': [
            '#4F46E5', '#10B981', '#F59E0B', '#EF4444',
            '#8B5CF6', '#EC4899', '#06B6D4', '#F97316'
        ]
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DEVELOPMENT = False
    
    # Override these in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production configuration")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or None
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No DATABASE_URL set for production configuration")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Visualization(db.Model):
    """Model for storing visualization configurations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    source_file = db.Column(db.String(255))  # Original data source filename
    chart_type = db.Column(db.String(50), nullable=False)
    config = db.Column(db.Text, nullable=False)  # JSON string of Plotly config
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_template = db.Column(db.Boolean, default=False)  # Flag for template visualizations
    tags = db.Column(db.String(255))  # Comma-separated tags for categorization

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_file': self.source_file,
            'chart_type': self.chart_type,
            'config': json.loads(self.config),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_template': self.is_template,
            'tags': self.tags.split(',') if self.tags else []
        }

    def get_preview_config(self):
        """Get a simplified version of the config for preview"""
        config = json.loads(self.config)
        if 'data' in config and len(config['data']) > 0:
            # Limit data points for preview
            for trace in config['data']:
                if 'x' in trace and len(trace['x']) > 50:
                    trace['x'] = trace['x'][:50]
                if 'y' in trace and len(trace['y']) > 50:
                    trace['y'] = trace['y'][:50]
        return config

class Dataset(db.Model):
    """Model for tracking uploaded datasets"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # csv, xlsx, etc.
    row_count = db.Column(db.Integer)
    column_info = db.Column(db.Text)  # JSON string of column names and types
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    description = db.Column(db.Text)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'row_count': self.row_count,
            'column_info': json.loads(self.column_info),
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'description': self.description
        }

def init_db(app):
    """Initialize the database and create tables"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Visualization(db.Model):
    """Enhanced model for storing library-focused visualizations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chart_type = db.Column(db.String(50), nullable=False)
    config = db.Column(db.Text, nullable=False)  # JSON string of Plotly config
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Enhanced metadata for library context
    category = db.Column(db.String(50))  # e.g., 'Circulation', 'Collections', 'Programs'
    time_period = db.Column(db.String(50))  # e.g., 'Monthly', 'Yearly', 'Weekly'
    is_template = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(255))
    data_source = db.Column(db.String(255))  # Reference to the dataset used
    shared = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)  # Additional context or methodology notes

    def to_dict(self):
        """Convert model to dictionary with enhanced metadata"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'chart_type': self.chart_type,
            'config': json.loads(self.config),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'category': self.category,
            'time_period': self.time_period,
            'is_template': self.is_template,
            'tags': self.tags.split(',') if self.tags else [],
            'data_source': self.data_source,
            'shared': self.shared,
            'notes': self.notes
        }

    def get_preview_config(self):
        """Get a simplified version of the config for preview"""
        config = json.loads(self.config)
        if 'data' in config and len(config['data']) > 0:
            for trace in config['data']:
                for key in ['x', 'y']:
                    if key in trace and len(trace[key]) > 20:
                        trace[key] = trace[key][:20]
        return config

class Dataset(db.Model):
    """Enhanced model for library datasets"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(10), nullable=False)
    
    # Enhanced metadata
    category = db.Column(db.String(50))  # e.g., 'Circulation Data', 'Program Statistics'
    date_range = db.Column(db.String(100))  # e.g., 'Jan 2024 - Dec 2024'
    row_count = db.Column(db.Integer)
    column_info = db.Column(db.Text)  # JSON string of column metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    description = db.Column(db.Text)
    update_frequency = db.Column(db.String(50))  # e.g., 'Monthly', 'Weekly'
    data_source = db.Column(db.String(100))  # e.g., 'ILS Export', 'Manual Entry'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'file_type': self.file_type,
            'category': self.category,
            'date_range': self.date_range,
            'row_count': self.row_count,
            'column_info': json.loads(self.column_info) if self.column_info else {},
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'description': self.description,
            'update_frequency': self.update_frequency,
            'data_source': self.data_source
        }

class Template(db.Model):
    """Model for pre-built library visualization templates"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chart_type = db.Column(db.String(50), nullable=False)
    config = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    difficulty_level = db.Column(db.String(20))  # 'Beginner', 'Intermediate', 'Advanced'
    required_columns = db.Column(db.Text)  # JSON list of required data columns
    help_text = db.Column(db.Text)  # Step-by-step guidance
    example_data = db.Column(db.Text)  # JSON string of example data
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'chart_type': self.chart_type,
            'config': json.loads(self.config),
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'required_columns': json.loads(self.required_columns) if self.required_columns else [],
            'help_text': self.help_text,
            'example_data': json.loads(self.example_data) if self.example_data else None
        }

def init_db(app):
    """Initialize the database with library-specific templates"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
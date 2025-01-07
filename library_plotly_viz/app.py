import os
import logging
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash
from sqlalchemy import desc
import pandas as pd
from models import db, Visualization, Dataset, Template, init_db

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_file=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_viz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    init_db(app)

    @app.route('/')
    def home():
        """Enhanced dashboard for librarians"""
        recent_vizs = Visualization.query.filter_by(is_template=False).order_by(
            desc(Visualization.updated_at)).limit(5).all()
        
        # Get categorized templates
        templates = Template.query.order_by(Template.category, Template.name).all()
        templates_by_category = {}
        for template in templates:
            if template.category not in templates_by_category:
                templates_by_category[template.category] = []
            templates_by_category[template.category].append(template)

        recent_datasets = Dataset.query.order_by(desc(Dataset.last_used)).limit(5).all()
        
        return render_template(
            'index.html',
            recent_vizs=[v.to_dict() for v in recent_vizs],
            templates_by_category=templates_by_category,
            recent_datasets=[d.to_dict() for d in recent_datasets]
        )

    @app.route('/viz/new', methods=['GET'])
    def new_visualization():
        """Create new visualization with template selection"""
        templates = Template.query.all()
        datasets = Dataset.query.order_by(Dataset.name).all()
        return render_template(
            'visualizations/new.html',
            templates=[t.to_dict() for t in templates],
            datasets=[d.to_dict() for d in datasets]
        )

    @app.route('/api/data/preview/<int:dataset_id>')
    def preview_data(dataset_id):
        """Preview dataset with smart sampling"""
        try:
            dataset = Dataset.query.get_or_404(dataset_id)
            df = pd.read_csv(dataset.file_path)
            
            # Smart sampling for large datasets
            if len(df) > 1000:
                df = df.sample(n=1000)
            
            # Detect date columns and format them
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.strftime('%Y-%m-%d')
            
            return jsonify({
                'data': df.to_dict(orient='records'),
                'columns': list(df.columns),
                'row_count': len(df)
            })
        except Exception as e:
            logger.error(f"Error previewing data: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/viz/save', methods=['POST'])
    def save_visualization():
        """Save visualization with enhanced error checking"""
        try:
            data = request.json
            required_fields = ['name', 'chart_type', 'config']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            viz = Visualization(
                name=data['name'],
                description=data.get('description', ''),
                chart_type=data['chart_type'],
                config=json.dumps(data['config']),
                category=data.get('category'),
                time_period=data.get('time_period'),
                tags=','.join(data.get('tags', [])),
                data_source=data.get('data_source'),
                notes=data.get('notes')
            )
            
            db.session.add(viz)
            db.session.commit()
            
            return jsonify({'id': viz.id, 'message': 'Visualization saved successfully'})
        except Exception as e:
            logger.error(f"Error saving visualization: {str(e)}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/viz/<int:viz_id>')
    def view_visualization(viz_id):
        """View visualization with enhanced context"""
        viz = Visualization.query.get_or_404(viz_id)
        return render_template(
            'visualizations/view.html',
            visualization=viz.to_dict(),
            created_at=viz.created_at.strftime('%B %d, %Y'),
            updated_at=viz.updated_at.strftime('%B %d, %Y')
        )

    @app.route('/help')
    def help_page():
        """Enhanced help system for librarians"""
        return render_template(
            'help.html',
            examples=Template.query.all(),
            faq=load_faq()
        )

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    def load_faq():
        """Load frequently asked questions"""
        return [
            {
                'question': 'How do I create a circulation trends visualization?',
                'answer': 'Select the "Circulation Trends" template and upload your circulation data CSV...'
            },
            {
                'question': 'What chart type should I use for collection analysis?',
                'answer': 'For collection analysis, pie charts work well for composition...'
            },
            # Add more FAQs here
        ]

    return app
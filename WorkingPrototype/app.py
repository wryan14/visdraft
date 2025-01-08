import os
import logging
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from sqlalchemy import desc
import pandas as pd
from models import db, Visualization, Dataset, Template, init_db
from werkzeug.utils import secure_filename
from datetime import datetime

def format_datetime(value, format='%B %d, %Y'):
    """Format a datetime object to a string."""
    if value is None:
        return ""
    return value.strftime(format)

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_file=None):
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    
    # Register the datetime filter
    app.jinja_env.filters['datetime'] = format_datetime
    
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
        try:
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
            
            # Default templates if none exist
            if not templates_by_category:
                templates_by_category = {
                    'Circulation': [],
                    'Collections': [],
                    'Programs': [],
                    'Usage Statistics': []
                }
            
            return render_template(
                'index.html',
                recent_vizs=[v.to_dict() for v in recent_vizs] if recent_vizs else [],
                templates_by_category=templates_by_category,
                recent_datasets=[d.to_dict() for d in recent_datasets] if recent_datasets else [],
                current_year=datetime.now().year
            )
        except Exception as e:
            logger.error(f"Error in home route: {str(e)}")
            return render_template(
                'index.html',
                recent_vizs=[],
                templates_by_category={},
                recent_datasets=[],
                current_year=datetime.now().year,
                error="Unable to load dashboard data. Please try again later."
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
            
            # Ensure all fields are properly serialized as strings
            viz = Visualization(
                name=str(data['name']),
                description=str(data.get('description', '')),
                chart_type=str(data['chart_type']),
                config=json.dumps(data['config']),  # Serialize config to JSON string
                category=str(data.get('category', '')),
                time_period=str(data.get('time_period', '')),
                tags=','.join(str(tag) for tag in data.get('tags', [])),
                data_source=json.dumps(data.get('data_source', {})),  # Serialize data_source to JSON string
                shared=bool(data.get('shared', False)),
                notes=str(data.get('notes', ''))
            )
            
            try:
                db.session.add(viz)
                db.session.commit()
                return jsonify({'id': viz.id, 'message': 'Visualization saved successfully'})
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error saving visualization: {str(e)}")
                return jsonify({'error': 'Database error while saving'}), 500
                
        except Exception as e:
            logger.error(f"Error saving visualization: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/viz/<int:viz_id>')
    def view_visualization(viz_id):
        """View visualization with enhanced context"""
        try:
            viz = Visualization.query.get_or_404(viz_id)
            
            # If there's data source info, fetch the actual data
            config = json.loads(viz.config)
            if viz.data_source:
                dataset = Dataset.query.get(viz.data_source)
                if dataset:
                    df = pd.read_csv(dataset.file_path)
                    if config.get('data') and config['data'][0]:
                        data_config = config['data'][0]
                        if data_config.get('xaxis') and data_config.get('yaxis'):
                            x_col = data_config['xaxis']
                            y_col = data_config['yaxis']
                            if data_config['type'] == 'histogram':
                                data_config['x'] = df[x_col].tolist()
                            else:
                                data_config['x'] = df[x_col].tolist()
                                data_config['y'] = df[y_col].tolist()
                            viz.config = json.dumps(config)
            
            # Get related visualizations
            related_vizs = Visualization.query\
                .filter(Visualization.id != viz_id)\
                .filter(
                    (Visualization.category == viz.category) | 
                    (Visualization.chart_type == viz.chart_type)
                )\
                .limit(5)\
                .all()
            
            return render_template(
                'visualizations/view.html',
                visualization=viz.to_dict(),
                related_visualizations=[v.to_dict() for v in related_vizs],
                created_at=viz.created_at.strftime('%B %d, %Y'),
                updated_at=viz.updated_at.strftime('%B %d, %Y')
            )
        except Exception as e:
            logger.error(f"Error viewing visualization {viz_id}: {str(e)}")
            flash('Error loading visualization', 'error')
            return redirect(url_for('home'))


    @app.route('/api/recent')
    def get_recent_visualizations():
        """Get recent visualizations for the dashboard"""
        try:
            # Get recent non-template visualizations
            recent_vizs = Visualization.query\
                .filter_by(is_template=False)\
                .order_by(desc(Visualization.updated_at))\
                .limit(5)\
                .all()
            
            # Safely convert to dict format
            viz_list = []
            for viz in recent_vizs:
                try:
                    viz_dict = {
                        'id': viz.id,
                        'name': viz.name,
                        'chart_type': viz.chart_type,
                        'category': viz.category,
                        'created_at': viz.created_at.strftime('%Y-%m-%d %H:%M:%S') if viz.created_at else None,
                        'updated_at': viz.updated_at.strftime('%Y-%m-%d %H:%M:%S') if viz.updated_at else None
                    }
                    viz_list.append(viz_dict)
                except Exception as viz_error:
                    logger.error(f"Error processing visualization {viz.id}: {str(viz_error)}")
                    continue
            
            return jsonify({
                'visualizations': viz_list
            })
            
        except Exception as e:
            logger.error(f"Error fetching recent visualizations: {str(e)}")
            return jsonify({
                'error': 'Unable to load recent visualizations',
                'visualizations': []
            }), 500

    @app.route('/api/data/upload', methods=['POST'])
    def upload_data():
        """Handle data file uploads with enhanced error handling"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            # Check file extension
            allowed_extensions = {'.csv', '.xlsx', '.xls'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'error': f'File type {file_ext} not supported. Please upload CSV or Excel files.'}), 400
                
            # Ensure filename is secure and unique
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{file_ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Create dataset record
            dataset = Dataset(
                name=filename,
                file_path=file_path,
                file_type=file_ext[1:],  # Remove the dot from extension
                uploaded_at=datetime.utcnow(),
                category='Uploaded Data',
                data_source='User Upload'
            )
            
            db.session.add(dataset)
            db.session.commit()
            
            # Read basic file info
            try:
                if file_ext == '.csv':
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                    
                dataset.row_count = len(df)
                dataset.column_info = json.dumps({
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.astype(str).to_dict()
                })
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Error reading file content: {str(e)}")
                # We don't need to delete the record if we can't read it,
                # as it might be useful to keep track of the upload attempt
            
            return jsonify({
                'message': 'File uploaded successfully',
                'dataset_id': dataset.id,
                'name': dataset.name
            })
            
        except Exception as e:
            logger.error(f"Error in upload_data: {str(e)}")
            db.session.rollback()
            return jsonify({'error': 'An error occurred while processing the file'}), 500
        
    @app.route('/templates')
    def list_templates():
        """List available visualization templates"""
        templates = Template.query.order_by(Template.category, Template.name).all()
        templates_by_category = {}
        for template in templates:
            if template.category not in templates_by_category:
                templates_by_category[template.category] = []
            templates_by_category[template.category].append(template)
        
        return render_template('templates.html', templates_by_category=templates_by_category)

    @app.route('/api/templates')
    def get_templates():
        """Get templates for a category"""
        category = request.args.get('category')
        if category:
            templates = Template.query.filter_by(category=category).all()
        else:
            templates = Template.query.all()
        
        return jsonify({
            'templates': [t.to_dict() for t in templates]
        })

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


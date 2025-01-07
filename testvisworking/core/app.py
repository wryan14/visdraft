# core/app.py
import os
import logging
from datetime import datetime
from flask import Flask, render_template, send_from_directory, jsonify
from sqlalchemy import desc
from core.visualizations.routes import viz_bp
from core.models import db, init_db, Visualization, Dataset

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name="config.default"):
    # Initialize Flask app with template directory
    app = Flask(__name__, 
                template_folder='../templates',  
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config_name)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, '../instance/plotlyvis.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    
    # Register the visualization blueprint
    app.register_blueprint(viz_bp, url_prefix='/viz')
    
    # Home route with dashboard
    @app.route('/')
    def home():
        # Get recent visualizations
        recent_vizs = Visualization.query.filter_by(is_template=False).order_by(desc(Visualization.updated_at)).limit(5).all()
        
        # Get template visualizations
        templates = Visualization.query.filter_by(is_template=True).all()
        
        # Get recent datasets
        recent_datasets = Dataset.query.order_by(desc(Dataset.last_used)).limit(5).all()
        
        return render_template(
            'index.html',
            recent_vizs=[viz.to_dict() for viz in recent_vizs],
            templates=[viz.to_dict() for viz in templates],
            recent_datasets=[ds.to_dict() for ds in recent_datasets],
            plotly_config=app.config.get('PLOTLY_CONFIG', {})
        )

    @app.route('/api/stats')
    def get_stats():
        """Get system statistics for the dashboard"""
        try:
            total_vizs = Visualization.query.filter_by(is_template=False).count()
            total_datasets = Dataset.query.count()
            recent_activity = (
                Visualization.query
                .filter_by(is_template=False)
                .order_by(desc(Visualization.updated_at))
                .limit(10)
                .all()
            )
            
            return jsonify({
                'total_visualizations': total_vizs,
                'total_datasets': total_datasets,
                'recent_activity': [
                    {
                        'id': v.id,
                        'name': v.name,
                        'type': v.chart_type,
                        'updated_at': v.updated_at.isoformat(),
                    }
                    for v in recent_activity
                ]
            })
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    # Debug route to check system status
    @app.route('/debug/status')
    def debug_status():
        return {
            'template_folder': app.template_folder,
            'available_templates': [str(t) for t in app.jinja_loader.list_templates()],
            'config': {
                k: str(v) for k, v in app.config.items() 
                if k not in ['SECRET_KEY'] and not k.startswith('_')
            },
            'database_tables': [str(t) for t in db.metadata.tables.keys()],
            'registered_blueprints': [str(bp) for bp in app.blueprints.keys()]
        }

    return app
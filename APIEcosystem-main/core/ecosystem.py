# core/ecosystem.py
import os
import logging
from flask import Flask, render_template_string, render_template, current_app
from core.dashboard.routes import dashboard_bp
from documentation.utils import DocumentationSystem
from documentation.routes import create_documentation_bp
from config.api_registry import APIRegistry

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_registered_apis():
    """Helper function to access registered APIs in templates"""
    return current_app.config['API_REGISTRY_CONFIG']

def create_app(config_name="config.default"):
    # Get the absolute path to the shared/templates directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    shared_templates_path = os.path.join(base_dir, 'shared/templates')

    logger.debug(f"Base directory: {base_dir}")
    logger.debug(f"Shared templates path: {shared_templates_path}")

    app = Flask(__name__, template_folder=shared_templates_path)
    
    # Load configurations
    if isinstance(config_name, str):
        if not config_name.startswith('config.'):
            config_name = f'config.{config_name}'
    app.config.from_object(config_name)
    
    # Add template global for accessing APIs in templates
    app.jinja_env.globals['get_registered_apis'] = get_registered_apis
    
    # Add home route
    @app.route('/')
    def home():
        return render_template('home.html')
    
    # Initialize API registry
    registry = APIRegistry()
    for api_name, config in app.config.get('API_REGISTRY_CONFIG', {}).items():
        registry.register(config)  # Pass the config dict directly
        logger.debug(f"Registered API: {api_name}")
        
        # Dynamically import and register API blueprint
        try:
            module_path = f"apis.{api_name}.routes"
            module = __import__(module_path, fromlist=[''])
            blueprint_name = f"{api_name}_bp"
            if hasattr(module, blueprint_name):
                blueprint = getattr(module, blueprint_name)
                url_prefix = config.get('url_prefix', f'/api/{api_name}')
                app.register_blueprint(blueprint, url_prefix=url_prefix)
                logger.debug(f"Registered blueprint for API: {api_name}")
        except ImportError as e:
            logger.error(f"Failed to load API {api_name}: {str(e)}")
    
    # Register dashboard blueprint
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    logger.debug("Registered dashboard blueprint")

    # Initialize documentation system with the app
    doc_system = DocumentationSystem()
    doc_system.init_app(app)
    logger.debug("Initialized documentation system")

    # Register documentation blueprint
    documentation_bp = create_documentation_bp(doc_system)
    app.register_blueprint(documentation_bp, url_prefix="/docs")
    logger.debug("Registered documentation blueprint")

    # Add template debug route
    @app.route('/debug/templates')
    def debug_templates():
        return {
            'template_folder': app.template_folder,
            'available_templates': [str(t) for t in app.jinja_loader.list_templates()],
            'searchpath': [str(p) for p in app.jinja_loader.searchpath]
        }

    # Sitemap route
    @app.route('/sitemap')
    def sitemap():
        links = []
        for rule in app.url_map.iter_rules():
            methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            url = f"<li><strong>{rule.endpoint}</strong> [{methods}] -> {rule.rule}</li>"
            links.append(url)

        return render_template_string("""
        <html>
        <head><title>Sitemap</title></head>
        <body>
            <h1>Sitemap</h1>
            <ul>
                {{ links|safe }}
            </ul>
        </body>
        </html>
        """, links='\n'.join(links))

    # Debug the template search path
    logger.debug(f"Template search paths: {app.jinja_loader.searchpath}")

    return app
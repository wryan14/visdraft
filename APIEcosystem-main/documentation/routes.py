# documentation/routes.py
from flask import Blueprint, render_template, current_app
import logging

logger = logging.getLogger(__name__)

def create_documentation_bp(doc_system, name='documentation'):
    documentation_bp = Blueprint(name, __name__)

    @documentation_bp.route('/')
    def docs_home():
        """Documentation home page listing all APIs"""
        logger.debug("Entering docs_home route")
        
        # Get APIs directly from registry config
        apis = []
        registry_config = current_app.config.get('API_REGISTRY_CONFIG', {})
        
        # Debug print
        logger.debug(f"Available APIs in registry: {list(registry_config.keys())}")
        
        for api_name, config in registry_config.items():
            api_info = {
                'name': config['name'],
                'description': config['description'],
                'version': config['version'],
                'interface': config['interface'],
                'registry_key': api_name,
                'url_prefix': config.get('url_prefix', f'/api/{api_name}')  # Add URL prefix
            }
            apis.append(api_info)
            
        logger.debug(f"APIs for template: {apis}")
        return render_template('documentation/home.html', apis=apis)

    @documentation_bp.route('/api/<string:api_name>')
    def api_docs(api_name):
        """Individual API documentation page"""
        logger.debug(f"Looking up documentation for API: {api_name}")
        
        registry_config = current_app.config.get('API_REGISTRY_CONFIG', {})
        logger.debug(f"Available keys in registry: {list(registry_config.keys())}")
        
        # Try different variations of the api_name
        api_key = api_name.lower().replace(' ', '_')
        api_key_alt = api_name.lower().replace('_', '')
        
        api_config = (registry_config.get(api_key) or 
                     registry_config.get(api_key_alt) or 
                     registry_config.get(api_name))
        
        if not api_config:
            logger.error(f"API {api_name} not found. Tried keys: {api_key}, {api_key_alt}, {api_name}")
            return f"Documentation not found for API: {api_name}", 404
            
        # Prepare API documentation data
        api_data = {
            'name': api_config['name'],
            'description': api_config['description'],
            'version': api_config['version'],
            'interface': api_config['interface'],
            'url_prefix': api_config.get('url_prefix', f'/api/{api_name}')
        }
        
        logger.debug(f"Rendering documentation for API: {api_data}")
        return render_template('documentation/api.html', api=api_data)

    return documentation_bp
# core/dashboard/routes.py
from flask import Blueprint, render_template, current_app, jsonify
import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Main dashboard view showing API statistics and status"""
    # Get API data from the registry
    api_registry = current_app.config.get('API_REGISTRY_CONFIG', {})
    
    # Calculate statistics
    total_apis = len(api_registry)
    # For now, assume all APIs are active
    active_apis = total_apis
    
    # Transform API data for display
    apis = []
    for api_name, config in api_registry.items():
        api_info = {
            "name": config['name'],
            "description": config['description'],
            "version": config['version'],
            "status": "Active",  # You might want to add this to your config
            "url_prefix": config['url_prefix'],
            # Safely access interface attributes
            "icon": getattr(config['interface'], 'icon', 'box')
        }
        apis.append(api_info)
    
    # Dashboard data
    data = {
        "total_apis": total_apis,
        "active_apis": active_apis,
        "apis": apis,
        "system_status": {
            "status": "Operational",
            "uptime": "99.9%",
            "total_requests": "25.4K"  # You might want to make this dynamic
        }
    }
    
    return render_template('dashboard/index.html', **data)

@dashboard_bp.route('/health')
def health_check():
    """System health check endpoint"""
    # Here you could add real health checks
    api_registry = current_app.config.get('API_REGISTRY_CONFIG', {})
    
    health_status = {
        "status": "healthy",
        "api_count": len(api_registry),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    return jsonify(health_status)
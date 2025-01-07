# # core/app.py
# import os
# import logging
# from flask import Flask, render_template, send_from_directory
# from core.visualizations.routes import viz_bp

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def create_app(config_name="config.default"):
#     # Initialize Flask app with template directory
#     app = Flask(__name__, 
#                 template_folder='../views',  # Point to our views directory
#                 static_folder='../static')
    
#     # Load configuration
#     app.config.from_object(config_name)
#     # Register the visualization blueprint
#     app.register_blueprint(viz_bp, url_prefix='/viz')
    
#     # Home route
#     @app.route('/')
#     def home():
#         # Sample visualization for demonstration
#         sample_viz = {
#             'id': 'demo',
#             'name': 'Monthly Metrics',
#             'type': 'line',
#             'data': {
#                 'x': [1, 2, 3, 4, 5],
#                 'y': [2, 4, 3, 5, 4],
#                 'type': 'scatter',
#                 'mode': 'lines+markers'
#             },
#             'layout': {
#                 'title': 'Sample Visualization',
#                 'height': 300,
#                 'margin': {'t': 30, 'r': 20, 'b': 30, 'l': 30}
#             }
#         }
        
#         return render_template(
#             'index.html',
#             sample_viz=sample_viz,
#             plotly_config=app.config.get('PLOTLY_CONFIG', {})
#         )

#     # Error handlers
#     @app.errorhandler(404)
#     def not_found_error(error):
#         return render_template('errors/404.html'), 404

#     @app.errorhandler(500)
#     def internal_error(error):
#         return render_template('errors/500.html'), 500

#     # Debug route to check templates
#     @app.route('/debug/templates')
#     def debug_templates():
#         return {
#             'template_folder': app.template_folder,
#             'available_templates': [str(t) for t in app.jinja_loader.list_templates()],
#             'searchpath': [str(p) for p in app.jinja_loader.searchpath]
#         }

#     return app
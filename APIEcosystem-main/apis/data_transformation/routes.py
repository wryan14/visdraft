# Modified data_transformation/routes.py
from flask import Blueprint, render_template, request, jsonify
from flask import current_app
from werkzeug.utils import secure_filename
import os

data_transformation_bp = Blueprint('data_transformation', __name__)

@data_transformation_bp.route('/')
def index():
    api_name = 'data_transformation'
    api_config = current_app.config['API_REGISTRY_CONFIG'].get(api_name)
    
    if not api_config:
        return jsonify({'error': f'API configuration for {api_name} not found.'}), 404

    return render_template(
        'apis/shared/api_interface.html',
        api_type=api_name,
        api_name=api_config['name'],
        api_description=api_config['description'],
        interface_config=api_config['interface']  # Contains the old API_CONFIGS data
    )

@data_transformation_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})

@data_transformation_bp.route('/process', methods=['POST'])
def process_api():
    data = request.get_json()
    files = data.get('files', [])
    parameters = data.get('parameters', {})

    # Simulate processing
    result = {
        'status': 'success',
        'data': f'Processed {len(files)} files with parameters: {parameters}',
    }
    return jsonify(result)

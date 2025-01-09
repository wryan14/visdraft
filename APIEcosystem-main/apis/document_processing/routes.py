from flask import Blueprint, request, jsonify, render_template
from .utils import process_volume, get_volume_data
from shared.extensions import db

bp = Blueprint('document_processing', __name__)

@bp.route('/')
def index():
    """Main interface for document processing"""
    return render_template('apis/document_processing/index.html')

@bp.route('/process', methods=['POST'])
def process():
    """Process a volume from the database"""
    data = request.get_json()
    volume_key = data.get('volume_key')
    volume = data.get('volume')
    
    if not volume_key or not volume:
        return jsonify({'error': 'Volume key and number are required'}), 400
    
    try:
        result = process_volume(volume_key, volume)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/volume/<title>')
def get_volume(title):
    """Get volume details from the database"""
    try:
        volume_data = get_volume_data(title)
        if volume_data:
            return jsonify(volume_data)
        return jsonify({'error': 'Volume not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
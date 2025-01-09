# routes.py
from flask import Blueprint, render_template, request, jsonify, current_app
import os
import re
from glob import glob
from .utils import process_html, search_church_father

text_extraction_bp = Blueprint('text_extraction', __name__)

@text_extraction_bp.route('/')
def index():
    api_name = 'text_extraction'
    api_config = current_app.config['API_REGISTRY_CONFIG'].get(api_name)
    
    if not api_config:
        return jsonify({'error': f'API configuration for {api_name} not found.'}), 404

    return render_template(
        'apis/shared/text_extraction.html',
        api_type=api_name,
        api_name=api_config['name'],
        api_description=api_config['description'],
        interface_config=api_config['interface']
    )

@text_extraction_bp.route('/volumes', methods=['GET'])
def get_volumes():
    try:
        path = r"E:\Translation\Patrologia_Latina"
        files = glob(os.path.join(path, "*.html"))
        volumes = []
        
        for file in files:
            filename = os.path.basename(file)
            vol_num = filename.split("_Vol_")[1].split("_")[0]
            volumes.append({
                'number': vol_num,
                'path': file
            })
        
        volumes.sort(key=lambda x: int(x['number']))
        return jsonify(volumes)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@text_extraction_bp.route('/content/<volume>', methods=['GET'])
def get_volume_content(volume):
    try:
        path = rf"E:\Translation\Patrologia_Latina\Patrologia_Latina_Vol_{volume}_Cleaned.html"
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@text_extraction_bp.route('/save-content', methods=['POST'])
def save_content():
    try:
        data = request.get_json()
        volume = data.get('volume')
        content = data.get('content')
        
        if not all([volume, content]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters'
            }), 400

        file_path = rf"E:\Translation\Patrologia_Latina\Patrologia_Latina_Vol_{volume}_Cleaned.html"
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        
        return jsonify({
            'status': 'success',
            'message': 'Content saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@text_extraction_bp.route('/process-document', methods=['POST'])
def process_document():
    try:
        form_data = request.get_json()
        print("Form Data Received:", form_data)
        
        volume = form_data['volume']
        start_delimiter = form_data['start_delimiter']
        end_delimiter = form_data['end_delimiter']
        author = form_data['author']
        database_title = form_data['database_title']
        
        author_description = search_church_father(author)
        combined_html = process_html(volume, start_delimiter, end_delimiter, database_title, author, author_description)
        print("COMBINED TEXT")
        print(combined_html[0:100])

        return jsonify({
            'status': 'success',
            'author_description': author_description,
            'combined_html': combined_html
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
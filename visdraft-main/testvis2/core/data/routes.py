"""Routes for data source management"""

import os
import pandas as pd
from datetime import datetime
from flask import (
    current_app, request, jsonify, send_from_directory,
    render_template, flash, redirect, url_for
)
from werkzeug.utils import secure_filename
from core.models import db, Dataset
from core.visualizations.helpers import get_column_types, get_column_stats
from . import data_bp

def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@data_bp.route('/')
def index():
    """List all available datasets"""
    datasets = Dataset.query.order_by(Dataset.last_used.desc().nulls_last()).all()
    return render_template('data/index.html', datasets=datasets)

@data_bp.route('/upload', methods=['POST'])
def upload():
    """Handle file upload and data processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        original_filename = filename
        
        # Check if dataset already exists
        existing = Dataset.query.filter_by(original_filename=original_filename).first()
        if existing:
            # Update timestamp of last use
            existing.last_used = datetime.utcnow()
            db.session.commit()
            return jsonify({
                'message': 'Dataset already exists',
                'dataset': existing.to_dict()
            })
        
        # Save the file
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Load and analyze the data
        if filename.endswith('.csv'):
            df = pd.read_csv(upload_path)
        else:  # Excel
            df = pd.read_excel(upload_path)
        
        # Get column information
        column_info = {
            'types': get_column_types(df),
            'stats': get_column_stats(df)
        }
        
        # Create dataset record
        dataset = Dataset(
            filename=filename,
            original_filename=original_filename,
            file_type=filename.rsplit('.', 1)[1].lower(),
            row_count=len(df),
            column_info=json.dumps(column_info),
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow()
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'dataset': dataset.to_dict()
        })
        
    except Exception as e:
        # Clean up partial upload if necessary
        if 'upload_path' in locals() and os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500

@data_bp.route('/preview/<int:dataset_id>')
def preview(dataset_id):
    """Show a preview of the dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.filename)
        
        if dataset.file_type == 'csv':
            df = pd.read_csv(file_path, nrows=100)  # Preview first 100 rows
        else:
            df = pd.read_excel(file_path, nrows=100)
        
        preview_data = df.to_dict(orient='records')
        columns = df.columns.tolist()
        column_types = get_column_types(df)
        
        return render_template(
            'data/preview.html',
            dataset=dataset,
            preview_data=preview_data,
            columns=columns,
            column_types=column_types
        )
        
    except Exception as e:
        flash(f'Error loading preview: {str(e)}', 'error')
        return redirect(url_for('data.index'))

@data_bp.route('/delete/<int:dataset_id>', methods=['POST'])
def delete(dataset_id):
    """Delete a dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        # Delete the file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the database record
        db.session.delete(dataset)
        db.session.commit()
        
        flash('Dataset deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error deleting dataset: {str(e)}', 'error')
    
    return redirect(url_for('data.index'))

@data_bp.route('/analyze/<int:dataset_id>')
def analyze(dataset_id):
    """Analyze a dataset and show statistics"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.filename)
        
        if dataset.file_type == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Get detailed statistics
        analysis = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'column_stats': get_column_stats(df),
            'missing_data': df.isnull().sum().to_dict(),
            'correlation': df.select_dtypes(include=['number']).corr().to_dict() if not df.select_dtypes(include=['number']).empty else {}
        }
        
        return render_template('data/analyze.html', dataset=dataset, analysis=analysis)
        
    except Exception as e:
        flash(f'Error analyzing dataset: {str(e)}', 'error')
        return redirect(url_for('data.index'))

@data_bp.route('/download/<int:dataset_id>')
def download(dataset_id):
    """Download a dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        dataset.filename,
        as_attachment=True,
        download_name=dataset.original_filename
    )
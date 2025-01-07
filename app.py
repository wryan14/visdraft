from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visualizations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Visualization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    config = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('editor.html')

@app.route('/visualizations')
def list_visualizations():
    visualizations = Visualization.query.all()
    return render_template('list.html', visualizations=visualizations)

@app.route('/viz/new')
def new_visualization():
    return render_template('editor.html')

@app.route('/viz/<int:id>')
def edit_visualization(id):
    visualization = Visualization.query.get_or_404(id)
    return render_template('editor.html', visualization=visualization)

@app.route('/viz/save', methods=['POST'])
def save_visualization():
    try:
        data = request.json
        
        if 'id' in data and data['id']:
            # Update existing
            viz = Visualization.query.get_or_404(data['id'])
            viz.name = data['name']
            viz.description = data['description']
            viz.config = data['config']
            viz.updated_at = datetime.utcnow()
        else:
            # Create new
            viz = Visualization(
                name=data['name'],
                description=data['description'],
                config=data['config']
            )
            db.session.add(viz)
        
        db.session.commit()
        return jsonify({
            'id': viz.id,
            'message': 'Visualization saved successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': str(e)
        }), 400

@app.route('/viz/load/<int:id>')
def load_visualization(id):
    try:
        viz = Visualization.query.get_or_404(id)
        return jsonify({
            'id': viz.id,
            'name': viz.name,
            'description': viz.description,
            'config': viz.config
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 404

@app.route('/viz/delete/<int:id>', methods=['DELETE'])
def delete_visualization(id):
    try:
        viz = Visualization.query.get_or_404(id)
        db.session.delete(viz)
        db.session.commit()
        return jsonify({
            'message': 'Visualization deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': str(e)
        }), 400

@app.route('/viz/data/<path:filename>')
def get_data_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 404

# File upload handling
@app.route('/viz/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file part'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'No selected file'
            }), 400
        
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({
                'filename': filename,
                'message': 'File uploaded successfully'
            }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
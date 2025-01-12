# core/visualizations/routes.py

from flask import (
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    current_app,
    abort, url_for, flash, redirect
)
from werkzeug.utils import secure_filename
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
from core.models import db, Visualization

viz_bp = Blueprint("viz", __name__)

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(DATA_DIR, 'raw', 'uploaded')
SAVED_VIZ_DIR = os.path.join(BASE_DIR, 'saved_visualizations')


def allowed_file(filename: str) -> bool:
    """
    Checks if a filename has an allowed extension (csv, xlsx, xls by default).
    """
    allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", ["csv", "xlsx", "xls"])
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts


def load_dataframe(filepath: str, filename: str) -> pd.DataFrame:
    """
    Load a DataFrame from a CSV or Excel file at the given filepath.
    """
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filename.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file type")
    return df


@viz_bp.route("/files", methods=["GET"])
def list_files():
    """
    Lists all allowed CSV/Excel files in the data directory (DATA_DIR).
    This can be used to populate a dropdown of existing data sources.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    valid_files = []
    for fname in os.listdir(DATA_DIR):
        if allowed_file(fname):
            valid_files.append(fname)
    return jsonify({"files": valid_files})


@viz_bp.route("/upload", methods=["POST"])
def upload_data():
    """
    Handles file uploads with improved validation, error handling, and storage management.
    Returns JSON about the file (columns, row count, etc.) so the front-end
    can populate the UI.
    """
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
    MAX_STORAGE_SPACE = 500 * 1024 * 1024  # 500MB total storage limit

    if "file" not in request.files:
        return jsonify({"error": "No file was provided in the request"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Size validation
    if request.content_length > MAX_FILE_SIZE:
        return jsonify({"error": f"File size exceeds the maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Invalid file type. Supported formats are: " + 
            ", ".join(current_app.config.get("ALLOWED_EXTENSIONS", ["csv", "xlsx", "xls"]))
        }), 400

    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Check total storage usage
    total_size = sum(os.path.getsize(os.path.join(UPLOAD_DIR, f)) 
                    for f in os.listdir(UPLOAD_DIR) 
                    if os.path.isfile(os.path.join(UPLOAD_DIR, f)))
    if total_size + request.content_length > MAX_STORAGE_SPACE:
        return jsonify({"error": "Storage space limit exceeded. Please delete some files first."}), 400

    # Handle duplicate filenames
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{base}_{counter}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        counter += 1

    try:
        # Save the uploaded file
        file.save(filepath)

        # Load into a DataFrame to gather metadata and validate content
        df = load_dataframe(filepath, filename)
        
        # Basic data validation
        if len(df.columns) == 0:
            raise ValueError("File contains no columns")
        if len(df) == 0:
            raise ValueError("File contains no data rows")

        # Generate metadata
        columns = df.columns.tolist()
        dtypes = df.dtypes.astype(str).to_dict()
        preview_data = df.head(5).to_dict(orient="records")
        file_size = os.path.getsize(filepath)

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "columns": columns,
            "dtypes": dtypes,
            "row_count": len(df),
            "preview": preview_data,
            "file_size": file_size,
            "file_size_formatted": f"{file_size / (1024*1024):.2f}MB"
        })
    except Exception as e:
        # Clean up partially saved file if something goes wrong
        if os.path.exists(filepath):
            os.remove(filepath)
        
        error_message = str(e)
        if "memory" in error_message.lower():
            error_message = "File is too large to process. Please try a smaller file."
        elif "decode" in error_message.lower():
            error_message = "Unable to read file. Please ensure it's a valid CSV/Excel file with proper encoding."
            
        return jsonify({"error": f"Error processing file: {error_message}"}), 400


@viz_bp.route("/data/<path:filename>", methods=["GET"])
def get_data(filename: str):
    """
    Fetch columns and data for a selected file from ../data/raw/uploaded.
    Useful if the user picks from the dropdown or from a previously uploaded file.
    """
    try:
        safe_name = secure_filename(filename)
        filepath = os.path.join(UPLOAD_DIR, safe_name)
        if not os.path.exists(filepath):
            # Optionally check the main DATA_DIR as well
            alt_path = os.path.join(DATA_DIR, safe_name)
            if os.path.exists(alt_path):
                filepath = alt_path
            else:
                return jsonify({"error": f"File not found: {filename}"}), 404

        df = load_dataframe(filepath, safe_name)
        return jsonify({
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@viz_bp.route("/create", methods=["GET"])
def create():
    """
    Display visualization creation interface.
    """
    template_type = request.args.get("template", "time_series")
    filename = request.args.get("file", "")

    return render_template(
        "visualizations/create.html",
        template_type=template_type,
        filename=filename,
        plotly_config=current_app.config.get("PLOTLY_CONFIG", {}),
        visualization=None  # No existing visualization for create
    )

@viz_bp.route("/<int:viz_id>/edit", methods=["GET"])
def edit(viz_id):
    """
    Display visualization edit interface with existing visualization data.
    """
    visualization = Visualization.query.get_or_404(viz_id)
    
    try:
        # Ensure the config is valid JSON
        viz_config = json.loads(visualization.config) if visualization.config else {}
        
        return render_template(
            "visualizations/create.html",
            visualization={
                'id': visualization.id,
                'name': visualization.name,
                'description': visualization.description,
                'config': viz_config,
                'chart_type': visualization.chart_type,
                'source_file': visualization.source_file
            }
        )
    except json.JSONDecodeError:
        flash('Error loading visualization configuration', 'error')
        return redirect(url_for('index'))


# Supported chart types for demonstration
SUPPORTED_CHARTS = {
    "scatter": px.scatter,
    "line": px.line,
    "bar": px.bar,
    "area": px.area,
    "histogram": px.histogram,
    "box": px.box,
    "violin": px.violin
}


@viz_bp.route("/preview", methods=["POST"])
def preview():
    """
    Generate a visualization preview based on user-selected settings.
    Expects JSON with:
      - filename
      - vizType
      - xColumn
      - yColumn (optional for some chart types)
      - yAggregation (e.g., 'sum', 'avg', 'count', 'min', 'max', 'none')
      - groupBy (optional)
    """
    data = request.get_json() or {}
    filename = data.get("filename")
    viz_type = data.get("vizType")
    x_column = data.get("xColumn")
    y_column = data.get("yColumn")
    y_aggregation = data.get("yAggregation", "none")
    group_by_column = data.get("groupBy", "")
    top_n = data.get("topN", None)
    sort_column = data.get("sortColumn", "")
    sort_order = data.get("sortOrder", "asc")

    if not (filename and viz_type and x_column):
        return jsonify({"error": "Missing required parameters (filename, vizType, xColumn)."}), 400

    try:
        safe_name = secure_filename(filename)
        filepath = os.path.join(UPLOAD_DIR, safe_name)
        if not os.path.exists(filepath):
            alt_path = os.path.join(DATA_DIR, safe_name)
            if os.path.exists(alt_path):
                filepath = alt_path
            else:
                return jsonify({"error": f"File not found: {filename}"}), 404

        df = load_dataframe(filepath, safe_name)

        if viz_type not in SUPPORTED_CHARTS:
            return jsonify({"error": f"Unsupported visualization type: {viz_type}"}), 400

        if x_column not in df.columns:
            return jsonify({"error": f"Selected X column '{x_column}' not found in dataset."}), 400
        if y_column and y_column not in df.columns:
            return jsonify({"error": f"Selected Y column '{y_column}' not found in dataset."}), 400
        if group_by_column and group_by_column not in df.columns:
            return jsonify({"error": f"Group By column '{group_by_column}' not found in dataset."}), 400

        df_for_plot = df.copy()
        agg_map = {
            "none": None,
            "sum": "sum",
            "avg": "mean",
            "count": "count",
            "min": "min",
            "max": "max"
        }
        agg_func = agg_map.get(y_aggregation, None)

        # Aggregation Logic
        if y_column and agg_func:
            group_cols = [x_column]
            if group_by_column:
                group_cols.append(group_by_column)

            if y_aggregation == "count":
                df_agg = df_for_plot.groupby(group_cols).size().reset_index(name="Count")
                y_column = "Count"
            elif agg_func in ["sum", "mean", "min", "max"]:
                if not pd.api.types.is_numeric_dtype(df[y_column]):
                    return jsonify({"error": f"Y column '{y_column}' must be numerical for '{y_aggregation}' aggregation."}), 400
                df_agg = df_for_plot.groupby(group_cols)[y_column].agg(agg_func).reset_index()
                new_y_column_name = f"{y_column}_{y_aggregation}"
                df_agg.rename(columns={y_column: new_y_column_name}, inplace=True)
                y_column = new_y_column_name
            else:
                df_agg = df_for_plot
            df_for_plot = df_agg

        # Sort Logic
        if sort_column == "x_column":
            sort_column = x_column
        elif sort_column == "y_column" and y_column:
            sort_column = y_column
        elif sort_column == "count" and "Count" in df_for_plot.columns:
            sort_column = "Count"

        if sort_column and sort_column in df_for_plot.columns:
            ascending = True if sort_order == "asc" else False
            df_for_plot = df_for_plot.sort_values(by=sort_column, ascending=ascending)
        else:
            # Optional: Default sorting behavior
            df_for_plot = df_for_plot.sort_values(by=x_column, ascending=True)

        # Top N Logic
        if top_n is not None:
            try:
                top_n = int(top_n)
                if top_n <= 0:
                    return jsonify({"error": "Top N must be a positive integer."}), 400
            except ValueError:
                return jsonify({"error": "Top N must be a positive integer."}), 400

            # Limit the DataFrame to Top N rows
            df_for_plot = df_for_plot.head(top_n)

        # Build Plotly figure
        chart_func = SUPPORTED_CHARTS[viz_type]
        chart_kwargs = {"x": x_column}

        if y_column and y_column in df_for_plot.columns:
            chart_kwargs["y"] = y_column
        if group_by_column:
            chart_kwargs["color"] = group_by_column

        fig = chart_func(df_for_plot, **chart_kwargs, title=f"{viz_type.title()} Chart")
        fig_json = json.loads(fig.to_json())
        return jsonify({"chartData": fig_json})

    except Exception as e:
        return jsonify({"error": f"Failed to generate preview: {str(e)}"}), 500


# In routes.py, add the index route and update the save route:

@viz_bp.route("/", methods=["GET"])
def index():
    """
    Display the visualization index page with all saved visualizations.
    """
    visualizations = Visualization.query.order_by(Visualization.updated_at.desc()).all()
    return render_template(
        "visualizations/index.html",
        recent_vizs=visualizations
    )

@viz_bp.route('/save', methods=['POST'])
def save_viz():
    """
    Saves or updates a visualization with metadata and Plotly configuration.
    """
    payload = request.json
    viz_id = payload.get('id')
    name = payload.get('name', 'Untitled')
    description = payload.get('description', '')
    filename = payload.get('filename')
    config = payload.get('config')
    chart_type = payload.get('chart_type', 'custom')

    if not config:
        return jsonify({'error': 'Missing visualization configuration'}), 400

    try:
        # Ensure the config is valid JSON
        config_str = json.dumps(config)
        
        if viz_id:
            # Update existing visualization
            visualization = Visualization.query.get_or_404(viz_id)
            visualization.name = name
            visualization.description = description
            visualization.config = config_str
            visualization.chart_type = chart_type
            visualization.source_file = filename
        else:
            # Create new visualization
            visualization = Visualization(
                name=name,
                description=description,
                config=config_str,
                chart_type=chart_type,
                source_file=filename
            )
            db.session.add(visualization)

        db.session.commit()

        return jsonify({
            'success': True,
            'id': visualization.id,
            'message': 'Visualization saved successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@viz_bp.route('/<int:viz_id>', methods=['GET'])
def get_visualization(viz_id):
    """Get a specific visualization by ID"""
    visualization = Visualization.query.get_or_404(viz_id)
    return jsonify(visualization.to_dict())

@viz_bp.route('/<int:viz_id>', methods=['DELETE'])
def delete_visualization(viz_id):
    """Delete a specific visualization"""
    visualization = Visualization.query.get_or_404(viz_id)
    try:
        db.session.delete(visualization)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Visualization deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@viz_bp.route('/list', methods=['GET'])
def list_visualizations():
    """Get all saved visualizations"""
    visualizations = Visualization.query.order_by(Visualization.updated_at.desc()).all()
    return jsonify({
        'visualizations': [viz.to_dict() for viz in visualizations]
    })

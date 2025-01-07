# core/visualizations/routes.py

from flask import (
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    current_app
)
from werkzeug.utils import secure_filename
import pandas as pd
import plotly.express as px
import json
import os

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
    Handles file uploads and places them in ../data/raw/uploaded.
    Returns JSON about the file (columns, row count, etc.) so the front-end
    can populate the UI.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        # Save the uploaded file
        file.save(filepath)

        # Load into a DataFrame to gather metadata
        df = load_dataframe(filepath, filename)
        columns = df.columns.tolist()
        dtypes = df.dtypes.astype(str).to_dict()
        preview_data = df.head(5).to_dict(orient="records")

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "columns": columns,
            "dtypes": dtypes,
            "row_count": len(df),
            "preview": preview_data
        })
    except Exception as e:
        # Clean up partially saved file if something goes wrong
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": f"Error processing file: {str(e)}"}), 400


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
        plotly_config=current_app.config.get("PLOTLY_CONFIG", {})
    )


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


@viz_bp.route('/viz/save', methods=['POST'])
def save_viz():
    """
    Saves a visualization's Plotly config (data + layout) plus metadata like
    vizName, vizDescription, and the original filename reference.
    Stores each saved visualization in ../saved_visualizations/<vizName>.json
    """
    payload = request.json
    filename = payload.get('filename')
    config = payload.get('config')  # Contains 'data' and 'layout'
    viz_name = payload.get('vizName') or "Untitled"
    viz_description = payload.get('vizDescription') or ""

    if not filename or not config:
        return jsonify({'error': 'Missing filename or config'}), 400

    try:
        # Validate the JSON structure
        json.dumps(config)  # will raise TypeError if not serializable
    except TypeError as e:
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

    # Wrap the Plotly config with metadata
    record = {
        "filename": filename,
        "vizName": viz_name,
        "vizDescription": viz_description,
        "plotlyConfig": config
    }

    os.makedirs(SAVED_VIZ_DIR, exist_ok=True)
    save_path = os.path.join(SAVED_VIZ_DIR, f'{viz_name}.json')

    with open(save_path, 'w') as f:
        json.dump(record, f, indent=4)

    return jsonify({
        'message': 'Visualization saved successfully',
        'path': save_path,
        'metadata': {
            'vizName': viz_name,
            'vizDescription': viz_description
        }
    }), 200


@viz_bp.route('/viz/get/<viz_name>', methods=['GET'])
def get_saved_viz(viz_name):
    """
    Returns the saved visualization JSON, including plotlyConfig, name, description, etc.
    """
    os.makedirs(SAVED_VIZ_DIR, exist_ok=True)
    save_path = os.path.join(SAVED_VIZ_DIR, f'{viz_name}.json')
    if not os.path.exists(save_path):
        return jsonify({"error": f"No saved visualization found for {viz_name}"}), 404

    with open(save_path, 'r') as f:
        record = json.load(f)

    return jsonify(record), 200

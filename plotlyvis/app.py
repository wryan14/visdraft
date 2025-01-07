import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from pythonjsonlogger import jsonlogger

# Initialize Flask app
app = Flask(__name__)

# Configure JSON logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Configure data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route("/")
def index():
    """Render the main visualization editor page."""
    return render_template("index.html")

@app.route("/api/configs", methods=["GET"])
def list_configs():
    """List all saved configurations."""
    try:
        configs = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(DATA_DIR, filename)) as f:
                    config = json.load(f)
                    configs.append({
                        "name": filename[:-5],
                        "type": config.get("data", [{}])[0].get("type", "unknown"),
                        "last_modified": datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(DATA_DIR, filename))
                        ).isoformat()
                    })
        return jsonify({"status": "success", "configs": configs})
    except Exception as e:
        logger.error("Error listing configurations", extra={"error": str(e)})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/configs/<name>", methods=["GET"])
def get_config(name):
    """Get a specific configuration."""
    try:
        filepath = os.path.join(DATA_DIR, f"{name}.json")
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "Configuration not found"}), 404
        
        with open(filepath) as f:
            config = json.load(f)
        return jsonify({"status": "success", "config": config})
    except Exception as e:
        logger.error("Error loading configuration", extra={"error": str(e), "name": name})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/configs/<name>", methods=["POST"])
def save_config(name):
    """Save or update a configuration."""
    try:
        config = request.json
        if not config:
            return jsonify({"status": "error", "message": "No configuration provided"}), 400
        
        filepath = os.path.join(DATA_DIR, f"{name}.json")
        with open(filepath, "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info("Configuration saved", extra={"name": name})
        return jsonify({"status": "success", "message": "Configuration saved successfully"})
    except Exception as e:
        logger.error("Error saving configuration", extra={"error": str(e), "name": name})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/configs/<name>", methods=["DELETE"])
def delete_config(name):
    """Delete a configuration."""
    try:
        filepath = os.path.join(DATA_DIR, f"{name}.json")
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "Configuration not found"}), 404
        
        os.remove(filepath)
        logger.info("Configuration deleted", extra={"name": name})
        return jsonify({"status": "success", "message": "Configuration deleted successfully"})
    except Exception as e:
        logger.error("Error deleting configuration", extra={"error": str(e), "name": name})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/search", methods=["GET"])
def search_configs():
    """Search configurations by name or type."""
    try:
        query = request.args.get("q", "").lower()
        configs = []
        
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(DATA_DIR, filename)) as f:
                    config = json.load(f)
                    name = filename[:-5]
                    plot_type = config.get("data", [{}])[0].get("type", "unknown")
                    
                    if query in name.lower() or query in plot_type.lower():
                        configs.append({
                            "name": name,
                            "type": plot_type,
                            "last_modified": datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(DATA_DIR, filename))
                            ).isoformat()
                        })
        
        return jsonify({"status": "success", "configs": configs})
    except Exception as e:
        logger.error("Error searching configurations", extra={"error": str(e), "query": query})
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

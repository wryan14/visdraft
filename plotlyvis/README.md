# PlotlyVis - Interactive Plotly Visualization Editor

PlotlyVis is a lightweight, user-friendly web application for creating, editing, and managing Plotly visualizations. It provides an interactive environment where you can edit Plotly configurations in real-time and see the results immediately.

## Features

- **Interactive Editor**: Built-in code editor with syntax highlighting and error checking
- **Real-time Preview**: See your visualization changes instantly
- **Configuration Management**: Save, load, and manage your Plotly configurations
- **Search Functionality**: Quick search through saved configurations
- **No Dependencies**: No NPM or additional JavaScript installations required
- **Production Ready**: Includes error handling, logging, and a clean interface

## Requirements

- Python 3.7+
- Required Python packages (install via requirements.txt):
  - Flask
  - Plotly
  - Pandas
  - NumPy
  - python-json-logger

## Installation

1. Clone or download the repository to your local machine

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. The interface consists of:
   - Top bar: Search configurations and save controls
   - Left sidebar: List of saved configurations
   - Middle: JSON editor for Plotly configuration
   - Right: Live visualization preview

4. Creating a Visualization:
   - Edit the JSON configuration in the editor
   - Click "Update Preview" to see your changes
   - Enter a name and click "Save" to store your configuration

5. Managing Configurations:
   - Use the search bar to find specific configurations
   - Click on a configuration to load it
   - Use the delete button to remove configurations

## Configuration Format

The editor expects a Plotly configuration in JSON format:

```json
{
    "data": [
        {
            "type": "scatter",
            "x": [1, 2, 3, 4],
            "y": [10, 15, 13, 17],
            "mode": "lines+markers"
        }
    ],
    "layout": {
        "title": "Sample Plot",
        "xaxis": {
            "title": "X Axis"
        },
        "yaxis": {
            "title": "Y Axis"
        }
    }
}
```

## File Structure

```
plotlyvis/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/
│   │   └── styles.css # Application styling
│   └── js/
│       └── main.js    # Frontend JavaScript
├── templates/
│   └── index.html     # Main interface template
└── data/              # Configuration storage directory
```

## Production Deployment

For production deployment:

1. Set `debug=False` in app.py

2. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn app:app
```

3. Consider setting up:
   - Reverse proxy (e.g., Nginx) for static files and SSL
   - Environment variables for configuration
   - Backup solution for the data directory

## Data Storage

Configurations are stored as JSON files in the `data` directory. Each configuration is saved as a separate file with the format `<name>.json`.

## Logging

The application uses JSON logging for structured output. Logs include:
- Configuration saves/loads
- Error events
- Search operations

## Security Considerations

- Input validation for configuration names
- JSON validation for configurations
- No external JavaScript dependencies
- Static file handling through Flask

## Browser Compatibility

Tested and compatible with:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Known Limitations

- Stores configurations as files (not recommended for very large numbers of configurations)
- Single-user design (no authentication)
- Limited to Plotly chart types available in plotly.js

## Support

For issues, questions, or contributions, please create an issue in the repository.

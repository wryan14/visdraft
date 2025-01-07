# Plotly Visualization Editor

A user-friendly interface for creating, customizing, and managing Plotly visualizations. This application provides an intuitive form-based approach to building charts while maintaining access to Plotly's powerful customization options.

## Features

- Interactive visualization preview
- Form-based configuration
- Support for multiple chart types
- Advanced data processing options
- Configuration save/load functionality
- Responsive design
- Error handling and validation
- Auto-save capability
- Undo/redo functionality

## Project Structure

```
newvis/
├── static/
│   ├── css/
│   │   ├── main.css
│   │   └── components/
│   ├── js/
│   │   ├── modules/
│   │   │   ├── visualization-state.js
│   │   │   ├── plotly-manager.js
│   │   │   ├── file-manager.js
│   │   │   ├── ui-manager.js
│   │   │   └── utils/
│   │   └── visualization-editor.js
│   └── assets/
├── templates/
│   ├── base.html
│   ├── editor.html
│   └── components/
├── core/
│   ├── __init__.py
│   ├── routes.py
│   └── services/
├── config/
│   ├── __init__.py
│   └── settings.py
├── instance/
├── tests/
│   ├── __init__.py
│   ├── test_visualization.py
│   └── test_data/
├── README.md
├── requirements.txt
└── wsgi.py
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

## Usage

1. Start the development server:
   ```bash
   python wsgi.py
   ```
2. Navigate to `http://localhost:5000` in your browser
3. Use the form interface to configure your visualization
4. Preview changes in real-time
5. Save configurations for later use

## Development

### Frontend Development

The frontend is built using vanilla JavaScript with modules for maintainability. Key components:

- `VisualizationEditor`: Main class orchestrating the editor functionality
- `VisualizationState`: Manages application state and configuration
- `PlotlyManager`: Handles Plotly chart rendering and interactions
- `FileManager`: Manages file operations and data loading
- `UIManager`: Handles UI updates and form interactions

### Backend Development

The backend is built with Flask and provides:

- Configuration storage and retrieval
- Data processing services
- File upload handling
- API endpoints for saving/loading visualizations

## API Documentation

### Endpoints

- `GET /api/visualizations`: List saved visualizations
- `GET /api/visualizations/<id>`: Get specific visualization
- `POST /api/visualizations`: Create new visualization
- `PUT /api/visualizations/<id>`: Update existing visualization
- `DELETE /api/visualizations/<id>`: Delete visualization

### Configuration Format

```javascript
{
  "id": "unique-id",
  "name": "Visualization Name",
  "description": "Description",
  "config": {
    "type": "line",
    "mapping": {
      "x": "column1",
      "y": "column2",
      "groupBy": "column3",
      "aggregation": "sum"
    },
    "advanced": {
      "sortBy": "column1",
      "sortDirection": "asc",
      "topN": 10,
      "filters": []
    },
    "plotly": {
      // Plotly-specific configuration
    }
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details
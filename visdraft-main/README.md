# PlotlyVis Editor

A powerful web application for creating, editing, and managing Plotly visualizations with an intuitive interface.

## Features

- **Interactive Visualization Editor**
  - Create and customize Plotly charts with a user-friendly interface
  - Real-time preview of changes
  - Support for multiple chart types (line, bar, scatter, pie, etc.)
  - Advanced configuration options through JSON editor

- **Data Management**
  - Upload and manage CSV and Excel files
  - Preview and analyze datasets
  - Column type detection and statistics
  - Data filtering and aggregation capabilities

- **Template System**
  - Save and reuse visualization configurations
  - Pre-built templates for common chart types
  - Customizable template categories

- **Modern UI/UX**
  - Clean, responsive design using Tailwind CSS
  - Drag-and-drop file uploads
  - Interactive data mapping interface
  - Real-time validation and feedback

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/plotlyvis.git
   cd plotlyvis/testvis2
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create required directories:
   ```bash
   mkdir -p uploads instance
   ```

## Configuration

1. Set up environment variables:
   ```bash
   export FLASK_APP=core.app:create_app
   export FLASK_ENV=development  # Use 'production' for production deployment
   ```

2. Configure the database:
   - The application uses SQLite by default
   - For production, set `DATABASE_URL` environment variable to your database URI
   - To use Redis for session management (optional):
     ```bash
     export REDIS_URL=redis://localhost:6379
     ```

## Running the Application

1. Initialize the database:
   ```bash
   flask db upgrade
   ```

2. Start the development server:
   ```bash
   flask run
   ```

3. Access the application at `http://localhost:5000`

## Project Structure

```
testvis2/
├── core/
│   ├── __init__.py
│   ├── app.py              # Application factory
│   ├── models.py           # Database models
│   ├── data/               # Data management module
│   │   ├── __init__.py
│   │   └── routes.py
│   └── visualizations/     # Visualization module
│       ├── __init__.py
│       ├── routes.py
│       └── helpers.py
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Dashboard
│   ├── data/              # Data management templates
│   │   ├── index.html
│   │   └── preview.html
│   └── visualizations/    # Visualization templates
│       └── create.html
├── static/
│   ├── css/
│   └── js/
├── instance/             # Instance-specific files
├── uploads/             # Data file uploads
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
└── wsgi.py            # WSGI entry point
```

## Usage

1. **Upload Data**
   - Click "Upload Dataset" on the dashboard
   - Drag and drop or select a CSV/Excel file
   - Preview and verify the data

2. **Create Visualization**
   - Click "Create New" on the dashboard
   - Select a data source
   - Choose chart type and map columns
   - Customize appearance and settings
   - Preview and save

3. **Templates**
   - Save commonly used configurations as templates
   - Access templates from the gallery
   - Apply templates to new datasets

## Development

### Adding New Chart Types

1. Add chart configuration in `config.py`:
   ```python
   CHART_TYPES = {
       'new_chart': {
           'name': 'New Chart Type',
           'description': 'Description of the chart',
           'required_fields': ['x', 'y'],
           'optional_fields': ['color', 'size'],
           'aggregations': ['sum', 'average']
       }
   }
   ```

2. Implement chart creation in `helpers.py`:
   ```python
   def create_plotly_figure(...):
       if viz_type == 'new_chart':
           return px.new_chart(...)
   ```

### Custom Data Processing

Add new data processing functions in `core/data/processors.py`:
```python
def process_data(df, processing_type, **kwargs):
    # Implement custom data processing
    return processed_df
```

## Production Deployment

1. Set production configuration:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   export DATABASE_URL=your-database-url
   ```

2. Set up a production server (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn "core.app:create_app()"
   ```

3. Configure reverse proxy (e.g., Nginx)

4. Set up SSL/TLS certificates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use and modify as needed.

## Support

- Create an issue for bug reports or feature requests
- Check the wiki for additional documentation
- Contact: your.email@example.com
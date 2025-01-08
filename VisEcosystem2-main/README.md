# VisEcosystem

A simple but powerful tool for creating and managing data visualizations. Built with Flask, Plotly, and modern web technologies.

## What is it?

VisEcosystem helps you:
- Upload and manage datasets (CSV, Excel)
- Create interactive visualizations
- Customize charts with a code editor
- Organize visualizations by category
- Preview data before visualizing

## Getting Started

1. Install the requirements:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python run.py
```

3. Visit http://localhost:5000 in your browser

## Basic Features

- **Create Visualizations**: Start from scratch with various chart types
- **Manage Datasets**: Upload, preview, and manage your data files
- **Interactive Editor**: Use the built-in code editor to customize your visualizations
- **Live Preview**: See your changes in real-time

## File Structure
```
/static
  /css
    style.css                 # Custom styles
  /js
    chart-config.js          # Chart configurations
    main.js                  # Core JavaScript
/templates
    base.html               # Base template
    index.html             # Homepage
    visualizations/        # Visualization templates
    datasets.html         # Dataset management
/uploads                   # Where datasets are stored
app.py                    # Main Flask application
models.py                 # Database models
run.py                   # Application entry point
```

## Tips

- Use the dataset preview to verify your data before creating visualizations
- The code editor supports all Plotly configuration options
- Categories help organize related visualizations
- The "View All" page shows visualizations grouped by category

## Notes

- All data is stored locally in an SQLite database
- File uploads are limited to 16MB
- Supported file formats: CSV, XLSX, XLS

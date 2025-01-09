# API Registration Guide

This guide explains how to register new APIs in the API Ecosystem project.

## Directory Structure

Every API must follow this structure:

```
apis/
└── your_api_name/
    ├── __init__.py
    ├── routes.py
    └── utils.py (optional)
```

## Step 1: Create API Directory Structure

1. Create a new directory under `apis/` with your API name:
   ```bash
   mkdir -p apis/your_api_name
   ```

2. Create the required files:
   - `__init__.py`: Exports the Blueprint
   - `routes.py`: Contains your API endpoints
   - `utils.py`: Optional, contains helper functions

## Step 2: Create API Blueprint

In `routes.py`:

```python
from flask import Blueprint, request, jsonify, render_template

bp = Blueprint('your_api_name', __name__)

@bp.route('/')
def index():
    return render_template('apis/your_api_name/index.html')

# Add more routes as needed
```

In `__init__.py`:

```python
from .routes import bp
```

## Step 3: Create Template

Create a template directory and file:

```bash
mkdir -p shared/templates/apis/your_api_name
touch shared/templates/apis/your_api_name/index.html
```

Template should extend the base template:

```html
{% extends "base.html" %}

{% block content %}
    <!-- Your API interface here -->
{% endblock %}
```

## Step 4: Register the API

Add your API configuration to `config/default.py`:

```python
API_REGISTRY_CONFIG = {
    'your_api_name': {
        'name': 'Your API Name',
        'description': 'Brief description of your API',
        'version': '1.0.0',
        'routes': ['/', '/your-endpoint'],
        'url_prefix': '/api/your-api-name',
        'interface': {
            'icon': 'icon-name',  # Choose from available icons
            'accepted_files': '.ext1, .ext2',  # If API accepts files
            'parameter_fields': ['param1', 'param2'],
            'result_display': 'json'  # or 'table', 'text'
        }
    }
}
```

## Step 5: Test the API

1. Restart the application
2. Navigate to your API's endpoint: `/api/your-api-name`
3. Test all endpoints and functionality
4. Verify error handling

## Best Practices

1. **Documentation**: Document all routes and functions
2. **Error Handling**: Implement proper error handling and return appropriate status codes
3. **Validation**: Validate all input parameters
4. **Templates**: Use consistent styling by extending base templates
5. **Configuration**: Keep configuration in `config/default.py`

## Example API Structure

Here's a minimal example:

```python
# routes.py
from flask import Blueprint, jsonify

bp = Blueprint('example', __name__)

@bp.route('/')
def index():
    return render_template('apis/example/index.html')

@bp.route('/process', methods=['POST'])
def process():
    try:
        # Process data
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Additional Notes

- Test your API thoroughly before deployment
- Follow existing API patterns in the project
- Use appropriate HTTP methods (GET, POST, etc.)
- Implement proper security measures
- Keep the interface user-friendly
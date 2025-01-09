# Simple Guide to Adding a New API

This guide will help you add a new feature (API) to the system in simple steps.

## What is an API?
Think of an API like a new feature or tool in the system. For example, if you want to add a tool that processes documents or analyzes images, that would be a new API.

## Step-by-Step Guide

### Step 1: Create Your Feature's Home
1. Go to the `apis` folder in the project
2. Create a new folder with your feature's name
   - Use simple, descriptive names like `document_processor` or `image_analyzer`
   - Avoid spaces (use underscores instead)

### Step 2: Create Required Files
In your new folder, create these three files:
1. `__init__.py` - Just create it empty
2. `routes.py` - This will handle your feature's web pages
3. `utils.py` - This will contain your feature's main functions

### Step 3: Create Your Feature's Webpage
1. Go to `shared/templates/apis`
2. Create a new folder with the same name as your API
3. Create `index.html` in this folder for your feature's main page

### Step 4: Register Your Feature
Add your feature to the system by editing `config/default.py`:
1. Open the file
2. Find the `API_REGISTRY_CONFIG` section
3. Add your feature's information like this:
```python
'your_feature_name': {
    'name': 'Your Feature's Display Name',
    'description': 'What your feature does',
    'version': '1.0.0',
    'routes': ['/'],
    'url_prefix': '/api/your-feature-name',
    'interface': {
        'icon': 'file',  # Choose an icon name
        'parameter_fields': ['field1', 'field2'],
        'result_display': 'text'
    }
}
```

## Real Example
Let's say you're adding a document processor:

1. Create folder: `apis/document_processor`
2. Create the files:
   - `__init__.py` (empty file)
   - `routes.py` (for web pages)
   - `utils.py` (for functions)
3. Create webpage folder: `shared/templates/apis/document_processor`
4. Add to config:
```python
'document_processor': {
    'name': 'Document Processor',
    'description': 'Process and organize documents',
    'version': '1.0.0',
    'routes': ['/'],
    'url_prefix': '/api/document-processor',
    'interface': {
        'icon': 'file',
        'parameter_fields': ['document_name'],
        'result_display': 'text'
    }
}
```

That's it! Your new feature is now part of the system. Ask a developer to help you with the specific code needed for your feature's functionality.
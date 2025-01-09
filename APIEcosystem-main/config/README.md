# README: API Ecosystem Framework

## Overview

This project implements a modular and extensible API ecosystem framework using Flask. It enables efficient registration, configuration, and management of APIs with a centralized approach. The framework is designed for scalability, maintainability, and ease of use, supporting both backend logic and frontend UI elements.

---

## Key Features
- **Dynamic API Registration**: APIs are registered with detailed configurations, including routes, descriptions, and UI elements.
- **Blueprint Integration**: Supports Flask Blueprints for modularity and separation of concerns.
- **Centralized API Management**: The `APIRegistry` class provides an interface for registering, retrieving, and managing APIs in a consistent format.
- **Built-in Configuration Management**: Combines global, instance-specific, and API-specific settings.

---

## Components

### **`APIConfig` and `InterfaceConfig`**
- **`APIConfig`**: Defines each API's name, description, version, routes, URL prefix, and user interface details.
- **`InterfaceConfig`**: Specifies UI details, including icons, accepted file types, parameter fields, and result display formats.

### **`APIRegistry`**
Centralized registry to manage API configurations:
- **Register APIs**: Adds APIs using structured dictionary configurations.
- **Retrieve APIs**: Fetches individual or all registered APIs for dynamic routing or documentation purposes.

### **Global Configuration**
The `config/default.py` file centralizes project-wide settings:
- **Debug and Secret Key**: Configures Flask app behavior and security settings.
- **API Configurations**: Combines API-specific configurations into a single registry (`API_REGISTRY_CONFIG`), ensuring consistency.
- **File Upload Settings**:
  - **`UPLOAD_FOLDER`**: Directory for file uploads.
  - **`MAX_CONTENT_LENGTH`**: Maximum file size (16 MB).
  - **`ALLOWED_EXTENSIONS`**: Permitted file extensions for uploads.

---

## Usage

### **Registering an API**
To register an API, use the `APIRegistry` and a structured configuration dictionary. For example:
```python
from config.api_registry import APIRegistry

registry = APIRegistry()

registry.register({
    'name': 'data_transformation',
    'description': 'Transform and process tabular data',
    'version': '1.0.0',
    'routes': ['/', '/upload', '/process'],
    'url_prefix': '/api/data-transformation',
    'interface': {
        'icon': 'database',
        'accepted_files': '.csv, .xlsx, .json',
        'parameter_fields': ['delimiter', 'encoding', 'transformationType'],
        'result_display': 'table'
    }
})
```

### **Adding New APIs**
To add a new API:
1. Define its configuration in `config/default.py` under `API_REGISTRY_CONFIG`.
2. Register the API in the registry:
   ```python
   registry.register(API_REGISTRY_CONFIG['document_processing'])
   ```

3. Add the corresponding Flask Blueprint and logic in the appropriate `apis` module directory.

### **File Upload and Validation**
- Upload settings, such as the allowed file types and maximum upload size, are configured globally in `config/default.py`.
- Each API can implement custom file validation and transformation logic using its registered routes.

---

## Benefits
- **Modularity**: Each API is managed independently, allowing for better code organization.
- **Scalability**: APIs can be added or modified without impacting the existing ecosystem.
- **User-Friendly Interface**: UI settings ensure a consistent and intuitive experience for interacting with APIs.
- **Security and Limits**: Centralized settings for file uploads and size restrictions help enforce best practices.

This framework is ideal for managing a growing API ecosystem with clear separation of concerns and robust configuration management.
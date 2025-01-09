# documentation/utils.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class EndpointDoc:
    """Documentation for an API endpoint"""
    path: str
    method: str
    description: str
    parameters: Dict[str, str]  # parameter_name: description
    response_format: str
    example_request: Optional[Dict] = None
    example_response: Optional[Dict] = None

@dataclass
class APIDocumentation:
    """Complete API documentation"""
    name: str
    description: str
    version: str
    accepted_files: str
    parameters: Dict[str, str]  # parameter_name: description
    endpoints: List[EndpointDoc]
    examples: List[Dict]  # List of example usage scenarios
    notes: Optional[str] = None

class DocumentationSystem:
    def __init__(self, app=None):
        self.app = app
        self.api_docs: Dict[str, APIDocumentation] = {}

    def init_app(self, app):
        """Initialize with Flask app to access API registry"""
        self.app = app
        self._generate_documentation()

    def _generate_documentation(self):
        """Generate documentation from API registry"""
        api_registry = self.app.config.get('API_REGISTRY_CONFIG', {})
        
        for api_name, config in api_registry.items():
            # Generate standard endpoints documentation
            endpoints = [
                EndpointDoc(
                    path=f"/api/{api_name}/",
                    method="GET",
                    description="API interface endpoint",
                    parameters={},
                    response_format="HTML Interface"
                ),
                EndpointDoc(
                    path=f"/api/{api_name}/upload",
                    method="POST",
                    description="File upload endpoint",
                    parameters={
                        "file": "File to be processed (multipart/form-data)"
                    },
                    response_format="JSON",
                    example_response={"filename": "uploaded_file.csv"}
                ),
                EndpointDoc(
                    path=f"/api/{api_name}/process",
                    method="POST",
                    description="Process uploaded files",
                    parameters={
                        "files": "List of uploaded filenames",
                        "parameters": "Processing parameters"
                    },
                    response_format="JSON",
                    example_request={
                        "files": ["example.csv"],
                        "parameters": {
                            param: "value" 
                            for param in config['interface'].parameter_fields
                        }
                    }
                )
            ]

            # Create API documentation
            self.api_docs[api_name] = APIDocumentation(
                name=config['name'],
                description=config['description'],
                version=config['version'],
                accepted_files=config['interface'].accepted_files,
                parameters={
                    param: f"Parameter description for {param}"
                    for param in config['interface'].parameter_fields
                },
                endpoints=endpoints,
                examples=[{
                    "title": "Basic Usage",
                    "description": f"Example of using the {config['name']}",
                    "steps": [
                        "Upload a file using the interface",
                        "Configure processing parameters",
                        "Click Process to start processing"
                    ]
                }]
            )

    def get_api_doc(self, api_name: str) -> Optional[APIDocumentation]:
        """Get documentation for specific API"""
        return self.api_docs.get(api_name)

    def search_documentation(self, query: str) -> Dict[str, List[APIDocumentation]]:
        """Search through API documentation"""
        query = query.lower()
        results = []
        
        for doc in self.api_docs.values():
            if (query in doc.name.lower() or 
                query in doc.description.lower() or
                any(query in param.lower() for param in doc.parameters.keys())):
                results.append(doc)
        
        return {'apis': results}
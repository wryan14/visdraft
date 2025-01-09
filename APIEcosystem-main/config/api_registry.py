# config/api_registry.py
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class InterfaceConfig:
    icon: str
    accepted_files: str
    parameter_fields: List[str]
    result_display: str

@dataclass
class APIConfig:
    name: str
    description: str
    version: str
    routes: List[str]
    url_prefix: str
    interface: InterfaceConfig
    template_folder: Optional[Path] = None
    static_folder: Optional[Path] = None
    
    def get_blueprint_config(self):
        return {
            'template_folder': str(self.template_folder) if self.template_folder else None,
            'static_folder': str(self.static_folder) if self.static_folder else None,
            'url_prefix': self.url_prefix
        }

    @classmethod
    def from_dict(cls, data: dict):
        # Convert interface dict to InterfaceConfig
        if 'interface' in data:
            data['interface'] = InterfaceConfig(**data['interface'])
        return cls(**data)

class APIRegistry:
    def __init__(self):
        self._apis: Dict[str, APIConfig] = {}
        
    def register(self, config: dict):
        """Register an API using a dictionary configuration"""
        api_config = APIConfig.from_dict(config)
        self._apis[api_config.name] = api_config
        
    def get_api(self, name: str) -> Optional[APIConfig]:
        return self._apis.get(name)
        
    def get_all_apis(self) -> Dict[str, APIConfig]:
        return self._apis.copy()
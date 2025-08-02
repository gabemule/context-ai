"""
Generic YAML loading utilities for Context-AI.

Provides reusable YAML loading functionality without configuration-specific logic.
Following Single Responsibility Principle (SRP).
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from utils.logging import get_logger


class GenericYAMLLoader:
    """
    Generic YAML file loader with error handling.
    
    Provides common YAML loading functionality that can be reused
    across different modules without coupling to specific configurations.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def load(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse YAML file with comprehensive error handling.
        
        Args:
            file_path: Path to YAML file to load
            
        Returns:
            Parsed YAML data as dictionary, None if loading fails
        """
        if not file_path.exists():
            self.logger.debug("YAML file not found: %s", file_path)
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data is None:
                self.logger.warning("YAML file is empty: %s", file_path)
                return {}
            
            if not isinstance(data, dict):
                self.logger.error("Invalid YAML structure in %s: expected dict, got %s", 
                                file_path, type(data).__name__)
                return None
            
            self.logger.debug("Loaded YAML: %s (%d keys)", file_path.name, len(data))
            return data
            
        except yaml.YAMLError as e:
            self.logger.error("Invalid YAML syntax in %s: %s", file_path, e)
            return None
        except (OSError, IOError) as e:
            self.logger.error("Failed to read YAML file %s: %s", file_path, e)
            return None
        except Exception as e:
            self.logger.error("Unexpected error loading YAML %s: %s", file_path, e)
            return None
    
    def save(self, data: Dict[str, Any], file_path: Path, 
             indent: int = 2, default_flow_style: bool = False) -> bool:
        """
        Save dictionary data to YAML file.
        
        Args:
            data: Dictionary data to save
            file_path: Path where to save the YAML file
            indent: YAML indentation level
            default_flow_style: Whether to use flow style formatting
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, 
                         indent=indent, 
                         default_flow_style=default_flow_style,
                         allow_unicode=True,
                         sort_keys=False)
            
            self.logger.debug("Saved YAML: %s (%d keys)", file_path.name, len(data))
            return True
            
        except (OSError, IOError) as e:
            self.logger.error("Failed to write YAML file %s: %s", file_path, e)
            return False
        except Exception as e:
            self.logger.error("Unexpected error saving YAML %s: %s", file_path, e)
            return False
    
    def validate_structure(self, data: Dict[str, Any], required_keys: list) -> bool:
        """
        Validate that YAML data contains required keys.
        
        Args:
            data: Parsed YAML data
            required_keys: List of required key names
            
        Returns:
            True if all required keys present, False otherwise
        """
        if not isinstance(data, dict):
            self.logger.error("Invalid data type for validation: expected dict, got %s", 
                            type(data).__name__)
            return False
        
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            self.logger.error("Missing required keys in YAML: %s", missing_keys)
            return False
        
        return True


# Global instance for convenience
_yaml_loader: Optional[GenericYAMLLoader] = None


def get_yaml_loader() -> GenericYAMLLoader:
    """Get global YAML loader instance."""
    global _yaml_loader
    if _yaml_loader is None:
        _yaml_loader = GenericYAMLLoader()
    return _yaml_loader

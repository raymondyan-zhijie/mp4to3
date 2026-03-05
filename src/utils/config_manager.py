"""
Configuration manager for MP4 to MP3 converter
Handles saving and loading user preferences
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration and user preferences"""
    
    def __init__(self, config_file: str = None):
        """
        Initialize the configuration manager
        
        Args:
            config_file: Path to the config file. If None, uses default location
        """
        if config_file is None:
            app_data_dir = Path(os.getenv('APPDATA')) / 'MP4to3'
            app_data_dir.mkdir(exist_ok=True)
            self.config_file = app_data_dir / 'config.json'
        else:
            self.config_file = Path(config_file)
            
        self.config = self._get_default_config()
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            'bitrate': '192k',
            'output_dir': os.path.expanduser("~\\Music"),
            'window_size': 'maximized',
            'theme': 'cosmo'
        }
    
    def load_config(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if config was loaded successfully, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
        
        return False
    
    def save_config(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if config was saved successfully, False otherwise
        """
        try:
            # Create parent directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save_config()
    
    def update(self, values: Dict[str, Any]) -> None:
        """
        Update multiple configuration values
        
        Args:
            values: Dictionary of key-value pairs to update
        """
        self.config.update(values)
        self.save_config()
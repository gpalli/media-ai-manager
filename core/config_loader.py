#!/usr/bin/env python3
"""
Configuration loader for MediaMind AI.
Handles loading and validation of configuration from YAML file.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigLoader:
    """Configuration loader for MediaMind AI."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file {self.config_path} not found, using defaults")
                return self._get_default_config()
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
                
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            logger.info("Using default configuration")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'app': {
                'name': 'MediaMind AI',
                'version': '2.0.0',
                'debug': True
            },
            'media': {
                'supported_formats': {
                    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
                    'videos': ['.mp4', '.avi', '.mov', '.mkv'],
                    'documents': ['.pdf', '.docx', '.pptx', '.txt']
                },
                'max_file_size_mb': 500,
                'scan_paths': ['/Users'],
                'excluded_paths': ['/System', '/Library', '/.Trash'],
                'parallel_workers': 4
            },
            'search': {
                'embedding_model': 'sentence-transformers/msmarco-bert-base-dot-v5',
                'faiss_dimension': 768,
                'chunk_size': 500,
                'chunk_overlap': 50,
                'max_results': 20
            },
            'ollama': {
                'base_url': 'http://localhost:11434',
                'vision_model': 'llava:latest',
                'text_model': 'llama3.1:latest',
                'timeout': 120
            },
            'database': {
                'type': 'sqlite',
                'path': './data/mediadb.sqlite',
                'vector_store': './data/faiss_index'
            },
            'web': {
                'host': 'localhost',
                'port': 8501,
                'title': 'MediaMind AI - Local Media Search Engine'
            }
        }
    
    def _validate_config(self):
        """Validate configuration values."""
        # Ensure required directories exist
        self._ensure_directories()
        
        # Validate scan paths
        valid_paths = []
        for path in self.config['media']['scan_paths']:
            if os.path.exists(path):
                valid_paths.append(path)
            else:
                logger.warning(f"Scan path does not exist: {path}")
        
        if not valid_paths:
            logger.warning("No valid scan paths found, using current directory")
            valid_paths = [os.getcwd()]
        
        self.config['media']['scan_paths'] = valid_paths
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            'data',
            'cache',
            'templates',
            'web'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_media_config(self) -> Dict[str, Any]:
        """Get media-specific configuration."""
        return self.config.get('media', {})
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search-specific configuration."""
        return self.config.get('search', {})
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama-specific configuration."""
        return self.config.get('ollama', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database-specific configuration."""
        return self.config.get('database', {})
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get web-specific configuration."""
        return self.config.get('web', {})
    
    def update_scan_paths(self, paths: list):
        """Update scan paths in configuration."""
        self.config['media']['scan_paths'] = paths
        logger.info(f"Updated scan paths: {paths}")
    
    def add_scan_path(self, path: str):
        """Add a new scan path."""
        if path not in self.config['media']['scan_paths']:
            self.config['media']['scan_paths'].append(path)
            logger.info(f"Added scan path: {path}")
    
    def remove_scan_path(self, path: str):
        """Remove a scan path."""
        if path in self.config['media']['scan_paths']:
            self.config['media']['scan_paths'].remove(path)
            logger.info(f"Removed scan path: {path}")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Allow dictionary-style assignment."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

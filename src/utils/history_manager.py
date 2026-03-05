"""
History manager for MP4 to MP3 converter
Handles saving and loading conversion history
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class HistoryManager:
    """Manages conversion history records"""
    
    def __init__(self, history_file: str = None):
        """
        Initialize the history manager
        
        Args:
            history_file: Path to the history file. If None, uses default location
        """
        if history_file is None:
            app_data_dir = Path(os.getenv('APPDATA')) / 'MP4to3'
            app_data_dir.mkdir(exist_ok=True)
            self.history_file = app_data_dir / 'conversion_history.json'
        else:
            self.history_file = Path(history_file)
            
        self.history = []
        self.load_history()
    
    def load_history(self) -> bool:
        """
        Load conversion history from file
        
        Returns:
            True if history was loaded successfully, False otherwise
        """
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                return True
        except Exception as e:
            print(f"Error loading history: {e}")
            return False
        
        return False
    
    def save_history(self) -> bool:
        """
        Save conversion history to file
        
        Returns:
            True if history was saved successfully, False otherwise
        """
        try:
            # Create parent directory if it doesn't exist
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def add_record(self, source_file: str, output_file: str, bitrate: str, duration: str) -> None:
        """
        Add a new record to the conversion history
        
        Args:
            source_file: Path to the source file
            output_file: Path to the output file
            bitrate: Bitrate used for conversion
            duration: Duration of the conversion process
        """
        record = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': source_file,
            'output': output_file,
            'bitrate': bitrate,
            'duration': duration
        }
        
        self.history.append(record)
        self.save_history()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversion history
        
        Returns:
            List of history records
        """
        return self.history.copy()
    
    def get_recent_records(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent conversion records
        
        Args:
            count: Number of recent records to return
            
        Returns:
            List of recent history records
        """
        return self.history[-count:] if len(self.history) >= count else self.history[:]
    
    def clear_history(self) -> bool:
        """
        Clear all conversion history
        
        Returns:
            True if history was cleared successfully, False otherwise
        """
        try:
            self.history = []
            self.save_history()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
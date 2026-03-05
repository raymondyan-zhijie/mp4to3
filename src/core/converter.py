"""
Core conversion logic for MP4 to MP3 converter
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional
from datetime import timedelta
from moviepy import VideoFileClip
import threading


class ConversionError(Exception):
    """Custom exception for conversion errors"""
    pass


class MP4ToMP3ConverterCore:
    """Core conversion functionality without UI dependencies"""
    
    def __init__(self):
        self.cancel_event = threading.Event()
        self.converting = False
        
    def convert_file(self, input_path: str, output_path: str, bitrate: str = "192k") -> float:
        """
        Convert a single MP4 file to MP3
        
        Args:
            input_path: Path to input MP4 file
            output_path: Path to output MP3 file
            bitrate: Audio bitrate (default: "192k")
            
        Returns:
            Conversion time in seconds
            
        Raises:
            ConversionError: If conversion fails
        """
        if self.cancel_event.is_set():
            raise ConversionError("Conversion was cancelled")
        
        start_time = time.time()
        
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                raise ConversionError(f"Input file does not exist: {input_path}")
                
            # Create video clip
            video = VideoFileClip(input_path)
            
            # Check if video has audio
            if video.audio is None:
                video.close()
                raise ConversionError(f"Video file has no audio track: {input_path}")
            
            # Extract audio and write to MP3
            audio = video.audio
            audio.write_audiofile(
                output_path,
                bitrate=bitrate,
                fps=44100,
                logger=None  # Suppress moviepy logging during conversion
            )
            
            # Clean up resources
            audio.close()
            video.close()
            
            conversion_time = time.time() - start_time
            return conversion_time
            
        except Exception as e:
            # Ensure resources are cleaned up in case of error
            try:
                video.close()
            except:
                pass
                
            raise ConversionError(f"Failed to convert {input_path}: {str(e)}")
    
    def convert_files(self, 
                     input_files: List[str], 
                     output_dir: str, 
                     bitrate: str = "192k",
                     progress_callback=None,
                     status_callback=None) -> dict:
        """
        Convert multiple MP4 files to MP3
        
        Args:
            input_files: List of input MP4 file paths
            output_dir: Output directory for MP3 files
            bitrate: Audio bitrate (default: "192k")
            progress_callback: Function called with progress updates (0-100)
            status_callback: Function called with status updates
            
        Returns:
            Dictionary with conversion statistics
        """
        total_start_time = time.time()
        total_files = len(input_files)
        
        stats = {
            'successful': 0,
            'failed': 0,
            'cancelled': False
        }
        
        self.converting = True
        self.cancel_event.clear()
        
        try:
            for index, input_file in enumerate(input_files):
                if self.cancel_event.is_set():
                    stats['cancelled'] = True
                    break
                
                # Prepare output file path
                input_filename = os.path.basename(input_file)
                output_filename = os.path.splitext(input_filename)[0] + ".mp3"
                output_path = os.path.join(output_dir, output_filename)
                
                # Handle duplicate output files
                counter = 1
                original_output_path = output_path
                while os.path.exists(output_path):
                    base_name = os.path.splitext(input_filename)[0]
                    output_path = os.path.join(
                        output_dir,
                        f"{base_name}_{counter}.mp3"
                    )
                    counter += 1
                
                # Update status
                if status_callback:
                    status_callback(f"Converting: {input_filename} ({index + 1}/{total_files})")
                
                try:
                    # Perform conversion
                    conversion_time = self.convert_file(input_file, output_path, bitrate)
                    
                    # Update progress
                    if progress_callback:
                        progress = ((index + 1) / total_files) * 100
                        progress_callback(progress)
                    
                    stats['successful'] += 1
                    
                    # Log success
                    logging.info(f"Successfully converted: {input_filename} -> {os.path.basename(output_path)} "
                                f"(Time: {timedelta(seconds=int(conversion_time))})")
                                
                except ConversionError as e:
                    stats['failed'] += 1
                    logging.error(f"Failed to convert {input_filename}: {str(e)}")
                    
        finally:
            self.converting = False
            
        total_time = time.time() - total_start_time
        stats['total_time'] = total_time
        stats['total_files'] = total_files
        
        return stats
    
    def cancel_current_operation(self):
        """Cancel the current conversion operation"""
        self.cancel_event.set()
    
    def reset_cancel_flag(self):
        """Reset the cancel event flag"""
        self.cancel_event.clear()
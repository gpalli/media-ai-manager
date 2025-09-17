#!/usr/bin/env python3
"""
Incremental update system for MediaMind AI.
Handles efficient scanning and updating of media files with proper change detection.
"""

import os
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

from .media_processor import MediaProcessor, MediaFile
from .ai_analyzer import AIMediaAnalyzer
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class FileChange:
    """Represents a change to a media file."""
    file_path: str
    change_type: str  # 'new', 'modified', 'moved', 'deleted'
    old_path: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    modified_date: Optional[datetime] = None

class IncrementalUpdater:
    """Handles incremental updates to the media database."""
    
    def __init__(self, config: Dict, db_manager: DatabaseManager, 
                 media_processor: MediaProcessor, ai_analyzer: AIMediaAnalyzer):
        self.config = config
        self.db_manager = db_manager
        self.media_processor = media_processor
        self.ai_analyzer = ai_analyzer
        
        # Track scan state
        self.scan_state_file = Path("data/scan_state.json")
        self.last_scan_time = self._get_last_scan_time()
        
    def _get_last_scan_time(self) -> datetime:
        """Get the timestamp of the last scan."""
        try:
            if self.scan_state_file.exists():
                import json
                with open(self.scan_state_file, 'r') as f:
                    state = json.load(f)
                    return datetime.fromisoformat(state.get('last_scan_time', '1970-01-01T00:00:00'))
        except Exception as e:
            logger.warning(f"Could not load scan state: {e}")
        
        return datetime.min
    
    def _save_scan_state(self, scan_time: datetime, processed_files: List[str]):
        """Save the current scan state."""
        try:
            import json
            state = {
                'last_scan_time': scan_time.isoformat(),
                'processed_files': processed_files,
                'scan_version': '1.0'
            }
            
            self.scan_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.scan_state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save scan state: {e}")
    
    def detect_changes(self, scan_paths: List[str]) -> List[FileChange]:
        """Detect changes in media files since last scan."""
        changes = []
        current_time = datetime.now()
        
        logger.info(f"Detecting changes since {self.last_scan_time}")
        
        # Get all media files in scan paths
        all_media_files = self.media_processor.discover_media_files(scan_paths)
        current_files = set(all_media_files)
        
        # Get files from database that are in the current scan paths
        db_files = self._get_database_files()
        db_file_paths = set()
        
        # Filter database files to only include those in current scan paths
        for file_path in db_files.keys():
            for scan_path in scan_paths:
                if file_path.startswith(scan_path):
                    db_file_paths.add(file_path)
                    break
        
        # Find new files
        new_files = current_files - db_file_paths
        for file_path in new_files:
            try:
                stat = os.stat(file_path)
                file_hash = self.media_processor._calculate_file_hash(file_path)
                changes.append(FileChange(
                    file_path=file_path,
                    change_type='new',
                    file_hash=file_hash,
                    file_size=stat.st_size,
                    modified_date=datetime.fromtimestamp(stat.st_mtime)
                ))
            except Exception as e:
                logger.error(f"Error processing new file {file_path}: {e}")
        
        # Find deleted files
        deleted_files = db_file_paths - current_files
        for file_path in deleted_files:
            changes.append(FileChange(
                file_path=file_path,
                change_type='deleted'
            ))
        
        # Check for modified files
        for file_path in current_files & db_file_paths:
            try:
                stat = os.stat(file_path)
                current_size = stat.st_size
                current_mtime = datetime.fromtimestamp(stat.st_mtime)
                current_hash = self.media_processor._calculate_file_hash(file_path)
                
                db_file = db_files[file_path]
                db_size = db_file.get('file_size', 0)
                db_mtime = db_file.get('modified_date')
                db_hash = db_file.get('file_hash', '')
                
                # Check if file was modified since last scan
                # A file is considered modified if:
                # 1. The hash has changed (content changed)
                # 2. The file was modified after the last scan time
                if (current_hash != db_hash or 
                    current_mtime > self.last_scan_time):
                    
                    changes.append(FileChange(
                        file_path=file_path,
                        change_type='modified',
                        file_hash=current_hash,
                        file_size=current_size,
                        modified_date=current_mtime
                    ))
                    
            except Exception as e:
                logger.error(f"Error checking modified file {file_path}: {e}")
        
        # Check for moved files (same hash, different path)
        current_hashes = {}
        for file_path in current_files:
            try:
                file_hash = self.media_processor._calculate_file_hash(file_path)
                current_hashes[file_hash] = file_path
            except Exception as e:
                logger.error(f"Error calculating hash for {file_path}: {e}")
        
        for db_file in db_files.values():
            db_hash = db_file.get('file_hash', '')
            db_path = db_file.get('file_path', '')
            
            if db_hash in current_hashes:
                current_path = current_hashes[db_hash]
                if current_path != db_path:
                    changes.append(FileChange(
                        file_path=current_path,
                        change_type='moved',
                        old_path=db_path,
                        file_hash=db_hash
                    ))
        
        logger.info(f"Detected {len(changes)} changes: "
                   f"{len([c for c in changes if c.change_type == 'new'])} new, "
                   f"{len([c for c in changes if c.change_type == 'modified'])} modified, "
                   f"{len([c for c in changes if c.change_type == 'moved'])} moved, "
                   f"{len([c for c in changes if c.change_type == 'deleted'])} deleted")
        
        return changes
    
    def _get_database_files(self) -> Dict[str, Dict]:
        """Get all files from database with their metadata."""
        try:
            results = self.db_manager.conn.execute('''
                SELECT file_path, file_hash, file_size, modified_date, id
                FROM media_files
            ''').fetchall()
            
            files = {}
            for row in results:
                files[row[0]] = {
                    'file_path': row[0],
                    'file_hash': row[1],
                    'file_size': row[2],
                    'modified_date': row[3],
                    'id': row[4]
                }
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting database files: {e}")
            return {}
    
    def process_changes(self, changes: List[FileChange], progress_callback=None) -> Dict[str, int]:
        """Process detected changes."""
        stats = {
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'deleted': 0
        }
        
        processed_files = []
        
        for i, change in enumerate(changes):
            try:
                if change.change_type == 'deleted':
                    self._handle_deleted_file(change)
                    stats['deleted'] += 1
                    
                elif change.change_type in ['new', 'modified']:
                    # Process the file
                    media_file = self.media_processor.process_file(change.file_path)
                    if not media_file:
                        stats['errors'] += 1
                        continue
                    
                    # AI analysis
                    media_file = self.ai_analyzer.analyze_media(media_file)
                    
                    # Store in database
                    media_id = self.db_manager.store_media_file(media_file)
                    processed_files.append(change.file_path)
                    stats['processed'] += 1
                    
                elif change.change_type == 'moved':
                    # Update file path in database
                    self._handle_moved_file(change)
                    processed_files.append(change.file_path)
                    stats['processed'] += 1
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, len(changes))
                    
            except Exception as e:
                logger.error(f"Error processing change {change.file_path}: {e}")
                stats['errors'] += 1
        
        # Save scan state
        scan_time = datetime.now()
        self._save_scan_state(scan_time, processed_files)
        self.last_scan_time = scan_time
        
        return stats
    
    def _handle_deleted_file(self, change: FileChange):
        """Handle a deleted file."""
        try:
            # Remove from database
            self.db_manager.conn.execute(
                'DELETE FROM media_files WHERE file_path = ?', 
                (change.file_path,)
            )
            
            # Remove from FAISS index (if implemented)
            # This would require tracking media_id to FAISS index mapping
            
            self.db_manager.conn.commit()
            logger.info(f"Removed deleted file: {change.file_path}")
            
        except Exception as e:
            logger.error(f"Error handling deleted file {change.file_path}: {e}")
    
    def _handle_moved_file(self, change: FileChange):
        """Handle a moved/renamed file."""
        try:
            # Update file path in database
            self.db_manager.conn.execute(
                'UPDATE media_files SET file_path = ? WHERE file_path = ?',
                (change.file_path, change.old_path)
            )
            
            self.db_manager.conn.commit()
            logger.info(f"Moved file: {change.old_path} -> {change.file_path}")
            
        except Exception as e:
            logger.error(f"Error handling moved file {change.file_path}: {e}")
    
    def incremental_scan(self, scan_paths: List[str], progress_callback=None) -> Dict[str, int]:
        """Perform an incremental scan of media files."""
        logger.info("Starting incremental scan...")
        
        # Detect changes
        changes = self.detect_changes(scan_paths)
        
        if not changes:
            logger.info("No changes detected")
            return {'processed': 0, 'skipped': 0, 'errors': 0, 'deleted': 0}
        
        # Process changes
        stats = self.process_changes(changes, progress_callback)
        
        logger.info(f"Incremental scan completed: {stats}")
        return stats
    
    def full_scan(self, scan_paths: List[str], progress_callback=None) -> Dict[str, int]:
        """Perform a full scan of media files."""
        logger.info("Starting full scan...")
        
        # Get all media files
        all_media_files = self.media_processor.discover_media_files(scan_paths)
        
        stats = {
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'deleted': 0
        }
        
        processed_files = []
        
        for i, file_path in enumerate(all_media_files):
            try:
                # Check if file already exists
                file_hash = self.media_processor._calculate_file_hash(file_path)
                if self.db_manager.file_exists(file_hash):
                    stats['skipped'] += 1
                    continue
                
                # Process file
                media_file = self.media_processor.process_file(file_path)
                if not media_file:
                    stats['errors'] += 1
                    continue
                
                # AI analysis
                media_file = self.ai_analyzer.analyze_media(media_file)
                
                # Store in database
                media_id = self.db_manager.store_media_file(media_file)
                processed_files.append(file_path)
                stats['processed'] += 1
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, len(all_media_files))
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                stats['errors'] += 1
        
        # Save scan state
        scan_time = datetime.now()
        self._save_scan_state(scan_time, processed_files)
        self.last_scan_time = scan_time
        
        logger.info(f"Full scan completed: {stats}")
        return stats
    
    def get_scan_statistics(self) -> Dict:
        """Get scan statistics."""
        try:
            if self.scan_state_file.exists():
                import json
                with open(self.scan_state_file, 'r') as f:
                    state = json.load(f)
                    return {
                        'last_scan_time': state.get('last_scan_time'),
                        'processed_files_count': len(state.get('processed_files', [])),
                        'scan_version': state.get('scan_version', 'unknown')
                    }
        except Exception as e:
            logger.error(f"Error getting scan statistics: {e}")
        
        return {
            'last_scan_time': None,
            'processed_files_count': 0,
            'scan_version': 'unknown'
        }
    
    def reset_scan_state(self):
        """Reset scan state (force full scan next time)."""
        try:
            if self.scan_state_file.exists():
                self.scan_state_file.unlink()
                logger.info("Scan state reset")
        except Exception as e:
            logger.error(f"Error resetting scan state: {e}")

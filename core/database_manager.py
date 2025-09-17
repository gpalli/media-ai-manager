#!/usr/bin/env python3
"""
Database manager for MediaMind AI.
Handles both relational data (SQLite) and vector embeddings (FAISS).
Based on the original implementation but enhanced for media metadata.
"""

import os
import sqlite3
import json
import logging
import pickle
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

import faiss
import numpy as np

from .media_processor import MediaFile

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages media metadata storage and retrieval."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_path = config.get('path', './data/mediadb.sqlite')
        self.vector_store_path = config.get('vector_store', './data/faiss_index')
        
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.vector_store_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self._init_sqlite_db()
        self._init_faiss_index()
    
    def _init_sqlite_db(self):
        """Initialize SQLite database with required tables."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self._create_tables()
        logger.info(f"SQLite database initialized: {self.db_path}")
    
    def _create_tables(self):
        """Create database tables for media metadata."""
        
        # Main media files table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                file_type TEXT NOT NULL,
                created_date TIMESTAMP NOT NULL,
                modified_date TIMESTAMP NOT NULL,
                indexed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Media dimensions
                width INTEGER,
                height INTEGER,
                duration REAL,
                fps REAL,
                bitrate INTEGER,
                
                -- AI-generated content
                ai_description TEXT,
                scene_type TEXT,
                extracted_text TEXT,
                
                -- JSON fields for complex data
                exif_data TEXT,  -- JSON
                camera_info TEXT,  -- JSON
                gps_data TEXT,  -- JSON
                ai_tags TEXT,    -- JSON array
                detected_objects TEXT,  -- JSON array
                
                -- Search optimization
                searchable_text TEXT GENERATED ALWAYS AS (
                    COALESCE(file_name, '') || ' ' ||
                    COALESCE(ai_description, '') || ' ' ||
                    COALESCE(scene_type, '') || ' ' ||
                    COALESCE(extracted_text, '') || ' ' ||
                    COALESCE(ai_tags, '') || ' ' ||
                    COALESCE(detected_objects, '')
                ) VIRTUAL
            )
        ''')
        
        # Create FTS virtual table for full-text search
        self.conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS media_files_fts USING fts5(
                file_name,
                ai_description,
                scene_type,
                extracted_text,
                ai_tags,
                detected_objects,
                content='media_files',
                content_rowid='id'
            )
        ''')
        
        # Tags table for normalized tag storage
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL,
                usage_count INTEGER DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Media-tag relationships
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS media_tags (
                media_id INTEGER,
                tag_id INTEGER,
                confidence REAL DEFAULT 1.0,
                PRIMARY KEY (media_id, tag_id),
                FOREIGN KEY (media_id) REFERENCES media_files(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        ''')
        
        # Collections for saved searches
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                query_data TEXT,  -- JSON
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Collection items
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS collection_items (
                collection_id INTEGER,
                media_id INTEGER,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (collection_id, media_id),
                FOREIGN KEY (collection_id) REFERENCES collections(id),
                FOREIGN KEY (media_id) REFERENCES media_files(id)
            )
        ''')
        
        # Create indexes for better performance
        self._create_indexes()
        
        self.conn.commit()
    
    def _create_indexes(self):
        """Create database indexes for performance optimization."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_file_hash ON media_files(file_hash)",
            "CREATE INDEX IF NOT EXISTS idx_file_path ON media_files(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_type ON media_files(file_type)",
            "CREATE INDEX IF NOT EXISTS idx_mime_type ON media_files(mime_type)",
            "CREATE INDEX IF NOT EXISTS idx_created_date ON media_files(created_date)",
            "CREATE INDEX IF NOT EXISTS idx_scene_type ON media_files(scene_type)",
            "CREATE INDEX IF NOT EXISTS idx_tag_name ON tags(tag_name)",
            "CREATE INDEX IF NOT EXISTS idx_media_tags_media ON media_tags(media_id)",
            "CREATE INDEX IF NOT EXISTS idx_media_tags_tag ON media_tags(tag_id)",
        ]
        
        for index_sql in indexes:
            try:
                self.conn.execute(index_sql)
            except sqlite3.Error as e:
                logger.warning(f"Failed to create index: {e}")
        
        # Create triggers to keep FTS table in sync
        triggers = [
            '''
            CREATE TRIGGER IF NOT EXISTS media_files_ai AFTER INSERT ON media_files BEGIN
                INSERT INTO media_files_fts(rowid, file_name, ai_description, scene_type, extracted_text, ai_tags, detected_objects)
                VALUES (new.id, new.file_name, new.ai_description, new.scene_type, new.extracted_text, new.ai_tags, new.detected_objects);
            END
            ''',
            '''
            CREATE TRIGGER IF NOT EXISTS media_files_au AFTER UPDATE ON media_files BEGIN
                UPDATE media_files_fts SET 
                    file_name = new.file_name,
                    ai_description = new.ai_description,
                    scene_type = new.scene_type,
                    extracted_text = new.extracted_text,
                    ai_tags = new.ai_tags,
                    detected_objects = new.detected_objects
                WHERE rowid = new.id;
            END
            ''',
            '''
            CREATE TRIGGER IF NOT EXISTS media_files_ad AFTER DELETE ON media_files BEGIN
                DELETE FROM media_files_fts WHERE rowid = old.id;
            END
            '''
        ]
        
        for trigger_sql in triggers:
            try:
                self.conn.execute(trigger_sql)
            except sqlite3.Error as e:
                logger.warning(f"Failed to create trigger: {e}")
    
    def _init_faiss_index(self):
        """Initialize FAISS index for vector search."""
        try:
            dimension = 768  # Default dimension for sentence transformers
            self.faiss_index = faiss.IndexFlatIP(dimension)
            self.faiss_metadata = []
            
            # Try to load existing index
            index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
            metadata_path = os.path.join(self.vector_store_path, "faiss_metadata.pkl")
            
            if os.path.exists(index_path) and os.path.exists(metadata_path):
                self.faiss_index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    self.faiss_metadata = pickle.load(f)
                logger.info(f"Loaded existing FAISS index with {self.faiss_index.ntotal} vectors")
            else:
                logger.info("Created new FAISS index")
                
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    def store_media_file(self, media_file: MediaFile) -> int:
        """Store a media file with all its metadata."""
        try:
            # Convert complex data to JSON strings
            exif_json = json.dumps(media_file.exif_data) if media_file.exif_data else None
            camera_json = json.dumps(media_file.camera_info) if media_file.camera_info else None
            gps_json = json.dumps(media_file.gps_data) if media_file.gps_data else None
            tags_json = json.dumps(media_file.ai_tags) if media_file.ai_tags else None
            objects_json = json.dumps(media_file.detected_objects) if media_file.detected_objects else None
            
            # Check if file already exists
            existing = self.conn.execute(
                'SELECT id FROM media_files WHERE file_path = ?', 
                (media_file.file_path,)
            ).fetchone()
            
            if existing:
                # Update existing record
                media_id = existing[0]
                cursor = self.conn.execute('''
                    UPDATE media_files SET
                        file_name = ?, file_hash = ?, file_size = ?, mime_type = ?, file_type = ?,
                        created_date = ?, modified_date = ?, width = ?, height = ?, duration = ?, 
                        fps = ?, bitrate = ?, ai_description = ?, scene_type = ?, extracted_text = ?,
                        exif_data = ?, camera_info = ?, gps_data = ?, ai_tags = ?, detected_objects = ?,
                        indexed_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    media_file.file_name, media_file.file_hash, media_file.file_size, 
                    media_file.mime_type, media_file.file_type, media_file.created_date, 
                    media_file.modified_date, media_file.width, media_file.height, 
                    media_file.duration, media_file.fps, media_file.bitrate, 
                    media_file.ai_description, media_file.scene_type, media_file.extracted_text,
                    exif_json, camera_json, gps_json, tags_json, objects_json, media_id
                ))
                
                # Remove existing tags
                self.conn.execute('DELETE FROM media_tags WHERE media_id = ?', (media_id,))
            else:
                # Insert new record
                cursor = self.conn.execute('''
                    INSERT INTO media_files 
                    (file_path, file_name, file_hash, file_size, mime_type, file_type,
                     created_date, modified_date, width, height, duration, fps, bitrate,
                     ai_description, scene_type, extracted_text, 
                     exif_data, camera_info, gps_data, ai_tags, detected_objects)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    media_file.file_path, media_file.file_name, media_file.file_hash, 
                    media_file.file_size, media_file.mime_type, media_file.file_type,
                    media_file.created_date, media_file.modified_date, media_file.width, 
                    media_file.height, media_file.duration, media_file.fps, media_file.bitrate,
                    media_file.ai_description, media_file.scene_type, media_file.extracted_text,
                    exif_json, camera_json, gps_json, tags_json, objects_json
                ))
                media_id = cursor.lastrowid
            
            # Verify the media file was inserted successfully
            if not media_id:
                logger.error(f"Failed to insert media file: {media_file.file_path}")
                return None
            
            logger.debug(f"Inserted media file with ID: {media_id}")
            
            # Commit the media file insertion first
            self.conn.commit()
            logger.debug(f"Stored media file: {media_file.file_path}")
            
            # Store tags after committing the media file
            if media_file.ai_tags:
                try:
                    self._store_tags(media_id, media_file.ai_tags)
                except Exception as e:
                    logger.error(f"Failed to store tags for {media_file.file_path}: {e}")
                    # Continue without tags rather than failing completely
            
            # Store embeddings in FAISS index
            if media_file.ai_description:
                self._store_text_embedding(media_id, media_file.ai_description, media_file.file_path)
            
            return media_id
            
        except Exception as e:
            logger.error(f"Failed to store media file {media_file.file_path}: {e}")
            self.conn.rollback()
            raise
    
    def _store_tags(self, media_id: int, tags: List[str]):
        """Store tags and create media-tag relationships."""
        logger.debug(f"Storing {len(tags)} tags for media_id: {media_id}")
        
        for tag in tags:
            if not tag.strip():
                continue
                
            tag = tag.strip().lower()
            logger.debug(f"Processing tag: {tag}")
            
            # Insert or update tag
            self.conn.execute('''
                INSERT OR IGNORE INTO tags (tag_name) VALUES (?)
            ''', (tag,))
            
            self.conn.execute('''
                UPDATE tags SET usage_count = usage_count + 1 WHERE tag_name = ?
            ''', (tag,))
            
            # Get tag ID
            tag_result = self.conn.execute(
                'SELECT id FROM tags WHERE tag_name = ?', (tag,)
            ).fetchone()
            
            if tag_result:
                tag_id = tag_result[0]
                logger.debug(f"Found tag_id: {tag_id} for tag: {tag}")
                # Create media-tag relationship
                self.conn.execute('''
                    INSERT OR IGNORE INTO media_tags (media_id, tag_id) VALUES (?, ?)
                ''', (media_id, tag_id))
            else:
                logger.warning(f"Tag not found after insertion: {tag}")
    
    def _store_text_embedding(self, media_id: int, text: str, file_path: str):
        """Store text embedding in FAISS index."""
        try:
            # This would generate embeddings using the AI analyzer
            # For now, we'll store a placeholder
            # In a real implementation, you'd call the embedding model here
            pass
        except Exception as e:
            logger.error(f"Failed to store text embedding: {e}")
    
    def file_exists(self, file_hash: str) -> bool:
        """Check if a file already exists in the database."""
        result = self.conn.execute(
            'SELECT 1 FROM media_files WHERE file_hash = ?', (file_hash,)
        ).fetchone()
        return result is not None
    
    def get_media_count(self) -> int:
        """Get the total number of media files in the database."""
        result = self.conn.execute('SELECT COUNT(*) FROM media_files').fetchone()
        return result[0] if result else 0
    
    def search_media(self, 
                    query: str = None,
                    tags: List[str] = None,
                    file_type: str = None,
                    scene_type: str = None,
                    date_from: datetime = None,
                    date_to: datetime = None,
                    mime_type: str = None,
                    limit: int = 50) -> List[Dict]:
        """Search media files using various criteria."""
        
        conditions = []
        params = []
        
        # Build WHERE clause
        if query:
            # Use FTS table for text search
            conditions.append("id IN (SELECT rowid FROM media_files_fts WHERE media_files_fts MATCH ?)")
            params.append(query)
        
        if tags:
            tag_placeholders = ','.join(['?' for _ in tags])
            conditions.append(f'''
                id IN (
                    SELECT DISTINCT mt.media_id 
                    FROM media_tags mt 
                    JOIN tags t ON mt.tag_id = t.id 
                    WHERE t.tag_name IN ({tag_placeholders})
                )
            ''')
            params.extend(tags)
        
        if file_type:
            conditions.append("file_type = ?")
            params.append(file_type)
        
        if scene_type:
            conditions.append("scene_type = ?")
            params.append(scene_type)
        
        if date_from:
            conditions.append("created_date >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("created_date <= ?")
            params.append(date_to)
        
        if mime_type:
            conditions.append("mime_type LIKE ?")
            params.append(f"{mime_type}%")
        
        # Build query
        base_query = '''
            SELECT id, file_path, file_name, file_size, mime_type, file_type,
                   created_date, modified_date, width, height, duration,
                   ai_description, scene_type, extracted_text,
                   ai_tags, detected_objects, exif_data, camera_info, gps_data
            FROM media_files
        '''
        
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            base_query += where_clause
        
        base_query += " ORDER BY created_date DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        results = self.conn.execute(base_query, params).fetchall()
        
        # Convert to dictionaries
        return [self._row_to_dict(row) for row in results]
    
    def search_similar_text(self, query_text: str, limit: int = 10) -> List[Dict]:
        """Search for media with similar text content using vector similarity."""
        try:
            # This would use the FAISS index for vector search
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            logger.error(f"Similar text search failed: {e}")
            return []
    
    def get_media_by_id(self, media_id: int) -> Optional[Dict]:
        """Get media file by ID."""
        result = self.conn.execute('''
            SELECT id, file_path, file_name, file_size, mime_type, file_type,
                   created_date, modified_date, width, height, duration,
                   ai_description, scene_type, extracted_text,
                   ai_tags, detected_objects, exif_data, camera_info, gps_data
            FROM media_files WHERE id = ?
        ''', (media_id,)).fetchone()
        
        return self._row_to_dict(result) if result else None
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary."""
        if not row:
            return None
            
        return {
            'id': row[0],
            'file_path': row[1],
            'file_name': row[2],
            'file_size': row[3],
            'mime_type': row[4],
            'file_type': row[5],
            'created_date': row[6],
            'modified_date': row[7],
            'width': row[8],
            'height': row[9],
            'duration': row[10],
            'ai_description': row[11],
            'scene_type': row[12],
            'extracted_text': row[13],
            'ai_tags': json.loads(row[14]) if row[14] else [],
            'detected_objects': json.loads(row[15]) if row[15] else [],
            'exif_data': json.loads(row[16]) if row[16] else {},
            'camera_info': json.loads(row[17]) if row[17] else {},
            'gps_data': json.loads(row[18]) if row[18] else {}
        }
    
    def create_collection(self, name: str, description: str, query_data: Dict) -> int:
        """Create a new collection from search results."""
        cursor = self.conn.execute('''
            INSERT INTO collections (name, description, query_data)
            VALUES (?, ?, ?)
        ''', (name, description, json.dumps(query_data)))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def add_to_collection(self, collection_id: int, media_ids: List[int]):
        """Add media items to a collection."""
        for media_id in media_ids:
            self.conn.execute('''
                INSERT OR IGNORE INTO collection_items (collection_id, media_id)
                VALUES (?, ?)
            ''', (collection_id, media_id))
        
        self.conn.commit()
    
    def get_collections(self) -> List[Dict]:
        """Get all collections."""
        results = self.conn.execute('''
            SELECT c.id, c.name, c.description, c.created_date, c.updated_date,
                   COUNT(ci.media_id) as item_count
            FROM collections c
            LEFT JOIN collection_items ci ON c.id = ci.collection_id
            GROUP BY c.id, c.name, c.description, c.created_date, c.updated_date
            ORDER BY c.updated_date DESC
        ''').fetchall()
        
        return [{
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'created_date': row[3],
            'updated_date': row[4],
            'item_count': row[5]
        } for row in results]
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        stats = {}
        
        # Total files
        stats['total_files'] = self.conn.execute(
            'SELECT COUNT(*) FROM media_files'
        ).fetchone()[0]
        
        # Files by type
        type_stats = self.conn.execute('''
            SELECT file_type, COUNT(*) as count
            FROM media_files
            GROUP BY file_type
        ''').fetchall()
        
        stats['by_type'] = {row[0]: row[1] for row in type_stats}
        
        # Most common tags
        top_tags = self.conn.execute('''
            SELECT tag_name, usage_count 
            FROM tags 
            ORDER BY usage_count DESC 
            LIMIT 10
        ''').fetchall()
        
        stats['top_tags'] = [{'tag': row[0], 'count': row[1]} for row in top_tags]
        
        # Database size
        stats['database_size'] = self.conn.execute(
            "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
        ).fetchone()[0]
        
        return stats
    
    def save_faiss_index(self):
        """Save FAISS index to disk."""
        try:
            index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
            metadata_path = os.path.join(self.vector_store_path, "faiss_metadata.pkl")
            
            faiss.write_index(self.faiss_index, index_path)
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.faiss_metadata, f)
            
            logger.info("FAISS index saved successfully")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
    
    def __del__(self):
        """Clean up database connections."""
        if hasattr(self, 'conn'):
            self.conn.close()

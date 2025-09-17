#!/usr/bin/env python3
"""Migrate database to remove unique constraint on file_hash."""

import sqlite3
import os

def migrate_database():
    """Remove unique constraint on file_hash."""
    db_path = "./data/mediadb.sqlite"
    
    if not os.path.exists(db_path):
        print("Database does not exist!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create a new table without the unique constraint on file_hash
        cursor.execute('''
            CREATE TABLE media_files_new (
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
                width INTEGER,
                height INTEGER,
                duration REAL,
                fps REAL,
                bitrate INTEGER,
                ai_description TEXT,
                scene_type TEXT,
                extracted_text TEXT,
                exif_data TEXT,
                camera_info TEXT,
                gps_data TEXT,
                ai_tags TEXT,
                detected_objects TEXT
            )
        ''')
        
        # Copy data from old table to new table (excluding id which is auto-increment)
        cursor.execute('''
            INSERT INTO media_files_new 
            (file_path, file_name, file_hash, file_size, mime_type, file_type,
             created_date, modified_date, indexed_date, width, height, duration, 
             fps, bitrate, ai_description, scene_type, extracted_text, 
             exif_data, camera_info, gps_data, ai_tags, detected_objects)
            SELECT file_path, file_name, file_hash, file_size, mime_type, file_type,
                   created_date, modified_date, indexed_date, width, height, duration, 
                   fps, bitrate, ai_description, scene_type, extracted_text, 
                   exif_data, camera_info, gps_data, ai_tags, detected_objects
            FROM media_files
        ''')
        
        # Drop the old table
        cursor.execute("DROP TABLE media_files")
        
        # Rename the new table
        cursor.execute("ALTER TABLE media_files_new RENAME TO media_files")
        
        # Recreate indexes
        cursor.execute("CREATE INDEX idx_file_path ON media_files(file_path)")
        cursor.execute("CREATE INDEX idx_file_hash ON media_files(file_hash)")
        cursor.execute("CREATE INDEX idx_mime_type ON media_files(mime_type)")
        cursor.execute("CREATE INDEX idx_file_type ON media_files(file_type)")
        cursor.execute("CREATE INDEX idx_created_date ON media_files(created_date)")
        cursor.execute("CREATE INDEX idx_scene_type ON media_files(scene_type)")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

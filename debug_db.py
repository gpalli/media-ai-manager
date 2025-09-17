#!/usr/bin/env python3
"""Debug database issues."""

import sqlite3
import os

def debug_database():
    """Debug database schema and constraints."""
    db_path = "./data/mediadb.sqlite"
    
    if not os.path.exists(db_path):
        print("Database does not exist!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Check media_files table structure
    cursor.execute("PRAGMA table_info(media_files);")
    columns = cursor.fetchall()
    print("\nmedia_files columns:")
    for col in columns:
        print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'} {'PRIMARY KEY' if col[5] else ''}")
    
    # Check foreign key constraints
    cursor.execute("PRAGMA foreign_key_list(media_tags);")
    fks = cursor.fetchall()
    print("\nForeign keys for media_tags:")
    for fk in fks:
        print(f"  {fk[3]} -> {fk[2]}.{fk[4]}")
    
    # Check if there are any records
    cursor.execute("SELECT COUNT(*) FROM media_files;")
    count = cursor.fetchone()[0]
    print(f"\nRecords in media_files: {count}")
    
    cursor.execute("SELECT COUNT(*) FROM tags;")
    count = cursor.fetchone()[0]
    print(f"Records in tags: {count}")
    
    cursor.execute("SELECT COUNT(*) FROM media_tags;")
    count = cursor.fetchone()[0]
    print(f"Records in media_tags: {count}")
    
    conn.close()

if __name__ == "__main__":
    debug_database()

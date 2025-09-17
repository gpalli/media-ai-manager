#!/usr/bin/env python3
"""
Enhanced Media Search Engine for MediaMind AI.
Based on the original Towards AI implementation but enhanced for media files.
"""

import os
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from .config_loader import ConfigLoader
from .media_processor import MediaProcessor, MediaFile
from .ai_analyzer import AIMediaAnalyzer
from .database_manager import DatabaseManager
from .incremental_updater import IncrementalUpdater

logger = logging.getLogger(__name__)

class EnhancedMediaSearchEngine:
    """
    Enhanced version of the local search engine, specifically designed for media files.
    Based on the Towards AI implementation but extended for images, videos, and documents.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        
        # Initialize components
        self.media_processor = MediaProcessor(self.config)
        self.ai_analyzer = AIMediaAnalyzer(self.config)
        self.db_manager = DatabaseManager(self.config.get('database', {}))
        self.incremental_updater = IncrementalUpdater(
            self.config, self.db_manager, self.media_processor, self.ai_analyzer
        )
        
        # Initialize embedding model
        self._init_embedding_model()
        
        # Initialize FAISS index
        self._init_faiss_index()
        
        logger.info("Enhanced Media Search Engine initialized successfully")
    
    def _init_embedding_model(self):
        """Initialize the sentence transformer model."""
        try:
            embedding_model = self.config.get('search', {}).get('embedding_model', 'sentence-transformers/msmarco-bert-base-dot-v5')
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _init_faiss_index(self):
        """Initialize FAISS index for vector search."""
        try:
            dimension = self.config.get('search', {}).get('faiss_dimension', 768)
            self.faiss_index = faiss.IndexFlatIP(dimension)
            self.faiss_metadata = []
            logger.info(f"Initialized FAISS index with dimension: {dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    def scan_and_index_media(self, scan_paths: List[str] = None, progress_callback=None, 
                           incremental: bool = True) -> Dict[str, Any]:
        """Scan directories for media files and index them with AI analysis."""
        if scan_paths is None:
            scan_paths = self.config.get('media', {}).get('scan_paths', [])
        
        logger.info(f"Starting media scan and indexing for paths: {scan_paths}")
        logger.info(f"Scan mode: {'incremental' if incremental else 'full'}")
        
        if incremental:
            # Use incremental updater for efficient scanning
            result = self.incremental_updater.incremental_scan(scan_paths, progress_callback)
        else:
            # Use full scan
            result = self.incremental_updater.full_scan(scan_paths, progress_callback)
        
        # Save FAISS index
        self.db_manager.save_faiss_index()
        
        logger.info(f"Media scan completed: {result}")
        return result
    
    def _store_text_embedding(self, media_id: int, text: str, file_path: str):
        """Store text embedding in FAISS index."""
        try:
            # Generate embedding
            embedding = self.embedding_model.encode([text])
            
            # Add to FAISS index
            self.faiss_index.add(embedding.astype('float32'))
            
            # Store metadata
            self.faiss_metadata.append({
                'media_id': media_id,
                'file_path': file_path,
                'text': text
            })
            
        except Exception as e:
            logger.error(f"Failed to store text embedding: {e}")
    
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
        return self.db_manager.search_media(
            query=query,
            tags=tags,
            file_type=file_type,
            scene_type=scene_type,
            date_from=date_from,
            date_to=date_to,
            mime_type=mime_type,
            limit=limit
        )
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Perform semantic search using vector similarity."""
        try:
            if not query.strip():
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in FAISS index
            scores, indices = self.faiss_index.search(query_embedding.astype('float32'), limit)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.faiss_metadata):
                    metadata = self.faiss_metadata[idx]
                    media_data = self.db_manager.get_media_by_id(metadata['media_id'])
                    if media_data:
                        media_data['similarity_score'] = float(score)
                        results.append(media_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def generate_answer(self, query: str, context_results: List[Dict] = None) -> str:
        """Generate AI-powered answer based on search results."""
        try:
            if not context_results:
                # Perform semantic search to get context
                context_results = self.semantic_search(query, limit=5)
            
            if not context_results:
                return "I couldn't find any relevant media files for your query."
            
            # Prepare context
            context_text = self._prepare_context(context_results)
            
            # Generate answer using Ollama
            prompt = f"""Based on the following media files and their descriptions, answer the user's question.

User Question: {query}

Media Files Context:
{context_text}

Please provide a helpful answer based on the available media files. If the question is about finding specific files, mention the file names and their locations."""

            response = self.ai_analyzer.ollama_client.generate(
                model=self.config.get('ollama', {}).get('text_model', 'llama3.1:latest'),
                prompt=prompt
            )
            
            return response['response'].strip()
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return "I encountered an error while generating an answer. Please try again."
    
    def _prepare_context(self, results: List[Dict]) -> str:
        """Prepare context text from search results."""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            context_part = f"{i}. File: {result['file_name']}\n"
            context_part += f"   Path: {result['file_path']}\n"
            context_part += f"   Type: {result['file_type']}\n"
            
            if result.get('ai_description'):
                context_part += f"   Description: {result['ai_description']}\n"
            
            if result.get('ai_tags'):
                context_part += f"   Tags: {', '.join(result['ai_tags'])}\n"
            
            if result.get('scene_type'):
                context_part += f"   Scene: {result['scene_type']}\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        return self.db_manager.get_statistics()
    
    def create_collection(self, name: str, description: str, media_ids: List[int]) -> int:
        """Create a new collection from media IDs."""
        query_data = {
            'media_ids': media_ids,
            'created_at': datetime.now().isoformat()
        }
        
        collection_id = self.db_manager.create_collection(name, description, query_data)
        self.db_manager.add_to_collection(collection_id, media_ids)
        
        return collection_id
    
    def get_collections(self) -> List[Dict]:
        """Get all collections."""
        return self.db_manager.get_collections()
    
    def update_scan_paths(self, paths: List[str]):
        """Update scan paths in configuration."""
        self.config_loader.update_scan_paths(paths)
        self.config_loader.save_config()
        logger.info(f"Updated scan paths: {paths}")
    
    def rescan_directory(self, path: str, incremental: bool = True) -> Dict[str, Any]:
        """Rescan a specific directory for new files."""
        logger.info(f"Rescanning directory: {path}")
        return self.scan_and_index_media([path], incremental=incremental)
    
    def force_full_scan(self, scan_paths: List[str] = None) -> Dict[str, Any]:
        """Force a full scan, ignoring incremental updates."""
        if scan_paths is None:
            scan_paths = self.config.get('media', {}).get('scan_paths', [])
        
        logger.info("Forcing full scan...")
        return self.scan_and_index_media(scan_paths, incremental=False)
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Get scan statistics including incremental update info."""
        stats = self.db_manager.get_statistics()
        scan_stats = self.incremental_updater.get_scan_statistics()
        
        return {
            **stats,
            'scan_info': scan_stats
        }
    
    def reset_scan_state(self):
        """Reset scan state to force full scan next time."""
        self.incremental_updater.reset_scan_state()
        logger.info("Scan state reset - next scan will be full scan")
    
    def get_media_by_id(self, media_id: int) -> Optional[Dict]:
        """Get media file by ID."""
        return self.db_manager.get_media_by_id(media_id)
    
    def search_similar_media(self, media_id: int, limit: int = 10) -> List[Dict]:
        """Find similar media files based on a reference media file."""
        try:
            # Get the reference media file
            reference = self.get_media_by_id(media_id)
            if not reference or not reference.get('ai_description'):
                return []
            
            # Use its description for semantic search
            return self.semantic_search(reference['ai_description'], limit)
            
        except Exception as e:
            logger.error(f"Similar media search failed: {e}")
            return []
    
    def export_collection(self, collection_id: int, format: str = 'json') -> str:
        """Export a collection to a file."""
        try:
            # Get collection data
            collections = self.get_collections()
            collection = next((c for c in collections if c['id'] == collection_id), None)
            
            if not collection:
                raise ValueError(f"Collection {collection_id} not found")
            
            # Get media files in collection
            media_files = self.db_manager.conn.execute('''
                SELECT mf.* FROM media_files mf
                JOIN collection_items ci ON mf.id = ci.media_id
                WHERE ci.collection_id = ?
                ORDER BY ci.added_date DESC
            ''', (collection_id,)).fetchall()
            
            # Prepare export data
            export_data = {
                'collection': collection,
                'media_files': [self.db_manager._row_to_dict(row) for row in media_files],
                'exported_at': datetime.now().isoformat()
            }
            
            # Export to file
            export_path = f"data/collection_{collection_id}_export.{format}"
            with open(export_path, 'w') as f:
                if format == 'json':
                    json.dump(export_data, f, indent=2, default=str)
                else:
                    # Add other formats as needed
                    raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Collection exported to: {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

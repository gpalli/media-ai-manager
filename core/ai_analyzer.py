#!/usr/bin/env python3
"""
AI-powered media analyzer using Ollama local models.
Provides computer vision and natural language processing for media files.
Based on the original implementation but enhanced for media analysis.
"""

import base64
import json
import logging
from typing import List, Dict, Optional, Any
from io import BytesIO
import time

import cv2
import numpy as np
from PIL import Image
import torch
from sentence_transformers import SentenceTransformer
import ollama

from .media_processor import MediaFile

logger = logging.getLogger(__name__)

class AIMediaAnalyzer:
    """AI analyzer for media files using local Ollama models."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ollama_config = config.get('ollama', {})
        self.vision_config = self.ollama_config.get('vision_analysis', {})
        
        # Initialize Ollama client
        try:
            self.ollama_client = ollama.Client(host=self.ollama_config.get('base_url', 'http://localhost:11434'))
            logger.info("Ollama client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise
        
        # Initialize embedding model
        try:
            embedding_model = config.get('search', {}).get('embedding_model', 'sentence-transformers/msmarco-bert-base-dot-v5')
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
        
        # Check if Ollama models are available
        self._check_ollama_models()
    
    def _check_ollama_models(self):
        """Check if required Ollama models are available."""
        try:
            models = self.ollama_client.list()
            available_models = [model['name'] for model in models['models']]
            
            vision_model = self.ollama_config.get('vision_model', 'llava:latest')
            text_model = self.ollama_config.get('text_model', 'llama3.1:latest')
            
            if vision_model not in available_models:
                logger.warning(f"Vision model {vision_model} not found. Available models: {available_models}")
                logger.info("You may need to pull the model: ollama pull llava:latest")
            
            if text_model not in available_models:
                logger.warning(f"Text model {text_model} not found. Available models: {available_models}")
                logger.info("You may need to pull the model: ollama pull llama3.1:latest")
                
        except Exception as e:
            logger.error(f"Error checking Ollama models: {e}")
    
    def analyze_media(self, media_file: MediaFile) -> MediaFile:
        """Perform complete AI analysis on a media file."""
        try:
            if media_file.file_type == 'image':
                return self._analyze_image(media_file)
            elif media_file.file_type == 'video':
                return self._analyze_video(media_file)
            elif media_file.file_type == 'document':
                return self._analyze_document(media_file)
            else:
                logger.warning(f"Unsupported media type for AI analysis: {media_file.file_type}")
                return media_file
                
        except Exception as e:
            logger.error(f"AI analysis failed for {media_file.file_path}: {e}")
            return media_file
    
    def _analyze_image(self, media_file: MediaFile) -> MediaFile:
        """Analyze an image file using vision models."""
        try:
            if not self.vision_config.get('enabled', True):
                return media_file
            
            # Load and prepare image
            image = Image.open(media_file.file_path)
            
            # Convert to base64 for Ollama
            image_b64 = self._image_to_base64(image)
            
            # Generate description using vision model
            if self.vision_config.get('generate_descriptions', True):
                media_file.ai_description = self._generate_image_description(image_b64)
            
            # Extract tags and objects
            if self.vision_config.get('extract_tags', True):
                media_file.ai_tags = self._extract_image_tags(image_b64)
            
            if self.vision_config.get('detect_objects', True):
                media_file.detected_objects = self._detect_objects(image_b64)
            
            if self.vision_config.get('analyze_scenes', True):
                media_file.scene_type = self._analyze_scene(image_b64)
            
            if self.vision_config.get('extract_text', True):
                media_file.extracted_text = self._extract_text_from_image(image_b64)
            
            logger.debug(f"AI analysis completed for image: {media_file.file_name}")
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
        
        return media_file
    
    def _analyze_video(self, media_file: MediaFile) -> MediaFile:
        """Analyze a video file by extracting key frames."""
        try:
            if not self.vision_config.get('enabled', True):
                return media_file
            
            # Extract key frames
            frames = self._extract_video_frames(media_file.file_path)
            
            if not frames:
                logger.warning(f"No frames extracted from video: {media_file.file_path}")
                return media_file
            
            # Analyze the most representative frame
            representative_frame = frames[len(frames) // 2]  # Middle frame
            image_b64 = self._image_to_base64(representative_frame)
            
            # Generate description
            if self.vision_config.get('generate_descriptions', True):
                media_file.ai_description = self._generate_video_description(image_b64)
            
            # Extract tags from multiple frames
            if self.vision_config.get('extract_tags', True):
                all_tags = []
                for frame in frames[:3]:  # Analyze first 3 frames
                    frame_b64 = self._image_to_base64(frame)
                    tags = self._extract_image_tags(frame_b64)
                    all_tags.extend(tags)
                
                # Remove duplicates and take most common tags
                media_file.ai_tags = list(set(all_tags))[:15]
            
            logger.debug(f"AI analysis completed for video: {media_file.file_name}")
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
        
        return media_file
    
    def _analyze_document(self, media_file: MediaFile) -> MediaFile:
        """Analyze a document file using text models."""
        try:
            if not media_file.text_content:
                return media_file
            
            # Generate summary/description
            if self.vision_config.get('generate_descriptions', True):
                media_file.ai_description = self._generate_document_summary(media_file.text_content)
            
            # Extract key topics/tags
            if self.vision_config.get('extract_tags', True):
                media_file.ai_tags = self._extract_document_tags(media_file.text_content)
            
            logger.debug(f"AI analysis completed for document: {media_file.file_name}")
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
        
        return media_file
    
    def _generate_image_description(self, image_b64: str) -> str:
        """Generate a detailed description of an image."""
        try:
            prompt = """Analyze this image and provide a detailed description. Include:
1. Main subjects and objects visible
2. Setting/location (indoor/outdoor, type of place)
3. Colors, lighting, and mood
4. Activities or actions taking place
5. Any notable details or interesting elements

Keep the description concise but informative (max 300 words)."""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('vision_model', 'llava:latest'),
                prompt=prompt,
                images=[image_b64]
            )
            
            return response['response'].strip()
            
        except Exception as e:
            logger.error(f"Failed to generate image description: {e}")
            return ""
    
    def _generate_video_description(self, frame_b64: str) -> str:
        """Generate a description for a video based on a representative frame."""
        try:
            prompt = """This is a frame from a video. Describe what's happening in this video based on this frame. Include:
1. The main scene or setting
2. Any people, objects, or activities visible
3. The likely context or purpose of the video
4. Visual style or quality

Keep it concise (max 200 words)."""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('vision_model', 'llava:latest'),
                prompt=prompt,
                images=[frame_b64]
            )
            
            return response['response'].strip()
            
        except Exception as e:
            logger.error(f"Failed to generate video description: {e}")
            return ""
    
    def _generate_document_summary(self, text_content: str) -> str:
        """Generate a summary of document content."""
        try:
            # Truncate text if too long
            max_length = 2000
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "..."
            
            prompt = f"""Summarize the following document content in 2-3 sentences. Focus on the main topics and key information:

{text_content}

Summary:"""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('text_model', 'llama3.1:latest'),
                prompt=prompt
            )
            
            return response['response'].strip()
            
        except Exception as e:
            logger.error(f"Failed to generate document summary: {e}")
            return ""
    
    def _extract_image_tags(self, image_b64: str) -> List[str]:
        """Extract relevant tags from an image."""
        try:
            prompt = """Look at this image and generate relevant tags/keywords that describe it. Focus on:
- Objects and subjects
- Activities
- Setting/location type
- Style or mood
- Colors (only if distinctive)

Provide 5-15 single-word tags separated by commas. Be specific and accurate."""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('vision_model', 'llava:latest'),
                prompt=prompt,
                images=[image_b64]
            )
            
            # Parse tags from response
            tags_text = response['response'].strip()
            tags = [tag.strip().lower() for tag in tags_text.split(',') if tag.strip()]
            
            return tags[:15]  # Limit to 15 tags
            
        except Exception as e:
            logger.error(f"Failed to extract tags: {e}")
            return []
    
    def _extract_document_tags(self, text_content: str) -> List[str]:
        """Extract key topics/tags from document content."""
        try:
            # Truncate text if too long
            max_length = 1500
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "..."
            
            prompt = f"""Extract 5-10 key topics/tags from this document content. Focus on main subjects, themes, and important concepts:

{text_content}

Key topics (comma-separated):"""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('text_model', 'llama3.1:latest'),
                prompt=prompt
            )
            
            # Parse tags from response
            tags_text = response['response'].strip()
            tags = [tag.strip().lower() for tag in tags_text.split(',') if tag.strip()]
            
            return tags[:10]  # Limit to 10 tags
            
        except Exception as e:
            logger.error(f"Failed to extract document tags: {e}")
            return []
    
    def _detect_objects(self, image_b64: str) -> List[str]:
        """Detect and list objects in the image."""
        try:
            prompt = """List the main objects visible in this image. Focus on:
- People (person, child, adult, etc.)
- Animals
- Vehicles
- Buildings/structures
- Nature elements
- Common objects

Provide a comma-separated list of objects. Be specific but not overly detailed."""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('vision_model', 'llava:latest'),
                prompt=prompt,
                images=[image_b64]
            )
            
            objects_text = response['response'].strip()
            objects = [obj.strip().lower() for obj in objects_text.split(',') if obj.strip()]
            
            return objects[:10]  # Limit to 10 objects
            
        except Exception as e:
            logger.error(f"Failed to detect objects: {e}")
            return []
    
    def _analyze_scene(self, image_b64: str) -> str:
        """Analyze the scene type of the image."""
        try:
            prompt = """Classify the scene in this image. Choose the most appropriate category:
- indoor/outdoor
- nature/urban/suburban
- home/office/public/commercial
- event/casual/formal

Provide just the main scene type in 1-3 words."""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('vision_model', 'llava:latest'),
                prompt=prompt,
                images=[image_b64]
            )
            
            return response['response'].strip().lower()
            
        except Exception as e:
            logger.error(f"Failed to analyze scene: {e}")
            return ""
    
    def _extract_text_from_image(self, image_b64: str) -> str:
        """Extract any visible text from the image."""
        try:
            prompt = """Look for any text visible in this image (signs, labels, documents, etc.). 
If you see any readable text, transcribe it exactly. If no text is visible, respond with 'no text found'."""

            response = self.ollama_client.generate(
                model=self.ollama_config.get('vision_model', 'llava:latest'),
                prompt=prompt,
                images=[image_b64]
            )
            
            text = response['response'].strip()
            return text if text.lower() != 'no text found' else ""
            
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return ""
    
    def _extract_video_frames(self, video_path: str, max_frames: int = 5) -> List[Image.Image]:
        """Extract representative frames from a video."""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return frames
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                logger.warning(f"Video has no frames: {video_path}")
                cap.release()
                return frames
            
            # Extract frames at regular intervals
            frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    frames.append(pil_image)
            
            cap.release()
            logger.debug(f"Extracted {len(frames)} frames from video")
            return frames
            
        except Exception as e:
            logger.error(f"Failed to extract video frames: {e}")
            return []
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        try:
            buffer = BytesIO()
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffer, format='JPEG', quality=85)
            img_data = buffer.getvalue()
            return base64.b64encode(img_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {e}")
            return ""
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using sentence transformers."""
        try:
            if not text:
                return []
            
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return []
    
    def search_similar_content(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for similar content using text similarity."""
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings(query)
            if not query_embedding:
                return []
            
            # This would integrate with the vector database
            # For now, return empty list as placeholder
            return []
            
        except Exception as e:
            logger.error(f"Similar content search failed: {e}")
            return []

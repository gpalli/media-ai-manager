#!/usr/bin/env python3
"""
Streamlit web application for MediaMind AI.
Enhanced media search engine with modern UI.
Based on the original Towards AI implementation but enhanced for media files.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
from PIL import Image
import json

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.search_engine import EnhancedMediaSearchEngine
from core.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="MediaMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .media-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .media-thumbnail {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    .tag-badge {
        background: #e1f5fe;
        color: #0277bd;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
    }
    
    .search-result {
        border-left: 4px solid #667eea;
        padding-left: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_search_engine():
    """Initialize the search engine with caching."""
    try:
        engine = EnhancedMediaSearchEngine()
        return engine
    except Exception as e:
        st.error(f"Failed to initialize search engine: {e}")
        return None

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 MediaMind AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Local Media Search Engine with AI-Powered Analysis</p>', unsafe_allow_html=True)
    
    # Initialize search engine
    search_engine = initialize_search_engine()
    if not search_engine:
        st.error("Failed to initialize search engine. Please check your configuration.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Scan paths configuration
        st.subheader("📁 Scan Paths")
        current_paths = search_engine.config_loader.get('media.scan_paths', [])
        
        new_path = st.text_input("Add new scan path:", placeholder="/path/to/your/media")
        if st.button("Add Path") and new_path:
            if os.path.exists(new_path):
                search_engine.update_scan_paths(current_paths + [new_path])
                st.success(f"Added path: {new_path}")
                st.rerun()
            else:
                st.error("Path does not exist!")
        
        # Display current paths
        if current_paths:
            st.write("Current scan paths:")
            for path in current_paths:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📂 {path}")
                with col2:
                    if st.button("❌", key=f"remove_{path}"):
                        new_paths = [p for p in current_paths if p != path]
                        search_engine.update_scan_paths(new_paths)
                        st.rerun()
        
        # Statistics
        st.subheader("📊 Statistics")
        stats = search_engine.get_scan_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Files", stats.get('total_files', 0))
        with col2:
            st.metric("Database Size", f"{stats.get('database_size', 0) / 1024 / 1024:.1f} MB")
        
        # Scan information
        scan_info = stats.get('scan_info', {})
        if scan_info.get('last_scan_time'):
            st.write(f"**Last Scan:** {scan_info['last_scan_time']}")
        if scan_info.get('processed_files_count'):
            st.write(f"**Processed Files:** {scan_info['processed_files_count']}")
        
        # File types
        if stats.get('by_type'):
            st.write("Files by type:")
            for file_type, count in stats['by_type'].items():
                st.write(f"• {file_type.title()}: {count}")
        
        # Top tags
        if stats.get('top_tags'):
            st.write("Top tags:")
            for tag_info in stats['top_tags'][:5]:
                st.write(f"• {tag_info['tag']} ({tag_info['count']})")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search", "📊 Scan & Index", "📁 Collections", "ℹ️ About"])
    
    with tab1:
        search_interface(search_engine)
    
    with tab2:
        scan_interface(search_engine)
    
    with tab3:
        collections_interface(search_engine)
    
    with tab4:
        about_interface()

def search_interface(search_engine):
    """Search interface tab."""
    st.header("🔍 Search Your Media")
    
    # Search options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "Search query:",
            placeholder="e.g., 'photos of mountains', 'videos from last year', 'documents about AI'",
            help="Enter a natural language query to search through your media files"
        )
    
    with col2:
        search_type = st.selectbox(
            "Search type:",
            ["Semantic Search", "Text Search", "Tag Search"],
            help="Choose how to search through your media"
        )
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            file_type = st.selectbox(
                "File type:",
                ["All", "image", "video", "document"],
                index=0
            )
        
        with col2:
            scene_type = st.selectbox(
                "Scene type:",
                ["All", "indoor", "outdoor", "nature", "urban"],
                index=0
            )
        
        with col3:
            date_range = st.selectbox(
                "Date range:",
                ["All time", "Last week", "Last month", "Last year"],
                index=0
            )
    
    # Search button
    if st.button("🔍 Search", type="primary"):
        if search_query:
            with st.spinner("Searching..."):
                # Prepare search parameters
                search_params = {}
                
                if file_type != "All":
                    search_params['file_type'] = file_type
                
                if scene_type != "All":
                    search_params['scene_type'] = scene_type
                
                # Date range
                if date_range != "All time":
                    now = datetime.now()
                    if date_range == "Last week":
                        search_params['date_from'] = now - timedelta(weeks=1)
                    elif date_range == "Last month":
                        search_params['date_from'] = now - timedelta(days=30)
                    elif date_range == "Last year":
                        search_params['date_from'] = now - timedelta(days=365)
                
                # Perform search
                if search_type == "Semantic Search":
                    results = search_engine.semantic_search(search_query, limit=20)
                else:
                    search_params['query'] = search_query
                    results = search_engine.search_media(**search_params, limit=20)
                
                # Display results
                display_search_results(results, search_engine)
        else:
            st.warning("Please enter a search query.")
    
    # Quick search examples
    st.subheader("💡 Quick Search Examples")
    examples = [
        "photos of people",
        "videos from vacation",
        "documents about machine learning",
        "images with text",
        "outdoor scenes"
    ]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(example, key=f"example_{i}"):
                st.session_state.search_query = example
                st.rerun()

def display_search_results(results: List[Dict], search_engine):
    """Display search results in a nice format."""
    if not results:
        st.info("No results found. Try adjusting your search criteria.")
        return
    
    st.success(f"Found {len(results)} results")
    
    # Results grid
    for i, result in enumerate(results):
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Thumbnail
                if result.get('file_type') in ['image', 'video']:
                    try:
                        if os.path.exists(result['file_path']):
                            if result['file_type'] == 'image':
                                img = Image.open(result['file_path'])
                                img.thumbnail((200, 200))
                                st.image(img, use_column_width=True)
                            else:
                                st.write("🎥 Video file")
                        else:
                            st.write("📁 File not found")
                    except Exception as e:
                        st.write("❌ Error loading preview")
                else:
                    st.write("📄 Document")
            
            with col2:
                # File info
                st.markdown(f"**{result['file_name']}**")
                st.write(f"📁 {result['file_path']}")
                st.write(f"📊 {result['file_type'].title()} • {result['file_size'] / 1024 / 1024:.1f} MB")
                
                # AI description
                if result.get('ai_description'):
                    st.write(f"🤖 {result['ai_description']}")
                
                # Tags
                if result.get('ai_tags'):
                    tags_html = " ".join([f'<span class="tag-badge">{tag}</span>' for tag in result['ai_tags'][:10]])
                    st.markdown(f"🏷️ {tags_html}", unsafe_allow_html=True)
                
                # Similarity score (for semantic search)
                if 'similarity_score' in result:
                    st.write(f"🎯 Similarity: {result['similarity_score']:.2f}")
                
                # Actions
                col_a, col_b, col_c = st.columns([1, 1, 1])
                with col_a:
                    if st.button("📂 Open Location", key=f"open_{i}"):
                        open_file_location(result['file_path'])
                with col_b:
                    if st.button("🔍 Similar", key=f"similar_{i}"):
                        find_similar_media(result['id'], search_engine)
                with col_c:
                    if st.button("➕ Add to Collection", key=f"add_{i}"):
                        st.session_state.selected_media = result['id']
                        st.session_state.show_collection_dialog = True
            
            st.divider()

def open_file_location(file_path: str):
    """Open file location in system file manager."""
    import subprocess
    import platform
    
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", "-R", file_path])
        elif system == "Windows":
            subprocess.run(["explorer", "/select,", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", os.path.dirname(file_path)])
        
        st.success("File location opened!")
    except Exception as e:
        st.error(f"Failed to open file location: {e}")

def find_similar_media(media_id: int, search_engine):
    """Find similar media files."""
    with st.spinner("Finding similar media..."):
        similar = search_engine.search_similar_media(media_id, limit=5)
        if similar:
            st.write("Similar media:")
            for item in similar:
                st.write(f"• {item['file_name']} - {item.get('ai_description', 'No description')}")
        else:
            st.info("No similar media found.")

def scan_interface(search_engine):
    """Scan and index interface tab."""
    st.header("📊 Scan & Index Media")
    
    # Current scan paths
    st.subheader("📁 Current Scan Paths")
    current_paths = search_engine.config_loader.get('media.scan_paths', [])
    
    if current_paths:
        for path in current_paths:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📂 {path}")
            with col2:
                if os.path.exists(path):
                    st.success("✅ Exists")
                else:
                    st.error("❌ Not found")
            with col3:
                if st.button("🗑️", key=f"remove_{path}"):
                    new_paths = [p for p in current_paths if p != path]
                    search_engine.update_scan_paths(new_paths)
                    st.rerun()
    else:
        st.warning("No scan paths configured. Add some paths to start scanning.")
    
    # Add new path
    st.subheader("➕ Add New Scan Path")
    new_path = st.text_input("Enter path to scan:", placeholder="/path/to/your/media")
    if st.button("Add Path") and new_path:
        if os.path.exists(new_path):
            search_engine.update_scan_paths(current_paths + [new_path])
            st.success(f"Added path: {new_path}")
            st.rerun()
        else:
            st.error("Path does not exist!")
    
    # Scan options
    st.subheader("🔍 Scan Options")
    
    # Scan mode selection
    scan_mode = st.radio(
        "Scan Mode:",
        ["Incremental Scan (Recommended)", "Full Scan"],
        help="Incremental scan only processes new/changed files. Full scan processes all files."
    )
    
    incremental = scan_mode == "Incremental Scan (Recommended)"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        scan_all = st.button("🚀 Scan All Paths", type="primary")
    with col2:
        scan_current = st.button("🔄 Rescan Current")
    with col3:
        force_full = st.button("🔄 Force Full Scan", help="Reset scan state and do full scan")
    
    if force_full:
        search_engine.reset_scan_state()
        st.success("Scan state reset! Next scan will be a full scan.")
        st.rerun()
    
    if scan_all or scan_current:
        with st.spinner(f"Scanning media files ({'incremental' if incremental else 'full'} mode)..."):
            if scan_all:
                result = search_engine.scan_and_index_media(incremental=incremental)
            else:
                # Rescan current paths
                result = search_engine.scan_and_index_media(current_paths, incremental=incremental)
            
            # Display results
            st.success("Scan completed!")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Processed", result['processed'])
            with col2:
                st.metric("Skipped", result['skipped'])
            with col3:
                st.metric("Errors", result['errors'])
            with col4:
                st.metric("Deleted", result.get('deleted', 0))
            with col5:
                st.metric("Total", result.get('total', result['processed'] + result['skipped'] + result['errors']))

def collections_interface(search_engine):
    """Collections interface tab."""
    st.header("📁 Collections")
    
    # Create new collection
    with st.expander("➕ Create New Collection"):
        col1, col2 = st.columns([2, 1])
        with col1:
            collection_name = st.text_input("Collection name:")
            collection_desc = st.text_area("Description (optional):")
        with col2:
            if st.button("Create Collection"):
                if collection_name:
                    collection_id = search_engine.create_collection(collection_name, collection_desc, [])
                    st.success(f"Created collection: {collection_name}")
                    st.rerun()
                else:
                    st.error("Please enter a collection name")
    
    # Display collections
    collections = search_engine.get_collections()
    
    if collections:
        for collection in collections:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{collection['name']}**")
                    if collection['description']:
                        st.write(collection['description'])
                    st.write(f"📊 {collection['item_count']} items")
                with col2:
                    st.write(f"📅 {collection['created_date']}")
                with col3:
                    if st.button("🗑️", key=f"delete_{collection['id']}"):
                        st.warning("Delete functionality not implemented yet")
                
                st.divider()
    else:
        st.info("No collections created yet.")

def about_interface():
    """About interface tab."""
    st.header("ℹ️ About MediaMind AI")
    
    st.markdown("""
    **MediaMind AI** is an enhanced local media search engine that uses AI to help you find and organize your photos, videos, and documents.
    
    ### 🚀 Features
    
    - **AI-Powered Search**: Use natural language to find your media files
    - **Smart Analysis**: Automatically generates descriptions, tags, and metadata
    - **Multiple File Types**: Supports images, videos, and documents
    - **Local Processing**: All analysis happens on your computer for privacy
    - **Collections**: Save and organize your search results
    - **Similarity Search**: Find similar media files
    
    ### 🛠️ Technology Stack
    
    - **Ollama**: Local AI models for analysis
    - **FAISS**: Vector similarity search
    - **Sentence Transformers**: Text embeddings
    - **Streamlit**: Web interface
    - **SQLite**: Metadata storage
    
    ### 📖 How to Use
    
    1. **Configure Scan Paths**: Add directories containing your media files
    2. **Scan & Index**: Process your media files with AI analysis
    3. **Search**: Use natural language to find what you're looking for
    4. **Organize**: Create collections to save your favorite results
    
    ### 🔧 Setup Requirements
    
    - Python 3.8+
    - Ollama installed and running
    - Required models: `llava:latest` and `llama3.1:latest`
    
    ### 📝 Installation
    
    ```bash
    # Install Ollama
    curl -fsSL https://ollama.com/install.sh | sh
    
    # Pull required models
    ollama pull llava:latest
    ollama pull llama3.1:latest
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    # Run the application
    streamlit run web/app.py
    ```
    
    ### 🤝 Contributing
    
    This project is based on the excellent work from the Towards AI article:
    [Building Your Own Generative Search Engine for Local Files](https://pub.towardsai.net/building-your-own-generative-search-engine-for-local-files-using-open-source-models-b09af871751c)
    
    ### 📄 License
    
    This project is open source and available under the MIT License.
    """)

if __name__ == "__main__":
    main()

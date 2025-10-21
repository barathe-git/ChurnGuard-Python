"""
CSS Loader Utility
Loads static CSS files for Streamlit pages
"""
import streamlit as st
import os
from pathlib import Path

def get_css_file_path(filename: str) -> Path:
    """Get the path to a CSS file"""
    current_dir = Path(__file__).parent.parent
    css_path = current_dir / "static" / "css" / filename
    return css_path

def load_css(filename: str) -> str:
    """Load CSS file content"""
    try:
        css_path = get_css_file_path(filename)
        if css_path.exists():
            with open(css_path, 'r') as f:
                return f.read()
        return ""
    except Exception as e:
        print(f"Error loading CSS file {filename}: {str(e)}")
        return ""

def inject_css(css_content: str):
    """Inject CSS into Streamlit page"""
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def load_page_css(*filenames: str):
    """Load and inject multiple CSS files"""
    for filename in filenames:
        css_content = load_css(filename)
        inject_css(css_content)


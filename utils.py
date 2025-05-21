import os
import json
import logging
import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger("wezterm_gui")

def load_css():
    """Load custom CSS"""
    try:
        css_path = os.path.join(os.path.dirname(__file__), "assets/styles.css")
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"CSS yüklenirken hata: {e}")
        st.warning("Arayüz stilleri yüklenemedi.")

def config_has_changed(new_config, current_config):
    """Check if config has changed significantly from current state"""
    # Check complex structures first
    if isinstance(new_config.get('custom_colors'), dict) and isinstance(current_config.get('custom_colors'), dict):
        if str(new_config['custom_colors']) != str(current_config['custom_colors']):
            return True
            
    # Check lists
    if isinstance(new_config.get('hyperlinkRules'), list) and isinstance(current_config.get('hyperlinkRules'), list):
        if set(new_config['hyperlinkRules'] or []) != set(current_config['hyperlinkRules'] or []):
            return True
    
    # Check all other values
    for key, value in new_config.items():
        if key not in ('custom_colors', 'hyperlinkRules') and value != current_config.get(key):
            return True
            
    return False

def update_terminal_js(config, theme_colors):
    """Generate and execute JavaScript for terminal updates"""
    cursor_styles = {
        'Block': f"background:{theme_colors['prompt']};color:black;",
        'Bar': f"border-left:2px solid {theme_colors['prompt']};",
        'Underline': f"border-bottom:2px solid {theme_colors['prompt']};"
    }
    cursor_style_css = cursor_styles.get(config['cursor_style'], cursor_styles['Block'])
    
    js_update = {
        'bg': theme_colors['bg'],
        'fg': theme_colors['fg'],
        'promptColor': theme_colors['prompt'],
        'cursorStyle': cursor_style_css,
        'fontSize': config['font_size'],
        'lineHeight': config['line_height'],
        'font': config['font'],
        'padding': config['padding'],
        'opacity': config['opacity'],
        'enableTabBar': config['enable_tab_bar'],
        'enableScrollBar': config['enable_scroll_bar']
    }
    
    js_code = f"if (window.updateTerminalConfig) {{ window.updateTerminalConfig('{json.dumps(js_update)}'); }}"
    components.html(f"<script>{js_code}</script>", height=0)

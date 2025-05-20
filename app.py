import streamlit as st
import json
import os
import streamlit.components.v1 as components
import platform
from pathlib import Path
import logging
import traceback
import tempfile

# Streamlit Cloud'da log dosyasını geçici dizinde oluştur
log_dir = tempfile.gettempdir()
log_file = os.path.join(log_dir, "wezterm_gui.log")

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("wezterm_gui")

class TerminalPreviewGenerator:
    """Terminal önizlemesi oluşturan sınıf"""
    
    @staticmethod
    def generate_terminal_html_components(colors, enable_tab_bar, use_fancy_tab_bar, 
                                        enable_scroll_bar, cursor_style, hyperlinkRules, leader_key):
        """Generate HTML components for terminal preview"""
        components = {}
        
        # Tab bar component
        if enable_tab_bar:
            tab_bar_bg = colors['bg'] if not use_fancy_tab_bar else 'rgba(0,0,0,0.3)'
            active_tab_bg = colors['prompt'] if use_fancy_tab_bar else 'rgba(255,255,255,0.1)'
            inactive_tab_color = colors['fg'] if use_fancy_tab_bar else 'rgba(255,255,255,0.6)'
            
            tab_style = f"""
                background-color: {tab_bar_bg};
                color: {colors['fg']};
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                padding: 5px 0;
                display: flex;
                align-items: center;
            """
            
            components['tab_bar'] = f"""
            <div style="{tab_style}">
                <div style="display: flex; overflow-x: auto; padding: 0 10px; width: 100%;">
                    <div style="background-color: {active_tab_bg}; color: {colors['fg']}; border-radius: 3px; padding: 4px 12px; margin-right: 5px; font-size: 12px; display: flex; align-items: center;">
                        <span style="margin-right: 8px;">bash</span>
                        {'<span style="font-size: 10px; opacity: 0.7;">✕</span>' if use_fancy_tab_bar else ''}
                    </div>
                    <div style="color: {inactive_tab_color}; padding: 4px 12px; margin-right: 5px; font-size: 12px; display: flex; align-items: center;">
                        <span style="margin-right: 8px;">zsh</span>
                        {'<span style="font-size: 10px; opacity: 0.7;">✕</span>' if use_fancy_tab_bar else ''}
                    </div>
                    <div style="color: {inactive_tab_color}; padding: 4px 12px; font-size: 12px; display: flex; align-items: center;">
                        <span style="margin-right: 8px;">python</span>
                        {'<span style="font-size: 10px; opacity: 0.7;">✕</span>' if use_fancy_tab_bar else ''}
                    </div>
                </div>
                <div style="padding: 0 10px; font-size: 14px; cursor: pointer;">+</div>
            </div>
            """
        else:
            components['tab_bar'] = ""
        
        # Cursor style component
        if cursor_style == 'Block':
            components['cursor'] = f"display: inline-block; background-color: {colors['prompt']}; color: black; animation: blink 1s step-end infinite;"
        elif cursor_style == 'Bar':
            components['cursor'] = f"display: inline-block; border-left: 2px solid {colors['prompt']}; animation: blink 1s step-end infinite;"
        elif cursor_style == 'Underline':
            components['cursor'] = f"display: inline-block; border-bottom: 2px solid {colors['prompt']}; animation: blink 1s step-end infinite;"
        
        # Scrollbar component
        if enable_scroll_bar:
            components['scrollbar'] = f"""
            <div style="width: 10px; background-color: {colors['bg']}; border-left: 1px solid rgba(255, 255, 255, 0.15); position: relative;">
                <div style="position: absolute; top: 0; right: 0; width: 8px; height: 30px; background-color: rgba(255, 255, 255, 0.3); border-radius: 4px; margin: 2px;"></div>
            </div>
            """
        else:
            components['scrollbar'] = ""

        # Hyperlink examples component
        hyperlink_examples = ""
        if hyperlinkRules:
            hyperlink_examples += "<span style='color: #888888;'># Hyperlink examples:</span><br>"
            
            if 'URL Algılama' in hyperlinkRules:
                hyperlink_examples += f"<span style='color: {colors['fg']}; text-decoration: underline; cursor: pointer;'>https://example.com</span><br>"
            
            if 'Dosya Yolları' in hyperlinkRules:
                hyperlink_examples += f"<span style='color: {colors['fg']}; text-decoration: underline; cursor: pointer;'>/home/user/file.txt</span><br>"
                
            if 'E-posta Adresleri' in hyperlinkRules:
                hyperlink_examples += f"<span style='color: {colors['fg']}; text-decoration: underline; cursor: pointer;'>user@example.com</span><br>"
            
            hyperlink_examples += "<br>"
        components['hyperlinks'] = hyperlink_examples

        # Leader key example component
        if leader_key:
            leader_key_example = f"<span style='color: #888888;'># Leader key ({leader_key}) example:</span><br>"
            leader_key_example += f"<span style='color: {colors['fg']}'>Press {leader_key} followed by a key to activate shortcuts</span><br><br>"
        else:
            leader_key_example = ""
        components['leader_key'] = leader_key_example
        
        # Animation for cursor blinking
        components['animations'] = """
        <style>
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0; }
          100% { opacity: 1; }
        }
        </style>
        """
        
        return components

    @staticmethod
    def generate_settings_table(theme, color_scheme, font, font_size, opacity, padding, 
                              line_height, cursor_style, enable_tab_bar, use_fancy_tab_bar, 
                              enable_scroll_bar, hyperlinkRules, leader_key, colors):
        """Generate HTML for settings table in preview"""
        return f"""
        <div style="
            margin-top: 15px; 
            padding: 15px; 
            background-color: #f5f5f5; 
            border-radius: 6px; 
            color: #333;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        ">
            <h4 style="margin: 0 0 15px 0; border-bottom: 1px solid #ddd; padding-bottom: 8px; color: #444;">Aktif Yapılandırma Ayarları</h4>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <th style="text-align: left; width: 33%; padding: 6px; border-bottom: 1px solid #ddd;">Ayar</th>
                    <th style="text-align: left; width: 67%; padding: 6px; border-bottom: 1px solid #ddd;">Değer</th>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Tema</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{theme}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Renk Şeması</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{color_scheme}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Yazı Tipi</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{font}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Yazı Boyutu</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{font_size}px</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Opaklık</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{opacity:.2f}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">İç Dolgu (Padding)</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{padding}px</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Satır Yüksekliği</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{line_height}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">İmleç Stili</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{cursor_style}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Sekme Çubuğu</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{'Etkin' if enable_tab_bar else 'Devre Dışı'}{' (Süslü)' if use_fancy_tab_bar and enable_tab_bar else ''}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Kaydırma Çubuğu</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{'Etkin' if enable_scroll_bar else 'Devre Dışı'}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Bağlantı Kuralları</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{', '.join(hyperlinkRules) if hyperlinkRules else 'Yok'}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;">Lider Tuşu</td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{leader_key if leader_key else 'Tanımlanmamış'}</code></td>
                </tr>
                <tr>
                    <td style="padding: 6px;">Renk Değerleri</td>
                    <td style="padding: 6px;">
                        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                            <div style="display: flex; align-items: center;">
                                <div style="width: 15px; height: 15px; background-color: {colors['bg']}; border: 1px solid #ccc; margin-right: 5px;"></div>
                                Arka Plan: <code>{colors['bg']}</code>
                            </div>
                            <div style="display: flex; align-items: center;">
                                <div style="width: 15px; height: 15px; background-color: {colors['fg']}; border: 1px solid #ccc; margin-right: 5px;"></div>
                                Yazı: <code>{colors['fg']}</code>
                            </div>
                            <div style="display: flex; align-items: center;">
                                <div style="width: 15px; height: 15px; background-color: {colors['prompt']}; border: 1px solid #ccc; margin-right: 5px;"></div>
                                Prompt: <code>{colors['prompt']}</code>
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """

    @staticmethod
    def generate_terminal_preview(theme, font, font_size, color_scheme, custom_colors=None, opacity=0.95,
                                enable_tab_bar=True, enable_scroll_bar=False, cursor_style='Block',
                                padding=8, line_height=1.0, use_fancy_tab_bar=True, hyperlinkRules=None,
                                leader_key=None):
        """Generate HTML for terminal preview with all settings visible"""
        try:
            # Get appropriate colors
            colors = WezTermConfigurator.get_colors_for_theme(theme, color_scheme, custom_colors)
            
            # Calculate content height based on whether tab bar is enabled
            content_height = 350 - (30 if enable_tab_bar else 0)
            
            # Generate HTML components
            components = TerminalPreviewGenerator.generate_terminal_html_components(
                colors, enable_tab_bar, use_fancy_tab_bar, enable_scroll_bar, 
                cursor_style, hyperlinkRules, leader_key
            )
            
            # Create main terminal container with padding
            terminal_html = components['animations'] + f"""
            <div style="
                background-color: #2c2c2c;
                border-radius: 6px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
                overflow: hidden;
                width: 100%;
                font-family: '{font}', monospace;
                font-size: {font_size}px;
                position: relative;
                margin-bottom: 20px;
            ">
                <!-- Window decorations - title bar -->
                <div style="
                    display: flex;
                    background-color: #21252b;
                    padding: 8px 15px;
                    align-items: center;
                    user-select: none;
                ">
                    <div style="display: flex; gap: 6px;">
                        <div style="height: 12px; width: 12px; background-color: #ff5f56; border-radius: 50%;"></div>
                        <div style="height: 12px; width: 12px; background-color: #ffbd2e; border-radius: 50%;"></div>
                        <div style="height: 12px; width: 12px; background-color: #27c93f; border-radius: 50%;"></div>
                    </div>
                    <div style="flex-grow: 1; text-align: center; color: #9da5b4; font-size: 12px;">
                        WezTerm - user@machine: ~/projects
                    </div>
                </div>
                
                <!-- Tab bar (if enabled) -->
                {components['tab_bar']}
                
                <!-- Terminal content area with scrollbar -->
                <div style="
                    display: flex;
                    height: {content_height}px;
                ">
                    <!-- Main terminal content -->
                    <div style="
                        flex-grow: 1;
                        background-color: {colors['bg']};
                        color: {colors['fg']};
                        padding: {padding}px;
                        opacity: {opacity};
                        overflow: auto;
                        line-height: {line_height};
                        position: relative;
                        white-space: pre;
                        font-variant-ligatures: normal;
                    ">
                        <div>
<span style="color: {colors['prompt']};">user@machine</span><span style="color: {colors['fg']};">:</span><span style="color: #5f87ff;">~/projects</span><span style="color: {colors['prompt']};">$</span> ls -la<br>
total 32<br>
drwxr-xr-x  5 user group  4096 May 20 14:32 .<br>
drwxr-xr-x 18 user group  4096 May 19 10:15 ..<br>
drwxr-xr-x  8 user group  4096 May 20 11:21 .git<br>
-rw-r--r--  1 user group   129 May 18 09:43 .gitignore<br>
-rw-r--r--  1 user group  1523 May 18 09:43 README.md<br>
-rw-r--r--  1 user group   978 May 20 14:30 app.py<br>
drwxr-xr-x  2 user group  4096 May 18 09:43 assets<br>
<br>
{components['hyperlinks']}
{components['leader_key']}
<span style="color: {colors['prompt']};">user@machine</span><span style="color: {colors['fg']};">:</span><span style="color: #5f87ff;">~/projects</span><span style="color: {colors['prompt']};">$</span> <span style="{components['cursor']}">_</span>
                        </div>
                    </div>
                    
                    <!-- Scrollbar (if enabled) -->
                    {components['scrollbar']}
                </div>
            </div>
            """
            
            # Add settings table
            terminal_html += TerminalPreviewGenerator.generate_settings_table(
                theme, color_scheme, font, font_size, opacity, padding, line_height, 
                cursor_style, enable_tab_bar, use_fancy_tab_bar, enable_scroll_bar, 
                hyperlinkRules, leader_key, colors
            )
            
            return terminal_html
        except Exception as e:
            logger.error(f"Terminal önizlemesi oluşturulurken hata: {e}\n{traceback.format_exc()}")
            return f"<div style='color: red; padding: 20px; background-color: #fff0f0; border-radius: 5px;'>Terminal önizlemesi oluşturulamadı: {str(e)}</div>"


class ConfigGenerator:
    """WezTerm yapılandırma dosyası üreten sınıf"""

    @staticmethod
    def generate_wezterm_lua(theme, font, font_size, color_scheme, custom_colors=None, opacity=0.95,
                          enable_tab_bar=True, enable_scroll_bar=False, cursor_style='Block',
                          padding=8, line_height=1.0, use_fancy_tab_bar=True, hyperlinkRules=None,
                          leader_key=None):
        """Generate WezTerm Lua configuration based on user selections"""
        try:
            # Convert cursor style to WezTerm format
            cursor_style_map = {
                'Block': 'SteadyBlock',
                'Bar': 'SteadyBar',
                'Underline': 'SteadyUnderline'
            }
            
            wezterm_cursor_style = cursor_style_map.get(cursor_style, 'SteadyBlock')
            
            # Start generating Lua configuration
            lua_config = f"""local wezterm = require 'wezterm'
local act = wezterm.action

return {{
  -- Font configuration
  font = wezterm.font('{font}'),
  font_size = {font_size},
  line_height = {line_height},
  
  -- Visual settings
  enable_tab_bar = {str(enable_tab_bar).lower()},
  use_fancy_tab_bar = {str(use_fancy_tab_bar).lower()},
  enable_scroll_bar = {str(enable_scroll_bar).lower()},
  window_background_opacity = {opacity},
  cursor_style = '{wezterm_cursor_style}',
  window_padding = {{
    left = {padding},
    right = {padding},
    top = {padding},
    bottom = {padding},
  }},
"""

            # Add hyperlink rules if selected
            if hyperlinkRules and len(hyperlinkRules) > 0:
                lua_config += "  -- Hyperlink settings\n"
                if 'URL Algılama' in hyperlinkRules:
                    lua_config += "  hyperlink_rules = {\n"
                    lua_config += "    -- URL detection\n"
                    lua_config += "    {\n"
                    lua_config += "      regex = '\\\\b\\\\w+://[\\\\w.-]+\\\\.[\\\\w.-]+\\\\S*\\\\b',\n"
                    lua_config += "      format = '$0',\n"
                    lua_config += "    },\n"
                
                if 'E-posta Adresleri' in hyperlinkRules:
                    lua_config += "    -- Email addresses\n"
                    lua_config += "    {\n"
                    lua_config += "      regex = '\\\\b\\\\w+@[\\\\w.-]+\\\\.[\\\\w]+\\\\b',\n"
                    lua_config += "      format = 'mailto:$0',\n"
                    lua_config += "    },\n"
                    
                if 'Dosya Yolları' in hyperlinkRules:
                    lua_config += "    -- File paths\n"
                    lua_config += "    {\n"
                    lua_config += "      regex = '\\\\b(\\\\w+:)?[\\\\/\\\\\\\\][\\\\w.~-]+[\\\\/\\\\\\\\][\\\\w.~-]+\\\\b',\n"
                    lua_config += "      format = '$0',\n"
                    lua_config += "    },\n"
                    
                lua_config += "  },\n"

            # Add leader key if provided
            if leader_key and leader_key.strip():
                # Parse key and modifiers - expected format: "MODIFIER + key"
                parts = [part.strip() for part in leader_key.split('+')]
                if len(parts) >= 2:
                    key = parts[-1].lower()
                    mods = '+'.join(part.upper() for part in parts[:-1])
                else:
                    # Default if the format isn't as expected
                    key = leader_key.strip().lower()
                    mods = 'CTRL'

                lua_config += f"""  -- Leader key configuration
  leader = {{ key = '{key}', mods = '{mods}', timeout_milliseconds = 1000 }},
"""

            # Add color configuration
            if theme == 'Custom' and custom_colors:
                lua_config += f"""  -- Custom colors
  colors = {{
    background = '{custom_colors['bg']}',
    foreground = '{custom_colors['fg']}',
    cursor_bg = '{custom_colors['prompt']}',
    cursor_fg = 'black',
  }},
}}
"""
            else:
                lua_config += f"""  -- Theme color scheme
  color_scheme = '{color_scheme}',
}}
"""
            
            return lua_config
        except Exception as e:
            logger.error(f"Lua yapılandırması oluşturulurken hata: {e}\n{traceback.format_exc()}")
            return None


class WezTermConfigurator:
    """WezTerm yapılandırıcı ana sınıfı"""
    
    # Color mappings and theme mappings
    color_mappings = {
        'Builtin Dark': {'bg': '#121212', 'fg': '#d0d0d0', 'prompt': '#5fafff'},
        'Builtin Light': {'bg': '#f0f0f0', 'fg': '#333333', 'prompt': '#0087af'},
        'Gruvbox': {'bg': '#282828', 'fg': '#ebdbb2', 'prompt': '#b8bb26'},
        'Dracula': {'bg': '#282a36', 'fg': '#f8f8f2', 'prompt': '#bd93f9'},
        'Monokai': {'bg': '#272822', 'fg': '#f8f8f2', 'prompt': '#a6e22e'},
        'Solarized Dark': {'bg': '#002b36', 'fg': '#839496', 'prompt': '#268bd2'},
        'Solarized Light': {'bg': '#fdf6e3', 'fg': '#657b83', 'prompt': '#268bd2'},
        'Nord': {'bg': '#2e3440', 'fg': '#d8dee9', 'prompt': '#88c0d0'}
    }
    
    theme_color_scheme_mapping = {
        'Dark': 'Builtin Dark',
        'Light': 'Builtin Light',
        'Custom': 'Custom'
    }
    
    def __init__(self):
        """Initialize the WezTerm configurator"""
        self.initialize_app()
        self.initialize_session_state()
        self.load_css()

    def initialize_app(self):
        """Initialize the Streamlit app"""
        st.set_page_config(
            layout="wide",
            page_title="WezTerm Configurator",
            page_icon="🖥️",
            menu_items={
                'Get Help': 'https://github.com/yourusername/wezterm-gui',
                'Report a bug': 'https://github.com/yourusername/wezterm-gui/issues',
                'About': "# WezTerm Yapılandırıcı\nWezTerm terminal emülatörü için görsel yapılandırma aracı."
            }
        )

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'theme' not in st.session_state:
            st.session_state['theme'] = 'Dark'
        if 'custom_colors' not in st.session_state:
            st.session_state['custom_colors'] = {'bg': '#282828', 'fg': '#ebdbb2', 'prompt': '#b8bb26'}
        if 'opacity' not in st.session_state:
            st.session_state['opacity'] = 0.95
        if 'selected_color_scheme' not in st.session_state:
            st.session_state['selected_color_scheme'] = 'Builtin Dark'

    def load_css(self):
        """Load custom CSS"""
        try:
            css_path = os.path.join(os.path.dirname(__file__), "assets/styles.css")
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"CSS dosyası yüklenirken hata oluştu: {e}\n{traceback.format_exc()}")
            st.error(f"CSS dosyası yüklenemedi: {e}")
            st.warning("Arayüz stil ayarları yüklenemedi, varsayılan Streamlit stili kullanılıyor.")

    @staticmethod
    def get_colors_for_theme(theme, color_scheme, custom_colors=None):
        """Get color values based on theme and color scheme"""
        if theme == "Custom" and custom_colors:
            return custom_colors
        return WezTermConfigurator.color_mappings.get(color_scheme, WezTermConfigurator.color_mappings['Builtin Dark'])

    @staticmethod
    def get_wezterm_config_path():
        """Get the WezTerm configuration file path based on OS"""
        try:
            # Streamlit Cloud'da doğrudan kaydetme özelliği yerine indirme seçeneği sunulacak
            if os.environ.get('STREAMLIT_SHARING') or os.environ.get('STREAMLIT_CLOUD'):
                return None
                
            if platform.system() == "Windows":
                return str(Path.home() / ".wezterm.lua")
            else:  # Linux/macOS
                config_dir = Path.home() / ".config" / "wezterm"
                return str(config_dir / "wezterm.lua")
        except Exception as e:
            logger.error(f"Yapılandırma yolu belirlenirken hata: {e}\n{traceback.format_exc()}")
            return None

    def save_configuration_to_wezterm(self, lua_code):
        """Save configuration to WezTerm config location"""
        try:
            # Streamlit Cloud'da çalışıyorsa indirme seçeneği öner
            if os.environ.get('STREAMLIT_SHARING') or os.environ.get('STREAMLIT_CLOUD'):
                return False, "Streamlit Cloud üzerinde çalışırken doğrudan kayıt desteklenmez. Lütfen indirme seçeneğini kullanın."
            
            config_path = self.get_wezterm_config_path()
            if not config_path:
                return False, "Yapılandırma yolu belirlenemedi"
                
            config_dir = os.path.dirname(config_path)
            
            # Create directory if it doesn't exist
            if not os.path.exists(config_dir) and config_dir:
                os.makedirs(config_dir)
                
            with open(config_path, 'w') as f:
                f.write(lua_code)
            return True, config_path
        except Exception as e:
            logger.error(f"Yapılandırma kaydedilirken hata: {e}\n{traceback.format_exc()}")
            return False, str(e)

    def import_color_scheme(self, file_content):
        """Import color scheme from JSON"""
        try:
            imported_colors = json.loads(file_content)
            
            if not all(key in imported_colors for key in ['bg', 'fg', 'prompt']):
                raise ValueError("Geçersiz renk şeması formatı. 'bg', 'fg' ve 'prompt' anahtarları olmalı.")
            
            # Update session state
            st.session_state['theme'] = 'Custom'
            st.session_state['custom_colors'] = imported_colors
            st.session_state['opacity'] = 0.95
            
            return True
        except Exception as e:
            logger.error(f"Renk şeması içe aktarılırken hata: {e}\n{traceback.format_exc()}")
            st.error(f"Renk şeması içe aktarılamadı: {e}")
            return False

    def render_sidebar(self):
        """Render the sidebar with all controls"""
        st.sidebar.markdown("## Tema Ayarları")
        theme = st.sidebar.selectbox('Tema', ['Dark', 'Light', 'Custom'],
                                    index=['Dark', 'Light', 'Custom'].index(st.session_state['theme']))
        if theme != st.session_state['theme']:
            st.session_state['theme'] = theme
            # Update selected color scheme based on theme
            if theme != 'Custom':
                st.session_state['selected_color_scheme'] = self.theme_color_scheme_mapping[theme]

        font = st.sidebar.selectbox('Yazı Tipi', ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Hack', 'Source Code Pro', 'Ubuntu Mono', 'Menlo', 'Monaco'])
        font_size = st.sidebar.slider('Yazı Boyutu', 8, 32, 14)

        # Show color scheme selector only if theme is not Custom
        if theme != 'Custom':
            color_scheme_options = list(self.color_mappings.keys())
            color_scheme = st.sidebar.selectbox('Renk Şeması', color_scheme_options, 
                                            index=color_scheme_options.index(st.session_state['selected_color_scheme']))
            if color_scheme != st.session_state['selected_color_scheme']:
                st.session_state['selected_color_scheme'] = color_scheme
        else:
            color_scheme = 'Custom'

        # Custom theme color settings (only shown when Custom theme is selected)
        if st.session_state['theme'] == 'Custom':
            st.sidebar.markdown("## Özel Renk Ayarları")
            custom_colors = st.session_state['custom_colors']
            bg = st.sidebar.color_picker('Arka Plan Rengi', custom_colors['bg'])
            fg = st.sidebar.color_picker('Yazı Rengi', custom_colors['fg'])
            prompt = st.sidebar.color_picker('Prompt Rengi', custom_colors['prompt'])
            opacity = st.sidebar.slider('Pencere Opaklığı', 0.5, 1.0, st.session_state['opacity'])
            # Update session state if changed
            if (bg, fg, prompt) != (custom_colors['bg'], custom_colors['fg'], custom_colors['prompt']):
                st.session_state['custom_colors'] = {'bg': bg, 'fg': fg, 'prompt': prompt}
            if opacity != st.session_state['opacity']:
                st.session_state['opacity'] = opacity
        else:
            custom_colors = {}
            opacity = st.sidebar.slider('Pencere Opaklığı', 0.5, 1.0, st.session_state['opacity'])
            if opacity != st.session_state['opacity']:
                st.session_state['opacity'] = opacity

        # Terminal configuration options
        st.sidebar.markdown("## Terminal Seçenekleri")
        enable_tab_bar = st.sidebar.checkbox('Sekme Çubuğunu Etkinleştir', value=True)
        enable_scroll_bar = st.sidebar.checkbox('Kaydırma Çubuğunu Etkinleştir', value=False)
        cursor_style = st.sidebar.selectbox('İmleç Stili', ['Block', 'Bar', 'Underline'], index=0)

        # Advanced options (collapsible)
        with st.sidebar.expander("Gelişmiş Seçenekler"):
            padding = st.sidebar.slider('Dolgu', 0, 20, 8)
            line_height = st.sidebar.slider('Satır Yüksekliği', 0.8, 2.0, 1.0, 0.1)
            use_fancy_tab_bar = st.sidebar.checkbox('Süslü Sekme Çubuğunu Kullan', value=True)
            hyperlinkRules = st.sidebar.multiselect('Bağlantı Kuralları', 
                                        ['URL Algılama', 'Dosya Yolları', 'E-posta Adresleri'],
                                        ['URL Algılama'])
            leader_key = st.sidebar.text_input('Lider Tuşu', 'CTRL + a')
            
            # Validate leader key format
            if leader_key and '+' not in leader_key:
                st.sidebar.warning("Lider tuşu formatı 'MOD + TUŞ' şeklinde olmalıdır, örneğin 'CTRL + a'")

        # Import/export functionality
        self.render_import_export_sidebar()
        
        # Return all the configuration values
        return {
            'theme': theme,
            'font': font,
            'font_size': font_size,
            'color_scheme': color_scheme,
            'custom_colors': custom_colors,
            'opacity': opacity,
            'enable_tab_bar': enable_tab_bar,
            'enable_scroll_bar': enable_scroll_bar,
            'cursor_style': cursor_style,
            'padding': padding,
            'line_height': line_height,
            'use_fancy_tab_bar': use_fancy_tab_bar,
            'hyperlinkRules': hyperlinkRules,
            'leader_key': leader_key
        }

    def render_import_export_sidebar(self):
        """Render import/export section in the sidebar"""
        st.sidebar.markdown("## İçe/Dışa Aktar")
        import_export = st.sidebar.expander("Renk Şeması İçe/Dışa Aktar")

        with import_export:
            # Export current color scheme
            if st.button("Mevcut Renk Şemasını Dışa Aktar"):
                try:
                    export_data = {}
                    if st.session_state['theme'] == 'Custom':
                        export_data = st.session_state['custom_colors']
                    else:
                        export_data = self.color_mappings.get(st.session_state['selected_color_scheme'], {})
                    export_json = json.dumps(export_data)
                    st.code(export_json)
                    st.download_button(
                        "JSON İndir", 
                        export_json, 
                        file_name=f"{st.session_state['selected_color_scheme'] if st.session_state['theme'] != 'Custom' else 'custom'}_colors.json",
                        mime="application/json"
                    )
                except Exception as e:
                    logger.error(f"Renk şeması dışa aktarılırken hata: {e}\n{traceback.format_exc()}")
                    st.error(f"Renk şeması dışa aktarılamadı: {e}")
            
            # Import color scheme
            st.markdown("### Renk Şeması İçe Aktar")
            upload_file = st.file_uploader("JSON dosyası yükle", type=['json'])
            if upload_file is not None:
                if self.import_color_scheme(upload_file.getvalue().decode()):
                    st.success("Renk şeması başarıyla içe aktarıldı! Lütfen sayfayı manuel olarak yenileyin.")

    def render_config_section(self, config):
        """Render the configuration code section"""
        st.subheader("Yapılandırma Kodu")
        
        # Generate configuration code
        if config['theme'] == 'Custom':
            lua_code = ConfigGenerator.generate_wezterm_lua(
                config['theme'], config['font'], config['font_size'], 
                config['color_scheme'], config['custom_colors'], config['opacity'],
                config['enable_tab_bar'], config['enable_scroll_bar'], config['cursor_style'],
                config['padding'], config['line_height'], config['use_fancy_tab_bar'], 
                config['hyperlinkRules'], config['leader_key']
            )
        else:
            lua_code = ConfigGenerator.generate_wezterm_lua(
                config['theme'], config['font'], config['font_size'], 
                config['color_scheme'], None, config['opacity'],
                config['enable_tab_bar'], config['enable_scroll_bar'], config['cursor_style'],
                config['padding'], config['line_height'], config['use_fancy_tab_bar'], 
                config['hyperlinkRules'], config['leader_key']
            )
        
        if lua_code:
            # Display the Lua code
            st.code(lua_code, language='lua')
            
            # Add download button - her zaman görünür
            st.download_button("wezterm.lua İndir", lua_code, file_name="wezterm.lua")
            
            # Streamlit Cloud kontrolü
            is_cloud = os.environ.get('STREAMLIT_SHARING') or os.environ.get('STREAMLIT_CLOUD')
            
            # Add direct save button - sadece lokal ortamlarda
            if not is_cloud:
                if st.button("Doğrudan WezTerm Yapılandırma Konumuna Kaydet"):
                    success, result = self.save_configuration_to_wezterm(lua_code)
                    if success:
                        st.success(f"Yapılandırma başarıyla kaydedildi: {result}")
                    else:
                        st.error(f"Yapılandırma kaydedilemedi: {result}")
            
            # Kullanım talimatları
            st.info("""
            **Bu yapılandırmayı kullanmak için:**
            1. Yukarıdaki "wezterm.lua İndir" düğmesini kullanarak dosyayı indirin
            2. `~/.config/wezterm/wezterm.lua` (Linux/macOS) veya `%USERPROFILE%\\.wezterm.lua` (Windows) konumuna kaydedin
            3. Değişikliklerinizi görmek için WezTerm'i yeniden başlatın
            """)
            
            # Lokal ortamlar için ek bilgi
            if not is_cloud:
                st.info("Yerel ortamda çalıştığınız için 'Doğrudan WezTerm Yapılandırma Konumuna Kaydet' özelliği de kullanılabilir.")
        else:
            st.error("Yapılandırma kodu oluşturulamadı. Lütfen ayarlarınızı kontrol edin.")

    def render_preview_section(self, config):
        """Render the terminal preview section"""
        st.subheader("Terminal Önizleme")
        
        try:
            # Generate preview HTML
            if config['theme'] == 'Custom':
                terminal_preview = TerminalPreviewGenerator.generate_terminal_preview(
                    config['theme'], config['font'], config['font_size'], config['color_scheme'], 
                    st.session_state['custom_colors'], config['opacity'],
                    config['enable_tab_bar'], config['enable_scroll_bar'], config['cursor_style'],
                    config['padding'], config['line_height'], config['use_fancy_tab_bar'], 
                    config['hyperlinkRules'], config['leader_key']
                )
            else:
                terminal_preview = TerminalPreviewGenerator.generate_terminal_preview(
                    config['theme'], config['font'], config['font_size'], config['color_scheme'], 
                    None, config['opacity'],
                    config['enable_tab_bar'], config['enable_scroll_bar'], config['cursor_style'],
                    config['padding'], config['line_height'], config['use_fancy_tab_bar'], 
                    config['hyperlinkRules'], config['leader_key']
                )
            
            if terminal_preview:
                components.html(terminal_preview, height=650)
            else:
                st.error("Terminal önizlemesi oluşturulamadı.")
        except Exception as e:
            logger.error(f"Terminal önizleme gösterilirken hata: {e}\n{traceback.format_exc()}")
            st.error(f"Terminal önizleme gösterilirken hata: {e}")
            st.warning("Sorunu çözmek için sayfayı yenilemeyi deneyin.")

    def run(self):
        """Run the WezTerm Configurator app"""
        # App title
        st.title('WezTerm Yapılandırıcı')
        st.write('Sol menüden seçimlerinizi yapın ve terminal önizlemesini görün!')
        
        # Render sidebar and get configuration
        config = self.render_sidebar()
        
        # Create two columns for layout
        col1, col2 = st.columns(2)
        
        # Render configuration code in the first column
        with col1:
            self.render_config_section(config)
        
        # Render terminal preview in the second column
        with col2:
            self.render_preview_section(config)


# App başlatma
if __name__ == "__main__":
    app = WezTermConfigurator()
    app.run()

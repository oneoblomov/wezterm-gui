import streamlit as st
import json
import os
import streamlit.components.v1 as components
import logging
import traceback
import tempfile

from terminal import TerminalPreviewGenerator
from config import ConfigGenerator
from themes import COLOR_MAPPINGS, THEME_COLOR_SCHEME_MAPPING, get_colors_for_theme
from utils import load_css, config_has_changed, update_terminal_js

# Setup logging
log_file = os.path.join(tempfile.gettempdir(), "wezterm_gui.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger("wezterm_gui")


class WezTermConfigurator:
    """WezTerm yapılandırıcı ana sınıfı"""
    
    def __init__(self):
        """Initialize the WezTerm configurator"""
        st.set_page_config(layout="wide", page_title="WezTerm Configurator", page_icon="🖥️")
        self.initialize_session_state()
        load_css()
        
        # Initialize terminal state
        if 'terminal_key' not in st.session_state:
            st.session_state.terminal_key = 0
            
        if 'current_config' not in st.session_state:
            st.session_state.current_config = {
                'theme': 'Dark',
                'font': 'JetBrains Mono',
                'font_size': 14,
                'color_scheme': 'Builtin Dark',
                'custom_colors': None,
                'opacity': 0.95,
                'enable_tab_bar': True,
                'enable_scroll_bar': False,
                'cursor_style': 'Block',
                'padding': 8,
                'line_height': 1.0,
                'use_fancy_tab_bar': True,
                'hyperlinkRules': ['URL Algılama'],
                'leader_key': 'CTRL + a'
            }

    def initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'theme': 'Dark',
            'custom_colors': {'bg': '#282828', 'fg': '#ebdbb2', 'prompt': '#b8bb26'},
            'opacity': 0.95,
            'selected_color_scheme': 'Builtin Dark'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def render_sidebar(self):
        """Render sidebar with configuration controls"""
        st.sidebar.markdown("## Tema Ayarları")
        
        # Theme selection
        theme = st.sidebar.selectbox('Tema', ['Dark', 'Light', 'Custom'],
                                   index=['Dark', 'Light', 'Custom'].index(st.session_state['theme']))
        if theme != st.session_state['theme']:
            st.session_state['theme'] = theme
            if theme != 'Custom':
                st.session_state['selected_color_scheme'] = THEME_COLOR_SCHEME_MAPPING[theme]

        # Font settings
        font = st.sidebar.selectbox('Yazı Tipi', ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Hack', 'Source Code Pro', 'Ubuntu Mono', 'Menlo', 'Monaco'])
        font_size = st.sidebar.slider('Yazı Boyutu', 8, 32, 14)

        # Color scheme
        if theme != 'Custom':
            color_scheme_options = list(COLOR_MAPPINGS.keys())
            color_scheme = st.sidebar.selectbox('Renk Şeması', color_scheme_options, 
                                          index=color_scheme_options.index(st.session_state['selected_color_scheme']))
            if color_scheme != st.session_state['selected_color_scheme']:
                st.session_state['selected_color_scheme'] = color_scheme
        else:
            color_scheme = 'Custom'

        # Opacity
        custom_colors = {}
        opacity = st.sidebar.slider('Pencere Opaklığı', 0.5, 1.0, st.session_state['opacity'])
        if opacity != st.session_state['opacity']:
            st.session_state['opacity'] = opacity
            
        # Custom colors
        if theme == 'Custom':
            st.sidebar.markdown("## Özel Renk Ayarları")
            custom_colors = st.session_state['custom_colors']
            bg = st.sidebar.color_picker('Arka Plan Rengi', custom_colors['bg'])
            fg = st.sidebar.color_picker('Yazı Rengi', custom_colors['fg'])
            prompt = st.sidebar.color_picker('Prompt Rengi', custom_colors['prompt'])
            
            if (bg, fg, prompt) != (custom_colors['bg'], custom_colors['fg'], custom_colors['prompt']):
                st.session_state['custom_colors'] = {'bg': bg, 'fg': fg, 'prompt': prompt}

        # Terminal options
        st.sidebar.markdown("## Terminal Seçenekleri")
        enable_tab_bar = st.sidebar.checkbox('Sekme Çubuğunu Etkinleştir', value=True)
        enable_scroll_bar = st.sidebar.checkbox('Kaydırma Çubuğunu Etkinleştir', value=False)
        cursor_style = st.sidebar.selectbox('İmleç Stili', ['Block', 'Bar', 'Underline'], index=0)

        # Advanced options
        with st.sidebar.expander("Gelişmiş Seçenekler"):
            padding = st.sidebar.slider('Dolgu', 0, 20, 8)
            line_height = st.sidebar.slider('Satır Yüksekliği', 0.8, 2.0, 1.0, 0.1)
            use_fancy_tab_bar = st.sidebar.checkbox('Süslü Sekme Çubuğunu Kullan', value=True)
            hyperlinkRules = st.sidebar.multiselect('Bağlantı Kuralları', 
                                      ['URL Algılama', 'Dosya Yolları', 'E-posta Adresleri'],
                                      ['URL Algılama'])
            leader_key = st.sidebar.text_input('Lider Tuşu', 'CTRL + a')
            
            if leader_key and '+' not in leader_key:
                st.sidebar.warning("Lider tuşu formatı 'MOD + TUŞ' şeklinde olmalıdır, örneğin 'CTRL + a'")
        
        # Return complete configuration
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

    def run(self):
        """Run the WezTerm Configurator app"""
        st.title('WezTerm Yapılandırıcı')
        st.write('Sol menüden seçimlerinizi yapın ve terminal önizlemesini görün!')
        
        # Create placeholder for terminal preview
        terminal_placeholder = st.empty()
        
        # Get configuration from sidebar
        config = self.render_sidebar()
        
        # Determine if terminal needs a full refresh
        has_config_changed = config_has_changed(config, st.session_state.current_config)
        
        # Terminal preview section
        st.subheader("Terminal Önizleme")
        
        try:
            # Either create a new terminal or update the existing one
            if has_config_changed or 'terminal_html' not in st.session_state:
                # Generate full terminal HTML
                colors = st.session_state['custom_colors'] if config['theme'] == 'Custom' else None
                terminal_html = TerminalPreviewGenerator.generate_dynamic_terminal_preview(
                    config['theme'], config['font'], config['font_size'], config['color_scheme'], 
                    colors, config['opacity'], config['enable_tab_bar'], config['enable_scroll_bar'], 
                    config['cursor_style'], config['padding'], config['line_height'], 
                    config['use_fancy_tab_bar'], config['hyperlinkRules'], config['leader_key']
                )
                
                # Save and display
                st.session_state.terminal_html = terminal_html
                st.session_state.terminal_key += 1
                with terminal_placeholder:
                    components.html(terminal_html, height=450, scrolling=False)
            else:
                # Update existing terminal via JS
                theme_colors = get_colors_for_theme(
                    config['theme'], 
                    config['color_scheme'], 
                    config['custom_colors']
                )
                update_terminal_js(config, theme_colors)
                with terminal_placeholder:
                    components.html(st.session_state.terminal_html, height=450, scrolling=False)
            
            # Save current state
            st.session_state.current_config = config.copy()
            
            # Show help text
            st.caption("💡 **İpucu:** Terminal'e tıklayarak komut girebilirsiniz. Yukarı/aşağı ok tuşları ile komut geçmişini gezebilirsiniz.")
            st.caption("📋 **Kullanılabilir Komutlar:** `clear`, `ls`, `pwd`, `date`, `echo`, `help`, `wezterm`, `config`, `whoami`,`uname`, `screenfetch`")
            
        except Exception as e:
            logger.error(f"Terminal önizleme hatası: {e}\n{traceback.format_exc()}")
            st.error(f"Terminal önizleme hatası: {e}")
        
        # Lua configuration and settings
        st.subheader("Yapılandırma Kodu ve Ayarlar")
        code_col, settings_col = st.columns([2, 1])
        
        # Configuration code column
        with code_col:
            lua_code = ConfigGenerator.generate_wezterm_lua(config)
            
            if lua_code:
                st.code(lua_code, language='lua')
                st.download_button("wezterm.lua İndir", lua_code, file_name="wezterm.lua")
                st.info("""
                **Bu yapılandırmayı kullanmak için:**
                1. "wezterm.lua İndir" düğmesini kullanarak dosyayı indirin
                2. `~/.config/wezterm/wezterm.lua` (Linux/macOS) veya `%USERPROFILE%\\.wezterm.lua` (Windows) konumuna kaydedin
                3. WezTerm'i yeniden başlatın
                """)
            else:
                st.error("Yapılandırma kodu oluşturulamadı. Lütfen ayarlarınızı kontrol edin.")
        
        # Settings column
        with settings_col:
            st.markdown("### Aktif Ayarlar")
            
            # Get colors for settings display
            display_colors = st.session_state['custom_colors'] if config['theme'] == 'Custom' else get_colors_for_theme(config['theme'], config['color_scheme'])
            
            # Generate and display settings table
            settings_html = TerminalPreviewGenerator.generate_settings_table(
                config['theme'], config['color_scheme'], config['font'], config['font_size'], 
                config['opacity'], config['padding'], config['line_height'], 
                config['cursor_style'], config['enable_tab_bar'], config['use_fancy_tab_bar'], 
                config['enable_scroll_bar'], config['hyperlinkRules'], config['leader_key'], 
                display_colors
            )
            
            components.html(settings_html, height=600, scrolling=True)


if __name__ == "__main__":
    app = WezTermConfigurator()
    app.run()

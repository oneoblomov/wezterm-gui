import streamlit as st
import os
import streamlit.components.v1 as components
import logging
import traceback
import tempfile

from src.terminal import TerminalPreviewGenerator
from src.config import ConfigGenerator
from src.themes import COLOR_MAPPINGS, THEME_COLOR_SCHEME_MAPPING, get_colors_for_theme
from src.utils import load_css, config_has_changed, update_terminal_js

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
        
        if 'terminal_key' not in st.session_state:
            st.session_state.terminal_key = 0
            
        if 'current_config' not in st.session_state:
            st.session_state.current_config = self.get_default_config()

    def get_default_config(self):
        """Varsayılan yapılandırma değerlerini döndür"""
        return {
            'theme': 'Dark',
            'font': 'JetBrains Mono',
            'font_size': 14,
            'color_scheme': 'Builtin Dark',
            'custom_colors': {'bg': '#282828', 'fg': '#ebdbb2', 'prompt': '#b8bb26'},
            'opacity': 0.95,
            'enable_tab_bar': True,
            'enable_scroll_bar': False,
            'default_cursor_style': 'Block',
            'padding': 8,
            'line_height': 1.0,
            'use_fancy_tab_bar': True,
            'hyperlinkRules': ['URL Algılama'],
            'leader_key': 'CTRL + a',
            'window_width': 800,
            'window_height': 600,
            'window_decorations': ['TITLE', 'RESIZE'],
            'window_position': None,
            'window_maximized': False,
            'window_fullscreen': False,
            'window_always_on_top': False,
            'window_close_confirmation': 'AlwaysPrompt',
            'window_hide_tab_bar_if_only_one_tab': True
        }

    def initialize_session_state(self):
        """Session state değişkenlerini başlat"""
        defaults = self.get_default_config()
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        if 'selected_color_scheme' not in st.session_state:
            st.session_state['selected_color_scheme'] = 'Builtin Dark'

    def render_theme_settings(self):
        """Tema ayarları bölümünü render et"""
        st.sidebar.markdown("## Tema Ayarları")
        
        # Theme selection
        theme = st.sidebar.selectbox('Tema', 
                                   ['Dark', 'Light', 'Custom'],
                                   index=['Dark', 'Light', 'Custom'].index(st.session_state['theme']))
        
        if theme != st.session_state['theme']:
            st.session_state['theme'] = theme
            if theme != 'Custom':
                st.session_state['selected_color_scheme'] = THEME_COLOR_SCHEME_MAPPING[theme]

        # Font settings
        font = st.sidebar.selectbox('Yazı Tipi', 
                                  ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Hack', 
                                   'Source Code Pro', 'Ubuntu Mono', 'Menlo', 'Monaco'])
        
        font_size = st.sidebar.slider('Yazı Boyutu', 8, 32, 14)

        # Color scheme
        if theme != 'Custom':
            color_scheme_options = list(COLOR_MAPPINGS.keys())
            color_scheme = st.sidebar.selectbox('Renk Şeması', 
                                          color_scheme_options, 
                                          index=color_scheme_options.index(st.session_state['selected_color_scheme']))
            
            if color_scheme != st.session_state['selected_color_scheme']:
                st.session_state['selected_color_scheme'] = color_scheme
        else:
            color_scheme = 'Custom'

        # Opacity
        opacity = st.sidebar.slider('Pencere Opaklığı', 0.5, 1.0, st.session_state['opacity'])
        if opacity != st.session_state['opacity']:
            st.session_state['opacity'] = opacity
        
        # Custom colors
        custom_colors = {}
        if theme == 'Custom':
            st.sidebar.markdown("## Özel Renk Ayarları")
            custom_colors = st.session_state['custom_colors']
            bg = st.sidebar.color_picker('Arka Plan Rengi', custom_colors['bg'])
            fg = st.sidebar.color_picker('Yazı Rengi', custom_colors['fg'])
            prompt = st.sidebar.color_picker('Prompt Rengi', custom_colors['prompt'])
            
            if (bg, fg, prompt) != (custom_colors['bg'], custom_colors['fg'], custom_colors['prompt']):
                st.session_state['custom_colors'] = {'bg': bg, 'fg': fg, 'prompt': prompt}
                custom_colors = {'bg': bg, 'fg': fg, 'prompt': prompt}
        
        return {
            'theme': theme,
            'font': font,
            'font_size': font_size,
            'color_scheme': color_scheme,
            'custom_colors': custom_colors,
            'opacity': opacity
        }

    def render_terminal_options(self):
        """Terminal seçenekleri bölümünü render et"""
        st.sidebar.markdown("## Terminal Seçenekleri")
        
        enable_tab_bar = st.sidebar.checkbox('Sekme Çubuğunu Etkinleştir', value=True)
        enable_scroll_bar = st.sidebar.checkbox('Kaydırma Çubuğunu Etkinleştir', value=False)
        default_cursor_style = st.sidebar.selectbox('İmleç Stili', ['Block', 'Bar', 'Underline'], index=0)

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
        
        return {
            'enable_tab_bar': enable_tab_bar,
            'enable_scroll_bar': enable_scroll_bar,
            'default_cursor_style': default_cursor_style,
            'padding': padding,
            'line_height': line_height,
            'use_fancy_tab_bar': use_fancy_tab_bar,
            'hyperlinkRules': hyperlinkRules,
            'leader_key': leader_key
        }

    def render_window_options(self):
        """Pencere özellikleri bölümünü render et"""
        st.sidebar.markdown("## Pencere Özellikleri")
        
        # Window dimensions
        window_width = st.sidebar.number_input('Pencere Genişliği (pixel)', 
                                         min_value=400, max_value=3840, 
                                         value=st.session_state.get('window_width', 800),
                                         step=50)
        
        window_height = st.sidebar.number_input('Pencere Yüksekliği (pixel)', 
                                          min_value=300, max_value=2160, 
                                          value=st.session_state.get('window_height', 600),
                                          step=50)
        
        # Window decorations
        window_decorations = st.sidebar.multiselect('Pencere Dekorasyonları',
                                              ['TITLE', 'RESIZE', 'MACOS_FORCE_ENABLE_SHADOW', 'INTEGRATED_BUTTONS'],
                                              default=st.session_state.get('window_decorations', ['TITLE', 'RESIZE']))
        
        # Window position
        window_position_enabled = st.sidebar.checkbox('Başlangıç Pozisyonu Belirle',
                                                value=st.session_state.get('window_position') is not None)
        window_position = None
        if window_position_enabled:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                pos_x = st.number_input('X Pozisyonu', value=0, step=10)
            with col2:
                pos_y = st.number_input('Y Pozisyonu', value=0, step=10)
            window_position = [pos_x, pos_y]
        
        # Window state options
        window_maximized = st.sidebar.checkbox('Pencere Başlangıçta Maksimize',
                                         value=st.session_state.get('window_maximized', False))
        
        window_fullscreen = st.sidebar.checkbox('Pencere Başlangıçta Tam Ekran',
                                          value=st.session_state.get('window_fullscreen', False))
        
        window_always_on_top = st.sidebar.checkbox('Her Zaman Üstte',
                                             value=st.session_state.get('window_always_on_top', False))
        
        # Window behavior
        window_close_confirmation = st.sidebar.selectbox('Kapatma Onayı',
                                                   ['Never', 'AlwaysPrompt', 'OnlyIfMultipleTabs'],
                                                   index=['Never', 'AlwaysPrompt', 'OnlyIfMultipleTabs'].index(
                                                       st.session_state.get('window_close_confirmation', 'AlwaysPrompt')
                                                   ))
        
        window_hide_tab_bar_if_only_one_tab = st.sidebar.checkbox('Tek Sekme Varsa Sekme Çubuğunu Gizle',
                                                            value=st.session_state.get('window_hide_tab_bar_if_only_one_tab', True))
        
        # Update session state
        self.update_window_session_state({
            'window_width': window_width,
            'window_height': window_height,
            'window_decorations': window_decorations,
            'window_position': window_position,
            'window_maximized': window_maximized,
            'window_fullscreen': window_fullscreen,
            'window_always_on_top': window_always_on_top,
            'window_close_confirmation': window_close_confirmation,
            'window_hide_tab_bar_if_only_one_tab': window_hide_tab_bar_if_only_one_tab
        })
        
        return {
            'window_width': window_width,
            'window_height': window_height,
            'window_decorations': window_decorations,
            'window_position': window_position,
            'window_maximized': window_maximized,
            'window_fullscreen': window_fullscreen,
            'window_always_on_top': window_always_on_top,
            'window_close_confirmation': window_close_confirmation,
            'window_hide_tab_bar_if_only_one_tab': window_hide_tab_bar_if_only_one_tab
        }
        
    def update_window_session_state(self, window_config):
        """Pencere ile ilgili session state değişkenlerini güncelle"""
        for key, value in window_config.items():
            st.session_state[key] = value

    def render_sidebar(self):
        """Sidebar'ı render et ve konfigürasyon sözlüğünü döndür"""
        # Her bir kategori için ayarları al
        theme_config = self.render_theme_settings()
        terminal_config = self.render_terminal_options()
        window_config = self.render_window_options()
        
        # Tüm ayarları birleştir
        config = {}
        config.update(theme_config)
        config.update(terminal_config)
        config.update(window_config)
        
        return config

    def run(self):
        """Run the WezTerm Configurator app"""
        st.title('WezTerm Yapılandırıcı')
        st.write('Sol menüden seçimlerinizi yapın ve terminal önizlemesini görün!')
        
        terminal_placeholder = st.empty()
        
        config = self.render_sidebar()
        
        has_config_changed = config_has_changed(config, st.session_state.current_config)
        
        self.render_terminal_preview(terminal_placeholder, config, has_config_changed)
        self.render_configuration_code(config)
        
    def render_terminal_preview(self, placeholder, config, has_config_changed):
        """Terminal önizlemesini render et"""
        st.subheader("Terminal Önizleme")
        
        try:
            if has_config_changed or 'terminal_html' not in st.session_state:
                colors = st.session_state['custom_colors'] if config['theme'] == 'Custom' else None
                terminal_html = TerminalPreviewGenerator.generate_dynamic_terminal_preview(
                    config['theme'], config['font'], config['font_size'], config['color_scheme'], 
                    colors, config['opacity'], config['enable_tab_bar'], config['enable_scroll_bar'], 
                    config['default_cursor_style'], config['padding'], config['line_height'], 
                    config['use_fancy_tab_bar'], config['hyperlinkRules'], config['leader_key']
                )
                
                st.session_state.terminal_html = terminal_html
                st.session_state.terminal_key += 1
                with placeholder:
                    components.html(terminal_html, height=450, scrolling=False)
            else:
                theme_colors = get_colors_for_theme(
                    config['theme'], 
                    config['color_scheme'], 
                    config['custom_colors']
                )
                update_terminal_js(config, theme_colors)
                with placeholder:
                    components.html(st.session_state.terminal_html, height=450, scrolling=False)
            
            st.session_state.current_config = config.copy()
            
            st.caption("💡 **İpucu:** Terminal'e tıklayarak komut girebilirsiniz. Yukarı/aşağı ok tuşları ile komut geçmişini gezebilirsiniz.")
            st.caption("📋 **Kullanılabilir Komutlar:** `clear`, `ls`, `pwd`, `date`, `echo`, `help`, `wezterm`, `config`, `whoami`,`uname`, `screenfetch`")
            
        except Exception as e:
            logger.error(f"Terminal önizleme hatası: {e}\n{traceback.format_exc()}")
            st.error(f"Terminal önizleme hatası: {e}")
    
    def render_configuration_code(self, config):
        """Yapılandırma kodu ve ayarlar bölümünü render et"""
        st.subheader("Yapılandırma Kodu ve Ayarlar")
        code_col, settings_col = st.columns([2, 1])
        
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
        
        with settings_col:
            self.render_settings_summary(config, settings_col)
    
    def render_settings_summary(self, config, container):
        """Ayarlar özeti bölümünü render et"""
        container.markdown("### Aktif Ayarlar")
        
        display_colors = st.session_state['custom_colors'] if config['theme'] == 'Custom' else get_colors_for_theme(config['theme'], config['color_scheme'])
        
        window_props = {
            'window_width': config.get('window_width'),
            'window_height': config.get('window_height'),
            'window_decorations': config.get('window_decorations'),
            'window_position': config.get('window_position'),
            'window_maximized': config.get('window_maximized'),
            'window_fullscreen': config.get('window_fullscreen'),
            'window_always_on_top': config.get('window_always_on_top'),
            'window_close_confirmation': config.get('window_close_confirmation'),
            'window_hide_tab_bar_if_only_one_tab': config.get('window_hide_tab_bar_if_only_one_tab')
        }
        
        settings_html = TerminalPreviewGenerator.generate_settings_table(
            config['theme'], config['color_scheme'], config['font'], config['font_size'], 
            config['opacity'], config['padding'], config['line_height'], 
            config['default_cursor_style'], config['enable_tab_bar'], config['use_fancy_tab_bar'], 
            config['enable_scroll_bar'], config['hyperlinkRules'], config['leader_key'], 
            display_colors, **window_props
        )
        
        components.html(settings_html, height=600, scrolling=True)


if __name__ == "__main__":
    app = WezTermConfigurator()
    app.run()

import logging
import traceback

logger = logging.getLogger("wezterm_gui")

class ConfigGenerator:
    """WezTerm yapılandırma dosyası üreten sınıf"""

    @staticmethod
    def generate_wezterm_lua(config):
        """Generate WezTerm Lua configuration based on user selections"""
        try:
            default_cursor_style_map = {'Block': 'SteadyBlock', 'Bar': 'SteadyBar', 'Underline': 'SteadyUnderline'}
            wezterm_default_cursor_style = default_cursor_style_map.get(config['default_cursor_style'], 'SteadyBlock')
            
            lua_config = [
                "local wezterm = require 'wezterm'",
                "local act = wezterm.action",
                "",
                "-- This is where you actually apply your config choices",
                "local config = wezterm.config_builder()",
                "",
                "-- Basic configuration",
                f"config.font = wezterm.font('{config['font']}')",
                f"config.font_size = {config['font_size']}",
                f"config.line_height = {config['line_height']}",
                "",
                f"config.enable_tab_bar = {str(config['enable_tab_bar']).lower()}",
                f"config.use_fancy_tab_bar = {str(config['use_fancy_tab_bar']).lower()}",
                f"config.enable_scroll_bar = {str(config['enable_scroll_bar']).lower()}",
                f"config.window_background_opacity = {config['opacity']}",
                f"config.default_cursor_style = '{wezterm_default_cursor_style}'",
                "config.window_padding = {",
                f"  left = {config['padding']}, right = {config['padding']},",
                f"  top = {config['padding']}, bottom = {config['padding']}",
                "}",
                ""
            ]

            lua_config.extend([
                "-- Window dimensions and position",
                f"config.initial_cols = {config['window_width'] // 8}  -- Approximate conversion from pixels to columns",
                f"config.initial_rows = {config['window_height'] // 16}  -- Approximate conversion from pixels to rows",
                ""
            ])
            
            if config.get('window_decorations'):
                decorations_code = []
                for decoration in config['window_decorations']:
                    decorations_code.append(f"wezterm.window_decoration.{decoration}")
                
                if decorations_code:
                    lua_config.append(f"config.window_decorations = {' | '.join(decorations_code)}")
                    lua_config.append("")
            
            if config.get('window_position'):
                lua_config.append(f"config.initial_position = {{ x = {config['window_position'][0]}, y = {config['window_position'][1]} }}")
                lua_config.append("")
            
            if config.get('window_maximized'):
                lua_config.append(f"config.default_gui_startup_args = {{ 'start', '--maximized' }}")
            elif config.get('window_fullscreen'):
                lua_config.append(f"config.default_gui_startup_args = {{ 'start', '--fullscreen' }}")
                
            lua_config.append(f"config.window_close_confirmation = '{config.get('window_close_confirmation', 'AlwaysPrompt')}'")
            lua_config.append(f"config.hide_tab_bar_if_only_one_tab = {str(config.get('window_hide_tab_bar_if_only_one_tab', True)).lower()}")
            lua_config.append(f"config.window_is_always_on_top = {str(config.get('window_always_on_top', False)).lower()}")
            lua_config.append("")

            if config['hyperlinkRules'] and len(config['hyperlinkRules']) > 0:
                lua_config.extend(ConfigGenerator._generate_hyperlink_rules(config['hyperlinkRules']))

            if config['leader_key'] and config['leader_key'].strip():
                lua_config.extend(ConfigGenerator._generate_leader_key_config(config['leader_key']))

            if config['theme'] == 'Custom' and config['custom_colors']:
                lua_config.extend([
                    "-- Custom colors",
                    "config.colors = {",
                    f"  background = '{config['custom_colors']['bg']}',",
                    f"  foreground = '{config['custom_colors']['fg']}',",
                    f"  cursor_bg = '{config['custom_colors']['prompt']}',",
                    "  cursor_fg = 'black',",
                    "}",
                    ""
                ])
            else:
                lua_config.extend([
                    "-- Theme color scheme",
                    f"config.color_scheme = '{config['color_scheme']}'",
                    ""
                ])
            
            lua_config.append("return config")
            return "\n".join(lua_config)
        except Exception as e:
            logger.error(f"Lua yapılandırması oluşturulurken hata: {e}\n{traceback.format_exc()}")
            return None

    @staticmethod
    def _generate_hyperlink_rules(hyperlinkRules):
        """Generate hyperlink rule configuration"""
        config_lines = ["-- Hyperlink settings", "config.hyperlink_rules = {"]
        
        if 'URL Algılama' in hyperlinkRules:
            config_lines.extend([
                "  -- URL detection",
                "  {",
                "    regex = '\\\\b\\\\w+://[\\\\w.-]+\\\\.[\\\\w.-]+\\\\S*\\\\b',",
                "    format = '$0',",
                "  },"
            ])
        
        if 'E-posta Adresleri' in hyperlinkRules:
            config_lines.extend([
                "  -- Email addresses",
                "  {",
                "    regex = '\\\\b\\\\w+@[\\\\w.-]+\\\\.[\\\\w]+\\\\b',",
                "    format = 'mailto:$0',",
                "  },"
            ])
                
        if 'Dosya Yolları' in hyperlinkRules:
            config_lines.extend([
                "  -- File paths",
                "  {",
                "    regex = '\\\\b(\\\\w+:)?[\\\\/\\\\\\\\][\\\\w.~-]+[\\\\/\\\\\\\\][\\\\w.~-]+\\\\b',",
                "    format = '$0',",
                "  },"
            ])
                
        config_lines.append("}")
        config_lines.append("")
        return config_lines

    @staticmethod
    def _generate_leader_key_config(leader_key):
        """Generate leader key configuration"""
        parts = [part.strip() for part in leader_key.split('+')]
        if len(parts) >= 2:
            key, mods = parts[-1].lower(), '+'.join(part.upper() for part in parts[:-1])
        else:
            key, mods = leader_key.strip().lower(), 'CTRL'

        return [
            "-- Leader key configuration",
            f"config.leader = {{ key = '{key}', mods = '{mods}', timeout_milliseconds = 1000 }}",
            ""
        ]

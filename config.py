import logging
import traceback

logger = logging.getLogger("wezterm_gui")

class ConfigGenerator:
    """WezTerm yapılandırma dosyası üreten sınıf"""

    @staticmethod
    def generate_wezterm_lua(config):
        """Generate WezTerm Lua configuration based on user selections"""
        try:
            cursor_style_map = {'Block': 'SteadyBlock', 'Bar': 'SteadyBar', 'Underline': 'SteadyUnderline'}
            wezterm_cursor_style = cursor_style_map.get(config['cursor_style'], 'SteadyBlock')
            
            # Base configuration
            lua_config = [
                "local wezterm = require 'wezterm'",
                "local act = wezterm.action",
                "",
                "return {",
                f"  font = wezterm.font('{config['font']}'),",
                f"  font_size = {config['font_size']},",
                f"  line_height = {config['line_height']},",
                "",
                f"  enable_tab_bar = {str(config['enable_tab_bar']).lower()},",
                f"  use_fancy_tab_bar = {str(config['use_fancy_tab_bar']).lower()},",
                f"  enable_scroll_bar = {str(config['enable_scroll_bar']).lower()},",
                f"  window_background_opacity = {config['opacity']},",
                f"  cursor_style = '{wezterm_cursor_style}',",
                "  window_padding = {",
                f"    left = {config['padding']}, right = {config['padding']},",
                f"    top = {config['padding']}, bottom = {config['padding']},",
                "  },"
            ]

            # Add hyperlink rules if selected
            if config['hyperlinkRules'] and len(config['hyperlinkRules']) > 0:
                lua_config.extend(ConfigGenerator._generate_hyperlink_rules(config['hyperlinkRules']))

            # Add leader key if provided
            if config['leader_key'] and config['leader_key'].strip():
                lua_config.extend(ConfigGenerator._generate_leader_key_config(config['leader_key']))

            # Add color configuration
            if config['theme'] == 'Custom' and config['custom_colors']:
                lua_config.extend([
                    "  -- Custom colors",
                    "  colors = {",
                    f"    background = '{config['custom_colors']['bg']}',",
                    f"    foreground = '{config['custom_colors']['fg']}',",
                    f"    cursor_bg = '{config['custom_colors']['prompt']}',",
                    "    cursor_fg = 'black',",
                    "  },",
                ])
            else:
                lua_config.extend([
                    "  -- Theme color scheme",
                    f"  color_scheme = '{config['color_scheme']}',",
                ])
            
            lua_config.append("}")
            return "\n".join(lua_config)
        except Exception as e:
            logger.error(f"Lua yapılandırması oluşturulurken hata: {e}\n{traceback.format_exc()}")
            return None

    @staticmethod
    def _generate_hyperlink_rules(hyperlinkRules):
        """Generate hyperlink rule configuration"""
        config_lines = ["  -- Hyperlink settings", "  hyperlink_rules = {"]
        
        if 'URL Algılama' in hyperlinkRules:
            config_lines.extend([
                "    -- URL detection",
                "    {",
                "      regex = '\\\\b\\\\w+://[\\\\w.-]+\\\\.[\\\\w.-]+\\\\S*\\\\b',",
                "      format = '$0',",
                "    },"
            ])
        
        if 'E-posta Adresleri' in hyperlinkRules:
            config_lines.extend([
                "    -- Email addresses",
                "    {",
                "      regex = '\\\\b\\\\w+@[\\\\w.-]+\\\\.[\\\\w]+\\\\b',",
                "      format = 'mailto:$0',",
                "    },"
            ])
                
        if 'Dosya Yolları' in hyperlinkRules:
            config_lines.extend([
                "    -- File paths",
                "    {",
                "      regex = '\\\\b(\\\\w+:)?[\\\\/\\\\\\\\][\\\\w.~-]+[\\\\/\\\\\\\\][\\\\w.~-]+\\\\b',",
                "      format = '$0',",
                "    },"
            ])
                
        config_lines.append("  },")
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
            "  -- Leader key configuration",
            f"  leader = {{ key = '{key}', mods = '{mods}', timeout_milliseconds = 1000 }},"
        ]

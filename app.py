import streamlit as st
import json
import os
import streamlit.components.v1 as components
import platform
from pathlib import Path
import logging
import traceback
import tempfile

# Log ayarları
log_file = os.path.join(tempfile.gettempdir(), "wezterm_gui.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
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
        tab_bar_bg = colors['bg'] if not use_fancy_tab_bar else 'rgba(0,0,0,0.3)'
        active_tab_bg = colors['prompt'] if use_fancy_tab_bar else 'rgba(255,255,255,0.1)'
        inactive_tab_color = colors['fg'] if use_fancy_tab_bar else 'rgba(255,255,255,0.6)'
        tab_x = '<span style="font-size:10px;opacity:0.7;">✕</span>' if use_fancy_tab_bar else ''
        
        components['tab_bar'] = f"""<div style="background:{tab_bar_bg};color:{colors['fg']};border-bottom:1px solid rgba(255,255,255,0.2);padding:5px 0;display:flex;align-items:center;">
            <div style="display:flex;padding:0 10px;width:100%;">
                <div style="background:{active_tab_bg};color:{colors['fg']};border-radius:3px;padding:4px 12px;margin-right:5px;font-size:12px;display:flex;align-items:center;">
                    <span style="margin-right:8px;">bash</span>{tab_x}
                </div>
                <div style="color:{inactive_tab_color};padding:4px 12px;margin-right:5px;font-size:12px;display:flex;align-items:center;">
                    <span style="margin-right:8px;">zsh</span>{tab_x}
                </div>
                <div style="color:{inactive_tab_color};padding:4px 12px;font-size:12px;display:flex;align-items:center;">
                    <span style="margin-right:8px;">python</span>{tab_x}
                </div>
            </div>
            <div style="padding:0 10px;font-size:14px;cursor:pointer;">+</div>
        </div>""" if enable_tab_bar else ""
        
        # Cursor style
        cursor_styles = {
            'Block': f"display:inline-block;background:{colors['prompt']};color:black;animation:blink 1s step-end infinite;",
            'Bar': f"display:inline-block;border-left:2px solid {colors['prompt']};animation:blink 1s step-end infinite;",
            'Underline': f"display:inline-block;border-bottom:2px solid {colors['prompt']};animation:blink 1s step-end infinite;"
        }
        components['cursor'] = cursor_styles.get(cursor_style, cursor_styles['Block'])
        
        # Scrollbar component
        components['scrollbar'] = f"""<div style="width:10px;background:{colors['bg']};border-left:1px solid rgba(255,255,255,0.15);position:relative;">
            <div style="position:absolute;top:0;right:0;width:8px;height:30px;background:rgba(255,255,255,0.3);border-radius:4px;margin:2px;"></div>
        </div>""" if enable_scroll_bar else ""

        # Hyperlinks
        components['hyperlinks'] = ""
        if hyperlinkRules:
            components['hyperlinks'] = "<span style='color:#888;'># Hyperlink examples:</span><br>"
            if 'URL Algılama' in hyperlinkRules:
                components['hyperlinks'] += f"<span style='color:{colors['fg']};text-decoration:underline;cursor:pointer;'>https://example.com</span><br>"
            if 'Dosya Yolları' in hyperlinkRules:
                components['hyperlinks'] += f"<span style='color:{colors['fg']};text-decoration:underline;cursor:pointer;'>/home/user/file.txt</span><br>"
            if 'E-posta Adresleri' in hyperlinkRules:
                components['hyperlinks'] += f"<span style='color:{colors['fg']};text-decoration:underline;cursor:pointer;'>user@example.com</span><br>"
            components['hyperlinks'] += "<br>"

        # Leader key example
        components['leader_key'] = ""
        if leader_key:
            components['leader_key'] = f"<span style='color:#888;'># Leader key ({leader_key}) example:</span><br>"
            components['leader_key'] += f"<span style='color:{colors['fg']}'>Press {leader_key} followed by a key to activate shortcuts</span><br><br>"
        
        # Animation for cursor blinking
        components['animations'] = "<style>@keyframes blink{0%{opacity:1}50%{opacity:0}100%{opacity:1}}</style>"
        
        return components

    @staticmethod
    def generate_settings_table(theme, color_scheme, font, font_size, opacity, padding, 
                              line_height, cursor_style, enable_tab_bar, use_fancy_tab_bar, 
                              enable_scroll_bar, hyperlinkRules, leader_key, colors):
        """Generate HTML for settings table in preview"""
        ayarlar = [
            ('Tema', theme),
            ('Renk Şeması', color_scheme),
            ('Yazı Tipi', font),
            ('Yazı Boyutu', f"{font_size}px"),
            ('Opaklık', f"{opacity:.2f}"),
            ('İç Dolgu', f"{padding}px"),
            ('Satır Yüksekliği', line_height),
            ('İmleç Stili', cursor_style),
            ('Sekme Çubuğu', 'Etkin' if enable_tab_bar else 'Devre Dışı'),
            ('Kaydırma Çubuğu', 'Etkin' if enable_scroll_bar else 'Devre Dışı'),
            ('Bağlantı Kuralları', ', '.join(hyperlinkRules) if hyperlinkRules else 'Yok'),
            ('Lider Tuşu', leader_key if leader_key else 'Tanımlanmamış')
        ]
        
        rows = ''.join([
            f"<tr><td style='padding:6px;border-bottom:1px solid #eee;'>{name}</td>"
            f"<td style='padding:6px;border-bottom:1px solid #eee;'><code>{value}</code></td></tr>"
            for name, value in ayarlar
        ])
        
        renkler = ''.join([
            f"<div style='display:flex;align-items:center;margin-right:10px;'>"
            f"<div style='width:15px;height:15px;background:{colors[key]};border:1px solid #ccc;margin-right:5px;'></div>"
            f"{name}: <code>{colors[key]}</code></div>"
            for key, name in [('bg', 'Arka Plan'), ('fg', 'Yazı'), ('prompt', 'Prompt')]
        ])
        
        return f"""
        <div style="margin-top:15px;padding:15px;background:#f5f5f5;border-radius:6px;color:#333;box-shadow:0 2px 6px rgba(0,0,0,0.1);border:1px solid #e0e0e0;">
            <h4 style="margin:0 0 15px 0;border-bottom:1px solid #ddd;padding-bottom:8px;color:#444;">Aktif Yapılandırma Ayarları</h4>
            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <th style="text-align:left;width:33%;padding:6px;border-bottom:1px solid #ddd;">Ayar</th>
                    <th style="text-align:left;width:67%;padding:6px;border-bottom:1px solid #ddd;">Değer</th>
                </tr>
                {rows}
                <tr>
                    <td style="padding:6px;">Renk Değerleri</td>
                    <td style="padding:6px;display:flex;flex-wrap:wrap;">{renkler}</td>
                </tr>
            </table>
        </div>
        """

    @staticmethod
    def generate_dynamic_terminal_preview(theme, font, font_size, color_scheme, custom_colors=None, opacity=0.95,
                                   enable_tab_bar=True, enable_scroll_bar=False, cursor_style='Block',
                                   padding=8, line_height=1.0, use_fancy_tab_bar=True, hyperlinkRules=None,
                                   leader_key=None):
        """Generate dynamic interactive HTML terminal preview with JavaScript"""
        try:
            colors = WezTermConfigurator.get_colors_for_theme(theme, color_scheme, custom_colors)
            content_height = 350 - (30 if enable_tab_bar else 0)
            
            # Create tab bar component
            tab_bar_bg = colors['bg'] if not use_fancy_tab_bar else 'rgba(0,0,0,0.3)'
            active_tab_bg = colors['prompt'] if use_fancy_tab_bar else 'rgba(255,255,255,0.1)'
            inactive_tab_color = colors['fg'] if use_fancy_tab_bar else 'rgba(255,255,255,0.6)'
            tab_x = '<span style="font-size:10px;opacity:0.7;">✕</span>' if use_fancy_tab_bar else ''
            
            tab_bar = f"""<div style="background:{tab_bar_bg};color:{colors['fg']};border-bottom:1px solid rgba(255,255,255,0.2);padding:5px 0;display:flex;align-items:center;">
                <div style="display:flex;padding:0 10px;width:100%;">
                    <div style="background:{active_tab_bg};color:{colors['fg']};border-radius:3px;padding:4px 12px;margin-right:5px;font-size:12px;display:flex;align-items:center;">
                        <span style="margin-right:8px;">bash</span>{tab_x}
                    </div>
                    <div style="color:{inactive_tab_color};padding:4px 12px;margin-right:5px;font-size:12px;display:flex;align-items:center;">
                        <span style="margin-right:8px;">zsh</span>{tab_x}
                    </div>
                    <div style="color:{inactive_tab_color};padding:4px 12px;font-size:12px;display:flex;align-items:center;">
                        <span style="margin-right:8px;">python</span>{tab_x}
                    </div>
                </div>
                <div style="padding:0 10px;font-size:14px;cursor:pointer;">+</div>
            </div>""" if enable_tab_bar else ""
            
            # Cursor style
            cursor_styles = {
                'Block': f"background:{colors['prompt']};color:black;",
                'Bar': f"border-left:2px solid {colors['prompt']};",
                'Underline': f"border-bottom:2px solid {colors['prompt']};"
            }
            cursor_style_css = cursor_styles.get(cursor_style, cursor_styles['Block'])
            
            # Scrollbar component
            scrollbar = f"""<div style="width:10px;background:{colors['bg']};border-left:1px solid rgba(255,255,255,0.15);position:relative;">
                <div style="position:absolute;top:0;right:0;width:8px;height:30px;background:rgba(255,255,255,0.3);border-radius:4px;margin:2px;"></div>
            </div>""" if enable_scroll_bar else ""
            
            # JavaScript interaktif terminal kodu - input sorununu giderme 
            js_code = f"""
            <script>
            // Terminal konfigürasyonu
            const termConfig = {{
                bg: "{colors['bg']}",
                fg: "{colors['fg']}",
                promptColor: "{colors['prompt']}",
                cursorStyle: "{cursor_style_css}",
                fontSize: {font_size},
                lineHeight: {line_height}
            }};
            
            // Terminal geçmişi
            let history = [
                "total 32",
                "drwxr-xr-x  5 user group  4096 May 20 14:32 .",
                "drwxr-xr-x 18 user group  4096 May 19 10:15 ..",
                "drwxr-xr-x  8 user group  4096 May 20 11:21 .git",
                "-rw-r--r--  1 user group   129 May 18 09:43 .gitignore",
                "-rw-r--r--  1 user group  1523 May 18 09:43 README.md", 
                "-rw-r--r--  1 user group   978 May 20 14:30 app.py",
                "drwxr-xr-x  2 user group  4096 May 18 09:43 assets"
            ];
            
            // Basit komut veritabanı
            const commands = {{
                "clear": () => {{ history = []; return ""; }},
                "ls": () => {{ return history.join("\\n"); }},
                "pwd": () => {{ return "/home/user/projects"; }},
                "date": () => {{ return new Date().toString(); }},
                "echo": (args) => {{ return args.join(" "); }},
                "help": () => {{ return "Kullanılabilir Komutlar: clear, ls, pwd, date, echo, help, wezterm"; }},
                "wezterm": () => {{ return "WezTerm 20XX.XX.X (abcdef12) - https://wezfurlong.org/wezterm/"; }}
            }};
            
            // Terminal başlatma ve işleme
            document.addEventListener("DOMContentLoaded", function() {{
                const terminal = document.getElementById("dynamic-terminal");
                const container = document.getElementById("terminal-container");
                
                // Yeni prompt oluşturma fonksiyonu
                function createPrompt() {{
                    const wrapper = document.createElement("div");
                    wrapper.className = "terminal-line";
                    
                    const promptSpan = document.createElement("span");
                    promptSpan.className = "prompt";
                    promptSpan.innerHTML = `<span style="color:${{termConfig.promptColor}};">user@machine</span><span style="color:${{termConfig.fg}};">:</span><span style="color:#5f87ff;">~/projects</span><span style="color:${{termConfig.promptColor}};">$</span> `;
                    
                    const inputSpan = document.createElement("span");
                    inputSpan.className = "input-area";
                    inputSpan.contentEditable = true;
                    
                    // Input focus ve cursor style
                    inputSpan.addEventListener("focus", function() {{
                        cursorElement.style.visibility = "visible";
                    }});
                    
                    inputSpan.addEventListener("blur", function() {{
                        cursorElement.style.visibility = "hidden";
                    }});
                    
                    // Clipboard paste handling
                    inputSpan.addEventListener("paste", function(e) {{
                        e.preventDefault();
                        const text = (e.clipboardData || window.clipboardData).getData("text");
                        document.execCommand("insertText", false, text);
                    }});
                    
                    // Key event listeners
                    inputSpan.addEventListener("keydown", function(e) {{
                        if (e.key === "Enter") {{
                            e.preventDefault();
                            executeCommand(this);
                        }} else if (e.key === "ArrowUp") {{
                            e.preventDefault();
                            if (commandHistoryIndex > 0) {{
                                commandHistoryIndex--;
                                this.textContent = commandHistory[commandHistoryIndex];
                                placeCaretAtEnd(this);
                            }}
                        }} else if (e.key === "ArrowDown") {{
                            e.preventDefault();
                            if (commandHistoryIndex < commandHistory.length - 1) {{
                                commandHistoryIndex++;
                                this.textContent = commandHistory[commandHistoryIndex];
                            }} else {{
                                commandHistoryIndex = commandHistory.length;
                                this.textContent = "";
                            }}
                            placeCaretAtEnd(this);
                        }}
                    }});
                    
                    // Cursor element
                    const cursorElement = document.createElement("span");
                    cursorElement.className = "cursor";
                    cursorElement.style = "{cursor_style_css}";
                    cursorElement.innerHTML = "&nbsp;";
                    
                    // Build prompt line
                    wrapper.appendChild(promptSpan);
                    wrapper.appendChild(inputSpan);
                    wrapper.appendChild(cursorElement);
                    
                    return wrapper;
                }}
                
                // Komut tarihçesi
                let commandHistory = [];
                let commandHistoryIndex = -1;
                
                // İlk prompt'u ekle
                container.appendChild(createPrompt());
                
                // Terminal konteynerine tıklandığında aktif input'a odaklan
                container.addEventListener("click", function() {{
                    const activeInput = container.querySelector(".terminal-line:last-child .input-area");
                    if (activeInput) {{
                        activeInput.focus();
                        placeCaretAtEnd(activeInput);
                    }}
                }});
                
                // İmleç animasyonu
                let cursorVisible = true;
                setInterval(() => {{
                    const cursors = container.querySelectorAll(".cursor");
                    cursorVisible = !cursorVisible;
                    
                    for (const cursor of cursors) {{
                        cursor.style.visibility = cursorVisible ? "visible" : "hidden";
                    }}
                }}, 500);
                
                // İmleci metnin sonuna konumla
                function placeCaretAtEnd(element) {{
                    const range = document.createRange();
                    const selection = window.getSelection();
                    range.selectNodeContents(element);
                    range.collapse(false);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }}
                
                // Komutu çalıştır
                function executeCommand(inputElement) {{
                    const command = inputElement.textContent.trim();
                    
                    // Komut satırını etiketle
                    const commandLine = inputElement.parentNode;
                    commandLine.innerHTML = `<span class="prompt"><span style="color:${{termConfig.promptColor}};">user@machine</span><span style="color:${{termConfig.fg}};">:</span><span style="color:#5f87ff;">~/projects</span><span style="color:${{termConfig.promptColor}};">$</span> </span>${{command}}`;
                    
                    // Komut tarihçesine ekle
                    if (command) {{
                        commandHistory.push(command);
                        commandHistoryIndex = commandHistory.length;
                        
                        // Komutu işle ve çıktıyı ekle
                        const output = processCommand(command);
                        if (output) {{
                            const outputElem = document.createElement("div");
                            outputElem.className = "command-output";
                            outputElem.textContent = output;
                            container.appendChild(outputElem);
                        }}
                    }}
                    
                    // Yeni bir prompt ekle
                    container.appendChild(createPrompt());
                    
                    // Yeni input'a odaklan
                    const newInput = container.querySelector(".terminal-line:last-child .input-area");
                    if (newInput) {{
                        newInput.focus();
                        placeCaretAtEnd(newInput);
                    }}
                    
                    // Aşağı kaydır
                    container.scrollTop = container.scrollHeight;
                }}
                
                // Komut işleme
                function processCommand(cmdString) {{
                    if (!cmdString) return "";
                    
                    // Komutu parse et
                    let [cmd, ...args] = cmdString.split(" ");
                    cmd = cmd.toLowerCase();
                    
                    // Komutu çalıştır
                    if (cmd in commands) {{
                        return commands[cmd](args);
                    }} else {{
                        return `bash: ${{cmd}}: command not found`;
                    }}
                }}
                
                // İlk input'a odaklan (başlangıçta)
                setTimeout(() => {{
                    const firstInput = container.querySelector(".input-area");
                    if (firstInput) {{
                        firstInput.focus();
                        placeCaretAtEnd(firstInput);
                    }}
                }}, 100);
            }});
            </script>
            """
            
            # Dinamik terminal HTML - CSS ve yapı güncellemesi
            terminal_html = f"""
            <style>
            @keyframes blink {{
              0% {{ opacity: 1; }}
              50% {{ opacity: 0; }}
              100% {{ opacity: 1; }}
            }}
            #terminal-container {{
                height: 100%;
                overflow: auto;
                font-family: '{font}', monospace;
                font-size: {font_size}px;
                line-height: {line_height};
            }}
            .terminal-line {{
                white-space: pre;
                padding: 0;
                margin: 0;
                display: flex;
                align-items: baseline;
            }}
            .terminal-line:last-child {{
                display: flex;
            }}
            .command-output {{
                white-space: pre;
                padding: 0;
                margin: 0;
            }}
            .cursor {{
                {cursor_style_css}
                display: inline-block;
                width: 8px;
                height: 16px;
                vertical-align: middle;
            }}
            .input-area {{
                background: transparent;
                border: none;
                outline: none;
                color: inherit;
                font-family: inherit;
                font-size: inherit;
                padding: 0;
                margin: 0;
                caret-color: transparent;
                min-width: 1px;
            }}
            </style>
            
            <div style="background:#2c2c2c;border-radius:6px;box-shadow:0 5px 15px rgba(0,0,0,0.4);overflow:hidden;width:100%;position:relative;margin-bottom:20px;">
                <!-- Window decorations - title bar -->
                <div style="display:flex;background:#21252b;padding:8px 15px;align-items:center;user-select:none;">
                    <div style="display:flex;gap:6px;">
                        <div style="height:12px;width:12px;background:#ff5f56;border-radius:50%;"></div>
                        <div style="height:12px;width:12px;background:#ffbd2e;border-radius:50%;"></div>
                        <div style="height:12px;width:12px;background:#27c93f;border-radius:50%;"></div>
                    </div>
                    <div style="flex-grow:1;text-align:center;color:#9da5b4;font-size:12px;">WezTerm - user@machine: ~/projects</div>
                </div>
                
                <!-- Tab bar -->
                {tab_bar}
                
                <!-- Terminal content area with scrollbar -->
                <div style="display:flex;height:{content_height}px;">
                    <div id="dynamic-terminal" style="flex-grow:1;background:{colors['bg']};color:{colors['fg']};padding:{padding}px;opacity:{opacity};">
                        <div id="terminal-container">
                            <!-- Terminal content will be added here by JavaScript -->
                        </div>
                    </div>
                    {scrollbar}
                </div>
            </div>
            {js_code}
            """
            
            # Ayarlar tablosunu ekle
            terminal_html += TerminalPreviewGenerator.generate_settings_table(
                theme, color_scheme, font, font_size, opacity, padding, line_height, 
                cursor_style, enable_tab_bar, use_fancy_tab_bar, enable_scroll_bar, 
                hyperlinkRules, leader_key, colors
            )
            
            return terminal_html
        except Exception as e:
            logger.error(f"Dinamik terminal önizlemesi oluşturulurken hata: {e}\n{traceback.format_exc()}")
            return f"<div style='color:red;padding:20px;background:#fff0f0;border-radius:5px;'>Dinamik terminal önizlemesi oluşturulamadı: {str(e)}</div>"


class ConfigGenerator:
    """WezTerm yapılandırma dosyası üreten sınıf"""

    @staticmethod
    def generate_wezterm_lua(theme, font, font_size, color_scheme, custom_colors=None, opacity=0.95,
                          enable_tab_bar=True, enable_scroll_bar=False, cursor_style='Block',
                          padding=8, line_height=1.0, use_fancy_tab_bar=True, hyperlinkRules=None,
                          leader_key=None):
        """Generate WezTerm Lua configuration based on user selections"""
        try:
            cursor_style_map = {'Block': 'SteadyBlock', 'Bar': 'SteadyBar', 'Underline': 'SteadyUnderline'}
            wezterm_cursor_style = cursor_style_map.get(cursor_style, 'SteadyBlock')
            
            lua_config = [
                "local wezterm = require 'wezterm'",
                "local act = wezterm.action",
                "",
                "return {",
                f"  font = wezterm.font('{font}'),",
                f"  font_size = {font_size},",
                f"  line_height = {line_height},",
                "",
                f"  enable_tab_bar = {str(enable_tab_bar).lower()},",
                f"  use_fancy_tab_bar = {str(use_fancy_tab_bar).lower()},",
                f"  enable_scroll_bar = {str(enable_scroll_bar).lower()},",
                f"  window_background_opacity = {opacity},",
                f"  cursor_style = '{wezterm_cursor_style}',",
                "  window_padding = {",
                f"    left = {padding}, right = {padding},",
                f"    top = {padding}, bottom = {padding},",
                "  },"
            ]

            # Add hyperlink rules if selected
            if hyperlinkRules and len(hyperlinkRules) > 0:
                lua_config.append("  -- Hyperlink settings")
                if 'URL Algılama' in hyperlinkRules:
                    lua_config.append("  hyperlink_rules = {")
                    lua_config.append("    -- URL detection")
                    lua_config.append("    {")
                    lua_config.append("      regex = '\\\\b\\\\w+://[\\\\w.-]+\\\\.[\\\\w.-]+\\\\S*\\\\b',")
                    lua_config.append("      format = '$0',")
                    lua_config.append("    },")
                
                if 'E-posta Adresleri' in hyperlinkRules:
                    lua_config.append("    -- Email addresses")
                    lua_config.append("    {")
                    lua_config.append("      regex = '\\\\b\\\\w+@[\\\\w.-]+\\\\.[\\\\w]+\\\\b',")
                    lua_config.append("      format = 'mailto:$0',")
                    lua_config.append("    },")
                    
                if 'Dosya Yolları' in hyperlinkRules:
                    lua_config.append("    -- File paths")
                    lua_config.append("    {")
                    lua_config.append("      regex = '\\\\b(\\\\w+:)?[\\\\/\\\\\\\\][\\\\w.~-]+[\\\\/\\\\\\\\][\\\\w.~-]+\\\\b',")
                    lua_config.append("      format = '$0',")
                    lua_config.append("    },")
                    
                lua_config.append("  },")

            # Add leader key if provided
            if leader_key and leader_key.strip():
                parts = [part.strip() for part in leader_key.split('+')]
                if len(parts) >= 2:
                    key, mods = parts[-1].lower(), '+'.join(part.upper() for part in parts[:-1])
                else:
                    key, mods = leader_key.strip().lower(), 'CTRL'

                lua_config.extend([
                    "  -- Leader key configuration",
                    f"  leader = {{ key = '{key}', mods = '{mods}', timeout_milliseconds = 1000 }},"
                ])

            # Add color configuration
            if theme == 'Custom' and custom_colors:
                lua_config.extend([
                    "  -- Custom colors",
                    "  colors = {",
                    f"    background = '{custom_colors['bg']}',",
                    f"    foreground = '{custom_colors['fg']}',",
                    f"    cursor_bg = '{custom_colors['prompt']}',",
                    "    cursor_fg = 'black',",
                    "  },",
                ])
            else:
                lua_config.extend([
                    "  -- Theme color scheme",
                    f"  color_scheme = '{color_scheme}',"
                ])
            
            lua_config.append("}")
            return "\n".join(lua_config)
        except Exception as e:
            logger.error(f"Lua yapılandırması oluşturulurken hata: {e}\n{traceback.format_exc()}")
            return None


class WezTermConfigurator:
    """WezTerm yapılandırıcı ana sınıfı"""
    
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
        defaults = {
            'theme': 'Dark',
            'custom_colors': {'bg': '#282828', 'fg': '#ebdbb2', 'prompt': '#b8bb26'},
            'opacity': 0.95,
            'selected_color_scheme': 'Builtin Dark'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def load_css(self):
        """Load custom CSS"""
        try:
            css_path = os.path.join(os.path.dirname(__file__), "assets/styles.css")
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"CSS dosyası yüklenirken hata: {e}\n{traceback.format_exc()}")
            st.warning("Arayüz stil ayarları yüklenemedi, varsayılan Streamlit stili kullanılıyor.")

    @staticmethod
    def get_colors_for_theme(theme, color_scheme, custom_colors=None):
        """Get color values based on theme and color scheme"""
        if theme == "Custom" and custom_colors:
            return custom_colors
        return WezTermConfigurator.color_mappings.get(color_scheme, WezTermConfigurator.color_mappings['Builtin Dark'])

    def import_color_scheme(self, file_content):
        """Import color scheme from JSON"""
        try:
            imported_colors = json.loads(file_content)
            
            if not all(key in imported_colors for key in ['bg', 'fg', 'prompt']):
                raise ValueError("Geçersiz renk şeması formatı. 'bg', 'fg' ve 'prompt' anahtarları olmalı.")
            
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
            if theme != 'Custom':
                st.session_state['selected_color_scheme'] = self.theme_color_scheme_mapping[theme]

        font = st.sidebar.selectbox('Yazı Tipi', ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Hack', 'Source Code Pro', 'Ubuntu Mono', 'Menlo', 'Monaco'])
        font_size = st.sidebar.slider('Yazı Boyutu', 8, 32, 14)

        if theme != 'Custom':
            color_scheme_options = list(self.color_mappings.keys())
            color_scheme = st.sidebar.selectbox('Renk Şeması', color_scheme_options, 
                                            index=color_scheme_options.index(st.session_state['selected_color_scheme']))
            if color_scheme != st.session_state['selected_color_scheme']:
                st.session_state['selected_color_scheme'] = color_scheme
        else:
            color_scheme = 'Custom'

        # Custom color settings
        custom_colors = {}
        opacity = st.sidebar.slider('Pencere Opaklığı', 0.5, 1.0, st.session_state['opacity'])
        if opacity != st.session_state['opacity']:
            st.session_state['opacity'] = opacity
            
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

        # Import/Export functionality
        self.render_import_export_sidebar()
        
        # Return configuration
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
            # Export color scheme
            if st.button("Mevcut Renk Şemasını Dışa Aktar"):
                try:
                    export_data = st.session_state['custom_colors'] if st.session_state['theme'] == 'Custom' else \
                                 self.color_mappings.get(st.session_state['selected_color_scheme'], {})
                    
                    export_json = json.dumps(export_data)
                    st.code(export_json)
                    
                    filename = f"{st.session_state['selected_color_scheme'] if st.session_state['theme'] != 'Custom' else 'custom'}_colors.json"
                    st.download_button("JSON İndir", export_json, file_name=filename, mime="application/json")
                except Exception as e:
                    logger.error(f"Renk şeması dışa aktarılırken hata: {e}\n{traceback.format_exc()}")
                    st.error(f"Renk şeması dışa aktarılamadı: {e}")
            
            # Import color scheme
            st.markdown("### Renk Şeması İçe Aktar")
            upload_file = st.file_uploader("JSON dosyası yükle", type=['json'])
            if upload_file is not None:
                if self.import_color_scheme(upload_file.getvalue().decode()):
                    st.success("Renk şeması başarıyla içe aktarıldı! Lütfen sayfayı yenileyin.")

    def render_config_section(self, config):
        """Render the configuration code section"""
        st.subheader("Yapılandırma Kodu")
        
        theme_config = config['theme'] == 'Custom'
        colors = config['custom_colors'] if theme_config else None
        
        lua_code = ConfigGenerator.generate_wezterm_lua(
            config['theme'], config['font'], config['font_size'], 
            config['color_scheme'], colors, config['opacity'],
            config['enable_tab_bar'], config['enable_scroll_bar'], config['cursor_style'],
            config['padding'], config['line_height'], config['use_fancy_tab_bar'], 
            config['hyperlinkRules'], config['leader_key']
        )
        
        if lua_code:
            st.code(lua_code, language='lua')
            st.download_button("wezterm.lua İndir", lua_code, file_name="wezterm.lua")
            st.info("""
            **Bu yapılandırmayı kullanmak için:**
            1. Yukarıdaki "wezterm.lua İndir" düğmesini kullanarak dosyayı indirin
            2. `~/.config/wezterm/wezterm.lua` (Linux/macOS) veya `%USERPROFILE%\\.wezterm.lua` (Windows) konumuna kaydedin
            3. Değişikliklerinizi görmek için WezTerm'i yeniden başlatın
            """)
        else:
            st.error("Yapılandırma kodu oluşturulamadı. Lütfen ayarlarınızı kontrol edin.")

    def render_preview_section(self, config):
        """Render the terminal preview section"""
        st.subheader("Terminal Önizleme")
        
        # Remove the static/dynamic radio option - always use dynamic preview
        try:
            colors = st.session_state['custom_colors'] if config['theme'] == 'Custom' else None
            
            # Generate interactive terminal preview
            terminal_preview = TerminalPreviewGenerator.generate_dynamic_terminal_preview(
                config['theme'], config['font'], config['font_size'], config['color_scheme'], 
                colors, config['opacity'],
                config['enable_tab_bar'], config['enable_scroll_bar'], config['cursor_style'],
                config['padding'], config['line_height'], config['use_fancy_tab_bar'], 
                config['hyperlinkRules'], config['leader_key']
            )
            
            if terminal_preview:
                components.html(terminal_preview, height=670, scrolling=False)
                st.caption("💡 **İpucu:** Terminal'e tıklayarak komut girebilirsiniz. Yukarı/aşağı ok tuşları ile komut geçmişini gezebilirsiniz.")
                st.caption("📋 **Kullanılabilir Komutlar:** `clear`, `ls`, `pwd`, `date`, `echo`, `help`, `wezterm`")
            else:
                st.error("Terminal önizlemesi oluşturulamadı.")
                
        except Exception as e:
            logger.error(f"Terminal önizleme gösterilirken hata: {e}\n{traceback.format_exc()}")
            st.error(f"Terminal önizleme gösterilirken hata: {e}")
            st.warning("Sorunu çözmek için sayfayı yenilemeyi deneyin.")

    def run(self):
        """Run the WezTerm Configurator app"""
        st.title('WezTerm Yapılandırıcı')
        st.write('Sol menüden seçimlerinizi yapın ve terminal önizlemesini görün!')
        
        config = self.render_sidebar()
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_config_section(config)
        
        with col2:
            self.render_preview_section(config)


if __name__ == "__main__":
    app = WezTermConfigurator()
    app.run()

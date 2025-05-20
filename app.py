import streamlit as st
import json
import os
import streamlit.components.v1 as components
import logging
import traceback
import tempfile

log_file = os.path.join(tempfile.gettempdir(), "wezterm_gui.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger("wezterm_gui")


class TerminalPreviewGenerator:
    """Terminal preview generator class"""
    
    @staticmethod
    def generate_settings_table(theme, color_scheme, font, font_size, opacity, padding, 
                              line_height, cursor_style, enable_tab_bar, use_fancy_tab_bar, 
                              enable_scroll_bar, hyperlinkRules, leader_key, colors):
        """Generate HTML for settings table in preview"""
        settings = [
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
            for name, value in settings
        ])
        
        color_items = ''.join([
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
                    <td style="padding:6px;display:flex;flex-wrap:wrap;">{color_items}</td>
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
            
            cursor_styles = {
                'Block': f"background:{colors['prompt']};color:black;",
                'Bar': f"border-left:2px solid {colors['prompt']};",
                'Underline': f"border-bottom:2px solid {colors['prompt']};"
            }
            cursor_style_css = cursor_styles.get(cursor_style, cursor_styles['Block'])
            
            tab_bar = ""
            if enable_tab_bar:
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
                </div>"""
            
            scrollbar = ""
            if enable_scroll_bar:
                scrollbar = f"""<div style="width:10px;background:{colors['bg']};border-left:1px solid rgba(255,255,255,0.15);position:relative;">
                    <div style="position:absolute;top:0;right:0;width:8px;height:30px;background:rgba(255,255,255,0.3);border-radius:4px;margin:2px;"></div>
                </div>"""
            
            js_code = f"""
            <script>
            // Terminal configuration object
            let termConfig = {{
                bg: "{colors['bg']}",
                fg: "{colors['fg']}",
                promptColor: "{colors['prompt']}",
                cursorStyle: "{cursor_style_css}",
                fontSize: {font_size},
                lineHeight: {line_height},
                font: "{font}",
                padding: {padding},
                opacity: {opacity},
                enableTabBar: {str(enable_tab_bar).lower()},
                enableScrollBar: {str(enable_scroll_bar).lower()}
            }};
            
            // Available commands
            const commands = {{
                "clear": () => {{ return ""; }},
                "ls": () => {{ return "total 32\\ndrwxr-xr-x  5 user group  4096 May 20 14:32 .\\ndrwxr-xr-x 18 user group  4096 May 19 10:15 ..\\ndrwxr-xr-x  8 user group  4096 May 20 11:21 .git\\n-rw-r--r--  1 user group   129 May 18 09:43 .gitignore\\n-rw-r--r--  1 user group  1523 May 18 09:43 README.md\\n-rw-r--r--  1 user group   978 May 20 14:30 app.py\\ndrwxr-xr-x  2 user group  4096 May 18 09:43 assets"; }},
                "pwd": () => {{ return "/home/user/projects"; }},
                "date": () => {{ return new Date().toString(); }},
                "echo": (args) => {{ return args.join(" "); }},
                "help": () => {{ return "Kullanılabilir Komutlar: clear, ls, pwd, date, echo, help, wezterm, config, whoami, uname, screenfetch"; }},
                "wezterm": () => {{ return "WezTerm 20XX.XX.X (abcdef12) - https://wezfurlong.org/wezterm/"; }},
                "config": () => {{ return JSON.stringify(termConfig, null, 2); }},
                "whoami": () => {{ return "user"; }},
                "uname": () => {{ return "Linux wezterm-sim 6.2.0-32-generic x86_64 GNU/Linux"; }},
                "screenfetch": () => {{
                    return `
<span style="color:#5fafff;">
             .-/+oossssoo+/-.                   OS: Linux
         \`:+ssssssssssssssssss+:\`             WezTerm 20XX.XX.X
       -+ssssssssssssssssssyyssss+-             
     .ossssssssssssssssssdMMMNysssso.       
    /ssssssssssshdmmNNmmyNMMMMhssssss/      
   +ssssssssshmydMMMMMMMNddddyssssssss+     
  /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/    
 .ssssssssdMMMNhsssssssssshNMMMdssssssss.   
 +sssshhhyNMMNyssssssssssssyNMMMysssssss+   
 ossyNMMMNyMMhsssssssssssssshmmmhssssssso   
 ossyNMMMNyMMhsssssssssssssshmmmhssssssso   
 +sssshhhyNMMNyssssssssssssyNMMMysssssss+   
 .ssssssssdMMMNhsssssssssshNMMMdssssssss.   
  /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/    
   +ssssssssshmydMMMMMMMNddddyssssssss+     
    /ssssssssssshdmmNNmmyNMMMMhssssss/      
     .ossssssssssssssssssdMMMNysssso.       
       -+ssssssssssssssssssyyssss+-         
         \`:+ssssssssssssssssss+:\`           
             .-/+oossssoo+/-.               
</span>`;
                }},
            }};
            
            document.addEventListener("DOMContentLoaded", function() {{
                const terminal = document.getElementById("dynamic-terminal");
                const container = document.getElementById("terminal-container");
                const tabBar = document.getElementById("terminal-tab-bar");
                const scrollbar = document.getElementById("terminal-scrollbar");
                
                let commandHistory = [];
                let commandHistoryIndex = -1;
                
                function updateTerminalStyling() {{
                    terminal.style.fontFamily = termConfig.font + ", monospace";
                    terminal.style.fontSize = termConfig.fontSize + "px";
                    terminal.style.lineHeight = termConfig.lineHeight;
                    terminal.style.backgroundColor = termConfig.bg;
                    terminal.style.color = termConfig.fg;
                    terminal.style.padding = termConfig.padding + "px";
                    terminal.style.opacity = termConfig.opacity;
                    
                    const cursors = document.querySelectorAll(".cursor");
                    cursors.forEach(cursor => {{
                        cursor.style.backgroundColor = termConfig.promptColor;
                        if (termConfig.cursorStyle.includes("border-left")) {{
                            cursor.style.backgroundColor = "transparent";
                            cursor.style.borderLeft = "2px solid " + termConfig.promptColor;
                        }} else if (termConfig.cursorStyle.includes("border-bottom")) {{
                            cursor.style.backgroundColor = "transparent";
                            cursor.style.borderBottom = "2px solid " + termConfig.promptColor;
                        }}
                    }});
                    
                    const prompts = document.querySelectorAll(".prompt");
                    prompts.forEach(prompt => {{
                        const spans = prompt.querySelectorAll("span");
                        if (spans.length >= 3) {{
                            spans[0].style.color = termConfig.promptColor; // user@machine
                            spans[1].style.color = termConfig.fg; // :
                            spans[3].style.color = termConfig.promptColor; // $
                        }}
                    }});
                    
                    if (tabBar) {{
                        tabBar.style.display = termConfig.enableTabBar ? "flex" : "none";
                    }}
                    
                    if (scrollbar) {{
                        scrollbar.style.display = termConfig.enableScrollBar ? "block" : "none";
                    }}
                    
                    const contentHeight = 350 - (termConfig.enableTabBar ? 30 : 0);
                    document.querySelector(".terminal-content-area").style.height = contentHeight + "px";
                }}

                function createPrompt() {{
                    const wrapper = document.createElement("div");
                    wrapper.className = "terminal-line";
                    
                    const promptSpan = document.createElement("span");
                    promptSpan.className = "prompt";
                    promptSpan.innerHTML = `<span style="color:${{termConfig.promptColor}};">user@machine</span><span style="color:${{termConfig.fg}};">:</span><span style="color:#5f87ff;">~/projects</span><span style="color:${{termConfig.promptColor}};">$</span> `;
                    
                    const inputSpan = document.createElement("span");
                    inputSpan.className = "input-area";
                    inputSpan.contentEditable = true;
                    
                    const cursorElement = document.createElement("span");
                    cursorElement.className = "cursor";
                    cursorElement.style = termConfig.cursorStyle;
                    cursorElement.innerHTML = "&nbsp;";
                    
                    inputSpan.addEventListener("focus", () => cursorElement.style.visibility = "visible");
                    inputSpan.addEventListener("blur", () => cursorElement.style.visibility = "hidden");
                    inputSpan.addEventListener("paste", handlePaste);
                    inputSpan.addEventListener("keydown", handleKeyDown);
                    
                    wrapper.appendChild(promptSpan);
                    wrapper.appendChild(inputSpan);
                    wrapper.appendChild(cursorElement);
                    
                    return wrapper;
                }}
                
                function handlePaste(e) {{
                    e.preventDefault();
                    const text = (e.clipboardData || window.clipboardData).getData("text");
                    document.execCommand("insertText", false, text);
                }}
                
                function handleKeyDown(e) {{
                    if (e.key === "Enter") {{
                        e.preventDefault();
                        executeCommand(this);
                    }} else if (e.key === "ArrowUp") {{
                        e.preventDefault();
                        navigateHistory(-1, this);
                    }} else if (e.key === "ArrowDown") {{
                        e.preventDefault();
                        navigateHistory(1, this);
                    }}
                }}
                
                function navigateHistory(direction, inputElement) {{
                    const newIndex = commandHistoryIndex + direction;
                    
                    if (direction < 0 && newIndex >= 0) {{ // Up
                        commandHistoryIndex = newIndex;
                        inputElement.textContent = commandHistory[commandHistoryIndex];
                    }} else if (direction > 0) {{ // Down
                        if (newIndex < commandHistory.length) {{
                            commandHistoryIndex = newIndex;
                            inputElement.textContent = commandHistory[commandHistoryIndex];
                        }} else {{
                            commandHistoryIndex = commandHistory.length;
                            inputElement.textContent = "";
                        }}
                    }}
                    
                    placeCaretAtEnd(inputElement);
                }}
                
                function executeCommand(inputElement) {{
                    const command = inputElement.textContent.trim();
                    
                    const commandLine = inputElement.parentNode;
                    commandLine.innerHTML = `<span class="prompt"><span style="color:${{termConfig.promptColor}};">user@machine</span><span style="color:${{termConfig.fg}};">:</span><span style="color:#5f87ff;">~/projects</span><span style="color:${{termConfig.promptColor}};">$</span> </span>${{command}}`;
                    
                    if (command) {{
                        commandHistory.push(command);
                        commandHistoryIndex = commandHistory.length;
                        
                        const output = processCommand(command);
                        if (output) {{
                            const outputElem = document.createElement("div");
                            outputElem.className = "command-output";
                            if (output.includes('<span')) {{
                                outputElem.innerHTML = output;
                            }} else {{
                                outputElem.textContent = output;
                            }}
                            container.appendChild(outputElem);
                        }}
                    }}
                    
                    container.appendChild(createPrompt());
                    
                    const newInput = container.querySelector(".terminal-line:last-child .input-area");
                    if (newInput) {{
                        newInput.focus();
                        placeCaretAtEnd(newInput);
                    }}
                    
                    container.scrollTop = container.scrollHeight;
                }}
                
                function processCommand(cmdString) {{
                    if (!cmdString) return "";
                    
                    let [cmd, ...args] = cmdString.split(" ");
                    cmd = cmd.toLowerCase();
                    
                    return cmd in commands ? commands[cmd](args) : `bash: ${{cmd}}: command not found`;
                }}
                
                function placeCaretAtEnd(element) {{
                    const range = document.createRange();
                    const selection = window.getSelection();
                    range.selectNodeContents(element);
                    range.collapse(false);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }}
                
                window.updateTerminalConfig = function(configJson) {{
                    const newConfig = JSON.parse(configJson);
                    Object.assign(termConfig, newConfig);
                    updateTerminalStyling();
                }};
                
                container.appendChild(createPrompt());
                
                container.addEventListener("click", function() {{
                    const activeInput = container.querySelector(".terminal-line:last-child .input-area");
                    if (activeInput) {{
                        activeInput.focus();
                        placeCaretAtEnd(activeInput);
                    }}
                }});
                
                let cursorVisible = true;
                setInterval(() => {{
                    const cursors = container.querySelectorAll(".cursor");
                    cursorVisible = !cursorVisible;
                    cursors.forEach(cursor => {{
                        cursor.style.visibility = cursorVisible ? "visible" : "hidden";
                    }});
                }}, 500);
                
                setTimeout(() => {{
                    const firstInput = container.querySelector(".input-area");
                    if (firstInput) {{
                        firstInput.focus();
                        placeCaretAtEnd(firstInput);
                    }}
                }}, 100);
                
                updateTerminalStyling();
            }});
            </script>
            """
            
            terminal_html = f"""
            <style>
            @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
            #terminal-container {{ height: 100%; overflow: auto; font-family: '{font}', monospace; font-size: {font_size}px; line-height: {line_height}; }}
            .terminal-line {{ white-space: pre; padding: 0; margin: 0; display: flex; align-items: baseline; }}
            .command-output {{ white-space: pre; padding: 0; margin: 0; }}
            .cursor {{ {cursor_style_css} display: inline-block; width: 8px; height: 16px; vertical-align: middle; }}
            .input-area {{ background: transparent; border: none; outline: none; color: inherit; font-family: inherit; font-size: inherit; padding: 0; margin: 0; caret-color: transparent; min-width: 1px; }}
            </style>
            
            <div style="background:#2c2c2c;border-radius:6px;box-shadow:0 5px 15px rgba(0,0,0,0.4);overflow:hidden;width:100%;position:relative;margin-bottom:20px;">
                <!-- Window title bar -->
                <div style="display:flex;background:#21252b;padding:8px 15px;align-items:center;user-select:none;">
                    <div style="display:flex;gap:6px;">
                        <div style="height:12px;width:12px;background:#ff5f56;border-radius:50%;"></div>
                        <div style="height:12px;width:12px;background:#ffbd2e;border-radius:50%;"></div>
                        <div style="height:12px;width:12px;background:#27c93f;border-radius:50%;"></div>
                    </div>
                    <div style="flex-grow:1;text-align:center;color:#9da5b4;font-size:12px;">WezTerm - user@machine: ~/projects</div>
                </div>
                
                <!-- Tab bar -->
                <div id="terminal-tab-bar" style="display:{'' if enable_tab_bar else 'none'}">{tab_bar}</div>
                
                <!-- Terminal content area -->
                <div class="terminal-content-area" style="display:flex;height:{content_height}px;">
                    <div id="dynamic-terminal" style="flex-grow:1;background:{colors['bg']};color:{colors['fg']};padding:{padding}px;opacity:{opacity};">
                        <div id="terminal-container"></div>
                    </div>
                    <div id="terminal-scrollbar" style="display:{'' if enable_scroll_bar else 'none'}">{scrollbar}</div>
                </div>
            </div>
            {js_code}
            """
            
            return terminal_html
        except Exception as e:
            logger.error(f"Terminal önizlemesi oluşturulurken hata: {e}\n{traceback.format_exc()}")
            return f"<div style='color:red;padding:20px;background:#fff0f0;border-radius:5px;'>Terminal önizlemesi oluşturulamadı: {str(e)}</div>"


class ConfigGenerator:
    """WezTerm yapılandırma dosyası üreten sınıf"""

    @staticmethod
    def generate_wezterm_lua(config):
        """Generate WezTerm Lua configuration based on user selections"""
        try:
            cursor_style_map = {'Block': 'SteadyBlock', 'Bar': 'SteadyBar', 'Underline': 'SteadyUnderline'}
            wezterm_cursor_style = cursor_style_map.get(config['cursor_style'], 'SteadyBlock')
            
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

            if config['hyperlinkRules'] and len(config['hyperlinkRules']) > 0:
                lua_config.append("  -- Hyperlink settings")
                lua_config.append("  hyperlink_rules = {")
                
                if 'URL Algılama' in config['hyperlinkRules']:
                    lua_config.append("    -- URL detection")
                    lua_config.append("    {")
                    lua_config.append("      regex = '\\\\b\\\\w+://[\\\\w.-]+\\\\.[\\\\w.-]+\\\\S*\\\\b',")
                    lua_config.append("      format = '$0',")
                    lua_config.append("    },")
                
                if 'E-posta Adresleri' in config['hyperlinkRules']:
                    lua_config.append("    -- Email addresses")
                    lua_config.append("    {")
                    lua_config.append("      regex = '\\\\b\\\\w+@[\\\\w.-]+\\\\.[\\\\w]+\\\\b',")
                    lua_config.append("      format = 'mailto:$0',")
                    lua_config.append("    },")
                    
                if 'Dosya Yolları' in config['hyperlinkRules']:
                    lua_config.append("    -- File paths")
                    lua_config.append("    {")
                    lua_config.append("      regex = '\\\\b(\\\\w+:)?[\\\\/\\\\\\\\][\\\\w.~-]+[\\\\/\\\\\\\\][\\\\w.~-]+\\\\b',")
                    lua_config.append("      format = '$0',")
                    lua_config.append("    },")
                    
                lua_config.append("  },")

            if config['leader_key'] and config['leader_key'].strip():
                parts = [part.strip() for part in config['leader_key'].split('+')]
                if len(parts) >= 2:
                    key, mods = parts[-1].lower(), '+'.join(part.upper() for part in parts[:-1])
                else:
                    key, mods = config['leader_key'].strip().lower(), 'CTRL'

                lua_config.extend([
                    "  -- Leader key configuration",
                    f"  leader = {{ key = '{key}', mods = '{mods}', timeout_milliseconds = 1000 }},"
                ])

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
        st.set_page_config(layout="wide", page_title="WezTerm Configurator", page_icon="🖥️")
        self.initialize_session_state()
        self.load_css()
        
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

    def load_css(self):
        """Load custom CSS"""
        try:
            css_path = os.path.join(os.path.dirname(__file__), "assets/styles.css")
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"CSS yüklenirken hata: {e}")
            st.warning("Arayüz stilleri yüklenemedi.")

    @staticmethod
    def get_colors_for_theme(theme, color_scheme, custom_colors=None):
        """Get color values based on theme and color scheme"""
        if theme == "Custom" and custom_colors:
            return custom_colors
        return WezTermConfigurator.color_mappings.get(color_scheme, WezTermConfigurator.color_mappings['Builtin Dark'])

    def render_sidebar(self):
        """Render sidebar with configuration controls"""
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

        st.sidebar.markdown("## Terminal Seçenekleri")
        enable_tab_bar = st.sidebar.checkbox('Sekme Çubuğunu Etkinleştir', value=True)
        enable_scroll_bar = st.sidebar.checkbox('Kaydırma Çubuğunu Etkinleştir', value=False)
        cursor_style = st.sidebar.selectbox('İmleç Stili', ['Block', 'Bar', 'Underline'], index=0)

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

    def update_terminal(self, config):
        """Update terminal via JavaScript without reload"""
        theme_colors = self.get_colors_for_theme(config['theme'], config['color_scheme'], 
                                               config['custom_colors'])
        
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

    def config_has_changed(self, new_config):
        """Check if config has changed significantly from current state"""
        current = st.session_state.current_config
        
        if isinstance(new_config.get('custom_colors'), dict) and isinstance(current.get('custom_colors'), dict):
            if str(new_config['custom_colors']) != str(current['custom_colors']):
                return True
                
        if isinstance(new_config.get('hyperlinkRules'), list) and isinstance(current.get('hyperlinkRules'), list):
            if set(new_config['hyperlinkRules'] or []) != set(current['hyperlinkRules'] or []):
                return True
        
        for key, value in new_config.items():
            if key not in ('custom_colors', 'hyperlinkRules') and value != current.get(key):
                return True
                
        return False

    def run(self):
        """Run the WezTerm Configurator app"""
        st.title('WezTerm Yapılandırıcı')
        st.write('Sol menüden seçimlerinizi yapın ve terminal önizlemesini görün!')
        
        terminal_placeholder = st.empty()
        
        config = self.render_sidebar()
        
        config_changed = self.config_has_changed(config)
        
        st.subheader("Terminal Önizleme")
        
        try:
            if config_changed or 'terminal_html' not in st.session_state:
                colors = st.session_state['custom_colors'] if config['theme'] == 'Custom' else None
                terminal_html = TerminalPreviewGenerator.generate_dynamic_terminal_preview(
                    config['theme'], config['font'], config['font_size'], config['color_scheme'], 
                    colors, config['opacity'], config['enable_tab_bar'], config['enable_scroll_bar'], 
                    config['cursor_style'], config['padding'], config['line_height'], 
                    config['use_fancy_tab_bar'], config['hyperlinkRules'], config['leader_key']
                )
                
                st.session_state.terminal_html = terminal_html
                st.session_state.terminal_key += 1
                with terminal_placeholder:
                    components.html(terminal_html, height=450, scrolling=False)
            else:
                self.update_terminal(config)
                with terminal_placeholder:
                    components.html(st.session_state.terminal_html, height=450, scrolling=False)
            
            st.session_state.current_config = config.copy()
            
            st.caption("💡 **İpucu:** Terminal'e tıklayarak komut girebilirsiniz. Yukarı/aşağı ok tuşları ile komut geçmişini gezebilirsiniz.")
            st.caption("📋 **Kullanılabilir Komutlar:** `clear`, `ls`, `pwd`, `date`, `echo`, `help`, `wezterm`, `config`, `whoami`,`uname`, `screenfetch`")
            
        except Exception as e:
            logger.error(f"Terminal önizleme hatası: {e}\n{traceback.format_exc()}")
            st.error(f"Terminal önizleme hatası: {e}")
        
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
            st.markdown("### Aktif Ayarlar")
            
            display_colors = st.session_state['custom_colors'] if config['theme'] == 'Custom' else self.get_colors_for_theme(config['theme'], config['color_scheme'])
            
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

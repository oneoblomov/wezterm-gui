import logging
import traceback
from themes import get_colors_for_theme

logger = logging.getLogger("wezterm_gui")

class TerminalPreviewGenerator:
    """Terminal önizlemesi oluşturan sınıf"""
    
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
            colors = get_colors_for_theme(theme, color_scheme, custom_colors)
            content_height = 350 - (30 if enable_tab_bar else 0)
            
            # Define cursor styles
            cursor_styles = {
                'Block': f"background:{colors['prompt']};color:black;",
                'Bar': f"border-left:2px solid {colors['prompt']};",
                'Underline': f"border-bottom:2px solid {colors['prompt']};"
            }
            cursor_style_css = cursor_styles.get(cursor_style, cursor_styles['Block'])
            
            # Create components
            tab_bar = generate_tab_bar(enable_tab_bar, colors, use_fancy_tab_bar)
            scrollbar = generate_scrollbar(enable_scroll_bar, colors)
            js_code = generate_terminal_js(colors, font_size, line_height, cursor_style_css, padding, opacity, enable_tab_bar, enable_scroll_bar)
            
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


# Helper functions

def generate_tab_bar(enable_tab_bar, colors, use_fancy_tab_bar):
    """Generate tab bar HTML"""
    if not enable_tab_bar:
        return ""
        
    tab_bar_bg = colors['bg'] if not use_fancy_tab_bar else 'rgba(0,0,0,0.3)'
    active_tab_bg = colors['prompt'] if use_fancy_tab_bar else 'rgba(255,255,255,0.1)'
    inactive_tab_color = colors['fg'] if use_fancy_tab_bar else 'rgba(255,255,255,0.6)'
    tab_x = '<span style="font-size:10px;opacity:0.7;">✕</span>' if use_fancy_tab_bar else ''
    
    return f"""<div style="background:{tab_bar_bg};color:{colors['fg']};border-bottom:1px solid rgba(255,255,255,0.2);padding:5px 0;display:flex;align-items:center;">
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

def generate_scrollbar(enable_scroll_bar, colors):
    """Generate scrollbar HTML"""
    if not enable_scroll_bar:
        return ""
        
    return f"""<div style="width:10px;background:{colors['bg']};border-left:1px solid rgba(255,255,255,0.15);position:relative;">
        <div style="position:absolute;top:0;right:0;width:8px;height:30px;background:rgba(255,255,255,0.3);border-radius:4px;margin:2px;"></div>
    </div>"""

def generate_terminal_js(colors, font_size, line_height, cursor_style_css, padding, opacity, enable_tab_bar, enable_scroll_bar):
    """Generate terminal JavaScript code"""
    return f"""
    <script>
    // Terminal configuration object
    let termConfig = {{
        bg: "{colors['bg']}",
        fg: "{colors['fg']}",
        promptColor: "{colors['prompt']}",
        cursorStyle: "{cursor_style_css}",
        fontSize: {font_size},
        lineHeight: {line_height},
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
         \\`:+ssssssssssssssssss+:\\`           WezTerm 20XX.XX.X
       -+ssssssssssssssssssyyssss+-             Kernel: 6.2.0-32-generic
     .ossssssssssssssssssdMMMNysssso.           Uptime: 1h 23m
    /ssssssssssshdmmNNmmyNMMMMhssssss/          CPU: Intel i7-10700K
   +ssssssssshmydMMMMMMMNddddyssssssss+         RAM: 16GB
  /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/        Disk: 500GB SSD
 .ssssssssdMMMNhsssssssssshNMMMdssssssss.       GPU: NVIDIA GeForce GTX 1660
 +sssshhhyNMMNyssssssssssssyNMMMysssssss+       Shell: bash   
 ossyNMMMNyMMhsssssssssssssshmmmhssssssso       
 ossyNMMMNyMMhsssssssssssssshmmmhssssssso   
 +sssshhhyNMMNyssssssssssssyNMMMysssssss+   
 .ssssssssdMMMNhsssssssssshNMMMdssssssss.   
  /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/    
   +ssssssssshmydMMMMMMMNddddyssssssss+     
    /ssssssssssshdmmNNmmyNMMMMhssssss/      
     .ossssssssssssssssssdMMMNysssso.       
       -+ssssssssssssssssssyyssss+-         
         \\`:+ssssssssssssssssss+:\\`           
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

# Color schemes for WezTerm
COLOR_MAPPINGS = {
    'Builtin Dark': {'bg': '#121212', 'fg': '#d0d0d0', 'prompt': '#5fafff'},
    'Builtin Light': {'bg': '#f0f0f0', 'fg': '#333333', 'prompt': '#0087af'},
    'Gruvbox': {'bg': '#282828', 'fg': '#ebdbb2', 'prompt': '#b8bb26'},
    'Dracula': {'bg': '#282a36', 'fg': '#f8f8f2', 'prompt': '#bd93f9'},
    'Monokai': {'bg': '#272822', 'fg': '#f8f8f2', 'prompt': '#a6e22e'},
    'Solarized Dark': {'bg': '#002b36', 'fg': '#839496', 'prompt': '#268bd2'},
    'Solarized Light': {'bg': '#fdf6e3', 'fg': '#657b83', 'prompt': '#268bd2'},
    'Nord': {'bg': '#2e3440', 'fg': '#d8dee9', 'prompt': '#88c0d0'}
}

# Theme to color scheme mapping
THEME_COLOR_SCHEME_MAPPING = {
    'Dark': 'Builtin Dark',
    'Light': 'Builtin Light',
    'Custom': 'Custom'
}

def get_colors_for_theme(theme, color_scheme, custom_colors=None):
    """Get color values based on theme and color scheme"""
    if theme == "Custom" and custom_colors:
        return custom_colors
    return COLOR_MAPPINGS.get(color_scheme, COLOR_MAPPINGS['Builtin Dark'])

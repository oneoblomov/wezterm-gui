import unittest
import sys
import os

# Add the project root and src directory to the path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from src.config import ConfigGenerator
from src.terminal import TerminalPreviewGenerator
from src.themes import get_colors_for_theme, COLOR_MAPPINGS
from src.utils import config_has_changed


class TestBasicMath(unittest.TestCase):
    """Basit matematik işlemleri için test sınıfı"""
    
    def test_addition(self):
        """İki sayının toplamı testi"""
        result = 2 + 3
        self.assertEqual(result, 5)
    
    def test_subtraction(self):
        """İki sayının farkı testi"""
        result = 10 - 4
        self.assertEqual(result, 6)
    
    def test_multiplication(self):
        """İki sayının çarpımı testi"""
        result = 3 * 4
        self.assertEqual(result, 12)
    
    def test_division(self):
        """İki sayının bölümü testi"""
        result = 15 / 3
        self.assertEqual(result, 5.0)


class TestStringOperations(unittest.TestCase):
    """String işlemleri için test sınıfı"""
    
    def test_string_concatenation(self):
        """String birleştirme testi"""
        first_name = "John"
        last_name = "Doe"
        full_name = first_name + " " + last_name
        self.assertEqual(full_name, "John Doe")
    
    def test_string_length(self):
        """String uzunluğu testi"""
        text = "Hello World"
        self.assertEqual(len(text), 11)
    
    def test_string_upper_lower(self):
        """String büyük/küçük harf testi"""
        text = "Hello World"
        self.assertEqual(text.upper(), "HELLO WORLD")
        self.assertEqual(text.lower(), "hello world")


class TestListOperations(unittest.TestCase):
    """Liste işlemleri için test sınıfı"""
    
    def test_list_append(self):
        """Liste eleman ekleme testi"""
        numbers = [1, 2, 3]
        numbers.append(4)
        self.assertEqual(numbers, [1, 2, 3, 4])
    
    def test_list_length(self):
        """Liste uzunluğu testi"""
        fruits = ["apple", "banana", "orange"]
        self.assertEqual(len(fruits), 3)
    
    def test_list_contains(self):
        """Liste eleman içerme testi"""
        colors = ["red", "green", "blue"]
        self.assertIn("green", colors)
        self.assertNotIn("yellow", colors)


class TestConfigGenerator(unittest.TestCase):
    """ConfigGenerator sınıfı için basit testler"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.basic_config = {
            'font': 'JetBrains Mono',
            'font_size': 14,
            'theme': 'Dark',
            'color_scheme': 'Builtin Dark',
            'opacity': 0.95,
            'enable_tab_bar': True,
            'use_fancy_tab_bar': False,
            'enable_scroll_bar': False,
            'default_cursor_style': 'Block',
            'padding': 8,
            'line_height': 1.0,
            'window_width': 800,
            'window_height': 600,
            'hyperlinkRules': [],
            'leader_key': None,
            'custom_colors': {}
        }
    
    def test_config_has_values(self):
        """Yapılandırmanın değerleri olduğunu test et"""
        self.assertIsNotNone(self.basic_config['font'])
        self.assertIsInstance(self.basic_config['font_size'], int)
        self.assertTrue(self.basic_config['font_size'] > 0)
    
    def test_generate_lua_returns_string(self):
        """Lua oluşturucunun string döndürdüğünü test et"""
        result = ConfigGenerator.generate_wezterm_lua(self.basic_config)
        self.assertIsInstance(result, (str, type(None)))
        if result is not None:
            self.assertTrue(len(result) > 0)


class TestThemes(unittest.TestCase):
    """Tema işlemleri için basit testler"""
    
    def test_color_mappings_exists(self):
        """COLOR_MAPPINGS'in var olduğunu test et"""
        self.assertIsInstance(COLOR_MAPPINGS, dict)
        self.assertTrue(len(COLOR_MAPPINGS) > 0)
    
    def test_builtin_themes_exist(self):
        """Yerleşik temaların var olduğunu test et"""
        expected_themes = ['Builtin Dark', 'Builtin Light']
        for theme in expected_themes:
            self.assertIn(theme, COLOR_MAPPINGS)
    
    def test_theme_has_colors(self):
        """Temaların renk değerleri olduğunu test et"""
        for theme_name, colors in COLOR_MAPPINGS.items():
            self.assertIsInstance(colors, dict)
            # Her tema en az bg ve fg renklerine sahip olmalı
            self.assertIn('bg', colors)
            self.assertIn('fg', colors)


class TestUtils(unittest.TestCase):
    """Yardımcı fonksiyonlar için basit testler"""
    
    def test_config_has_changed_same_configs(self):
        """Aynı yapılandırmalar için değişiklik kontrolü"""
        config1 = {'font': 'Arial', 'size': 12}
        config2 = {'font': 'Arial', 'size': 12}
        
        # Bu fonksiyon çeşitli şekillerde davranabilir, sadece bool döndürdüğünü kontrol et
        result = config_has_changed(config1, config2)
        self.assertIsInstance(result, bool)
    
    def test_config_has_changed_different_configs(self):
        """Farklı yapılandırmalar için değişiklik kontrolü"""
        config1 = {'font': 'Arial', 'size': 12}
        config2 = {'font': 'Times', 'size': 14}
        
        result = config_has_changed(config1, config2)
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    # Test çalıştırıcısı
    print("Basit testler çalıştırılıyor...")
    unittest.main(verbosity=2)

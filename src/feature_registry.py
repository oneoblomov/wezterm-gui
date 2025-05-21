import streamlit as st
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional, Union

@dataclass
class Feature:
    """Bir yapılandırma özelliğini temsil eder"""
    name: str  # Özellik adı
    category: str  # Kategori (Tema, Terminal, Pencere, vb.)
    default_value: Any  # Varsayılan değer
    description: str = ""  # Açıklama
    options: List[Any] = field(default_factory=list)  # Seçenekler listesi (selectbox için)
    min_value: Optional[Union[int, float]] = None  # Minimum değer (slider/number input için)
    max_value: Optional[Union[int, float]] = None  # Maksimum değer (slider/number input için)
    step: Optional[Union[int, float]] = None  # Adım boyutu (slider/number input için)
    widget_type: str = "selectbox"  # Widget türü (selectbox, slider, checkbox, vb.)
    depends_on: Optional[Dict[str, Any]] = None  # Bağımlılıklar
    render_function: Optional[Callable] = None  # Özel render fonksiyonu

class FeatureRegistry:
    """Özellik kaydı ve yönetimi için registry sınıfı"""
    
    _features: Dict[str, Feature] = {}
    _categories: Dict[str, List[Feature]] = {}
    
    @classmethod
    def register(cls, feature: Feature):
        """Bir özelliği registry'e ekle"""
        cls._features[feature.name] = feature
        
        # Kategori yoksa oluştur
        if feature.category not in cls._categories:
            cls._categories[feature.category] = []
        
        # Özelliği kategorisine ekle
        cls._categories[feature.category].append(feature)
        
        # Session state'e varsayılan değeri ekle
        if feature.name not in st.session_state:
            st.session_state[feature.name] = feature.default_value
    
    @classmethod
    def get_feature(cls, name: str) -> Optional[Feature]:
        """Adına göre bir özelliği al"""
        return cls._features.get(name)
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Tüm kategorilerin listesini al"""
        return list(cls._categories.keys())
    
    @classmethod
    def get_features_by_category(cls, category: str) -> List[Feature]:
        """Kategoriye göre özellikleri al"""
        return cls._categories.get(category, [])
    
    @classmethod
    def render_feature(cls, feature_name: str) -> Any:
        """Belirli bir özelliği render et ve değerini döndür"""
        feature = cls.get_feature(feature_name)
        if not feature:
            return None
        
        # Özel render fonksiyonu varsa onu kullan
        if feature.render_function:
            return feature.render_function(feature)
        
        # Bağımlılıkları kontrol et
        if feature.depends_on:
            show_feature = True
            for dep_key, dep_value in feature.depends_on.items():
                if st.session_state.get(dep_key) != dep_value:
                    show_feature = False
                    break
            
            if not show_feature:
                return st.session_state.get(feature.name)
        
        # Farklı widget türlerine göre render et
        if feature.widget_type == "selectbox":
            value = st.sidebar.selectbox(
                feature.name, 
                feature.options, 
                index=feature.options.index(st.session_state[feature.name])
                if st.session_state[feature.name] in feature.options else 0
            )
        elif feature.widget_type == "slider":
            value = st.sidebar.slider(
                feature.name,
                min_value=feature.min_value or 0,
                max_value=feature.max_value or 100,
                value=st.session_state[feature.name],
                step=feature.step or 1
            )
        elif feature.widget_type == "checkbox":
            value = st.sidebar.checkbox(
                feature.name,
                value=st.session_state[feature.name]
            )
        elif feature.widget_type == "number_input":
            value = st.sidebar.number_input(
                feature.name,
                min_value=feature.min_value,
                max_value=feature.max_value,
                value=st.session_state[feature.name],
                step=feature.step or 1
            )
        elif feature.widget_type == "multiselect":
            value = st.sidebar.multiselect(
                feature.name,
                feature.options,
                default=st.session_state[feature.name]
            )
        else:
            return st.session_state.get(feature.name)
        
        # Session state'i güncelle
        st.session_state[feature.name] = value
        return value

    @classmethod
    def render_category(cls, category: str) -> Dict[str, Any]:
        """Bir kategoriyi render et ve ayarları bir sözlük olarak döndür"""
        features = cls.get_features_by_category(category)
        st.sidebar.markdown(f"## {category}")
        
        values = {}
        for feature in features:
            values[feature.name] = cls.render_feature(feature.name)
        
        return values
    
    @classmethod
    def register_defaults(cls):
        """Varsayılan özellikleri kaydet"""
        # Tema özellikleri
        cls.register(Feature(
            name="theme",
            category="Tema Ayarları",
            default_value="Dark",
            description="Tema türü",
            options=["Dark", "Light", "Custom"],
            widget_type="selectbox"
        ))
        
        cls.register(Feature(
            name="font",
            category="Tema Ayarları",
            default_value="JetBrains Mono",
            description="Yazı tipi",
            options=["JetBrains Mono", "Fira Code", "Cascadia Code", "Hack", 
                    "Source Code Pro", "Ubuntu Mono", "Menlo", "Monaco"],
            widget_type="selectbox"
        ))
        
        cls.register(Feature(
            name="font_size",
            category="Tema Ayarları",
            default_value=14,
            description="Yazı boyutu",
            min_value=8,
            max_value=32,
            step=1,
            widget_type="slider"
        ))
        
        # Buraya daha fazla varsayılan özellik eklenebilir

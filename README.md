# WezTerm Yapılandırıcı

WezTerm terminal emülatörü için görsel bir yapılandırma aracı. Basit ve etkileşimli bir arayüz ile WezTerm ayarlarınızı düzenleyebilir ve sonuçları gerçek zamanlı olarak görebilirsiniz.

## Canlı Demo

Uygulamaya buradan ulaşabilirsiniz: [https://wezterm-gui.streamlit.app/](https://wezterm-gui.streamlit.app/)

## Özellikler

- Terminal önizlemesi
- Renk şemalarını özelleştirme
- Yazı tipi, boyut ve boşluk ayarları
- Sekme çubuğu ve kaydırma çubuğu konfigürasyonu
- İmleç stili seçimi
- Lider tuşu ve kısayol ayarları
- Lua yapılandırma dosyası oluşturma

## Kurulum

1. Bu projeyi klonlayın:

   ```bash
   git clone https://github.com/oneoblomov/wezterm-gui.git
   cd wezterm-gui
   ```

2. Gerekli Python paketlerini yükleyin:

   ```bash
   pip install -r requirements.txt
   ```

3. Uygulamayı çalıştırın:

   ```bash
   streamlit run app.py
   ```

## Kullanım

1. Sol menüden istediğiniz renk şeması, yazı tipi ve diğer ayarları seçin
2. Terminal önizlemesini gerçek zamanlı olarak görün
3. Oluşturulan Lua yapılandırma dosyasını indirin
4. `wezterm.lua` dosyasını WezTerm konfigürasyon dizininize yerleştirin

## WezTerm Yapılandırma Dosyası Konumu

- Windows: `%USERPROFILE%\.wezterm.lua`
- macOS/Linux: `~/.config/wezterm/wezterm.lua`

## Gereksinimler

- Python 3.7+
- Streamlit
- Modern bir web tarayıcısı

## Lisans

MIT

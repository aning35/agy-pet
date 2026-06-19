import pystray
from PIL import Image, ImageDraw
import multiprocessing

def _create_default_image():
    import os
    import sys
    
    def get_base_dir():
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    icon_path = os.path.join(get_base_dir(), "assets", "tray_icon.png")
    if os.path.exists(icon_path):
        return Image.open(icon_path).convert("RGBA")
    else:
        # Fallback if missing
        image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(image)
        d.ellipse((8, 8, 56, 56), fill=(36, 39, 58), outline=(202, 211, 245), width=3)
        return image

def run_tray_process(command_queue):
    from config_manager import load_config
    from i18n import t

    def get_label(key):
        def _get(item):
            try:
                config = load_config()
                lang = config.get("language", "en")
                return t(key, lang)
            except Exception:
                return t(key, "en")
        return _get

    def on_toggle(icon, item):
        command_queue.put("TOGGLE")
        
    def on_quit(icon, item):
        command_queue.put("QUIT")
        icon.stop()
        
    def on_settings(icon, item):
        command_queue.put("SETTINGS")
        
    image = _create_default_image()
    menu = pystray.Menu(
        pystray.MenuItem(get_label("tray_toggle"), on_toggle, default=True),
        pystray.MenuItem(get_label("tray_settings"), on_settings),
        pystray.MenuItem(get_label("tray_quit"), on_quit)
    )
    
    icon = pystray.Icon("AgyPet", image, "AgyPet v0.1.2", menu)
    icon.run()

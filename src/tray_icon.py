import pystray
from PIL import Image, ImageDraw
import multiprocessing

def _create_default_image():
    # Create a 64x64 transparent image
    image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    
    # Draw a cute simple capsule/pill face to represent the pet
    d.ellipse((8, 8, 56, 56), fill=(36, 39, 58), outline=(202, 211, 245), width=3)
    # Eyes
    d.ellipse((20, 24, 28, 32), fill=(166, 218, 149)) # Green eyes
    d.ellipse((36, 24, 44, 32), fill=(166, 218, 149))
    # Mouth
    d.arc((24, 36, 40, 48), 0, 180, fill=(237, 135, 150), width=3)
    
    return image

def run_tray_process(command_queue):
    def on_toggle(icon, item):
        command_queue.put("TOGGLE")
        
    def on_quit(icon, item):
        command_queue.put("QUIT")
        icon.stop()
        
    image = _create_default_image()
    menu = pystray.Menu(
        pystray.MenuItem("Show/Hide Pet", on_toggle, default=True),
        pystray.MenuItem("Quit", on_quit)
    )
    
    icon = pystray.Icon("AgyPet", image, "AgyPet v0.1.0", menu)
    icon.run()

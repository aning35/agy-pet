import sys
import os
import tkinter as tk
from PIL import Image, ImageTk

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AnimatedGif:
    def __init__(self, canvas, image_id, path, delay=40):
        self.canvas = canvas
        self.image_id = image_id
        self.delay = delay
        self.frames = []
        im = Image.open(path)
        i = 0
        while True:
            self.frames.append(ImageTk.PhotoImage(im.copy().convert("RGBA")))
            i += 1
            try:
                im.seek(i)
            except EOFError:
                break
        self.current_frame = 0
        self.is_running = True
        self.next_frame()

    def next_frame(self):
        if not self.is_running or not self.frames:
            return
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.canvas.itemconfig(self.image_id, image=self.frames[self.current_frame])
        self.canvas.after(self.delay, self.next_frame)

def show_fireworks_mac(gif_path):
    try:
        import objc
        from AppKit import NSApplication, NSWindow, NSWindowStyleMaskBorderless, NSColor, NSImageView, NSImage, NSMakeRect, NSScreen
        
        class FireworksApp(NSApplication):
            def closeApp_(self, sender):
                self.terminate_(self)

        app = FireworksApp.sharedApplication()
        
        # Center on screen
        main_screen = NSScreen.mainScreen()
        if main_screen:
            screen_frame = main_screen.frame()
        else:
            screen_frame = NSMakeRect(0, 0, 1920, 1080)
        
        width = 800
        height = 600
        # Basic centering, AppKit uses bottom-left origin
        x = (screen_frame.size.width - width) / 2
        y = (screen_frame.size.height - height) / 2
        
        rect = NSMakeRect(x, y, width, height)
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, NSWindowStyleMaskBorderless, 2, False
        )
        
        win.setOpaque_(False)
        win.setBackgroundColor_(NSColor.clearColor())
        win.setLevel_(2000) # Floating
        win.setIgnoresMouseEvents_(True) # Click-through
        
        image = NSImage.alloc().initWithContentsOfFile_(gif_path)
        if not image:
            sys.exit(1)
            
        image_view = NSImageView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))
        image_view.setImage_(image)
        
        win.setContentView_(image_view)
        win.makeKeyAndOrderFront_(None)
        
        # Close after 4 seconds
        app.performSelector_withObject_afterDelay_(
            objc.selector(app.closeApp_, signature=b'v@:@'), None, 4.0
        )
        
        app.run()
    except Exception as e:
        print(f"macOS native fireworks failed: {e}")
        # Could fallback to Tkinter if needed, but it's broken anyway

def main():
    base_dir = get_base_dir()
    gif_path = os.path.join(base_dir, "assets", "gifs", "fireworks.gif")
    if not os.path.exists(gif_path):
        print(f"File not found: {gif_path}")
        sys.exit(1)

    if sys.platform == "darwin":
        show_fireworks_mac(gif_path)
        return

    # Windows fallback
    root = tk.Tk()
    
    transparent_color = "#000002"
    try:
        root.attributes("-transparentcolor", transparent_color)
    except Exception:
        pass
        
    root.configure(bg=transparent_color)
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    
    width = 800
    height = 600
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Make click-through on Windows
    if os.name == 'nt':
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, ex_style | 0x00080000 | 0x00000020)
        except Exception:
            pass
            
    canvas = tk.Canvas(root, bg=transparent_color, highlightthickness=0, bd=0, width=width, height=height)
    canvas.pack(fill=tk.BOTH, expand=True)
    image_id = canvas.create_image(width//2, height//2, anchor="center")
        
    global anim
    anim = AnimatedGif(canvas, image_id, gif_path, delay=40)
    
    root.lift()
    
    # Destroy after 4 seconds
    root.after(4000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    main()

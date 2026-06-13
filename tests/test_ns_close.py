import objc
from AppKit import NSApplication, NSWindow, NSWindowStyleMaskBorderless, NSColor, NSImageView, NSImage, NSMakeRect
import sys
import os

class FireworksApp(NSApplication):
    def closeApp_(self, sender):
        self.terminate_(self)

def show_gif():
    app = FireworksApp.sharedApplication()
    
    rect = NSMakeRect(200, 200, 800, 600)
    win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        rect, NSWindowStyleMaskBorderless, 2, False
    )
    
    win.setOpaque_(False)
    win.setBackgroundColor_(NSColor.clearColor())
    win.setLevel_(2000)
    
    image = NSImage.alloc().initWithContentsOfFile_("assets/gifs/fireworks.gif")
    if not image:
        sys.exit(1)
        
    image_view = NSImageView.alloc().initWithFrame_(rect)
    image_view.setImage_(image)
    
    win.setContentView_(image_view)
    win.makeKeyAndOrderFront_(None)
    
    # Close after 4 seconds
    app.performSelector_withObject_afterDelay_(
        objc.selector(app.closeApp_, signature=b'v@:@'), None, 4.0
    )
    
    app.run()

if __name__ == "__main__":
    show_gif()

import tkinter as tk
import sys
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
if sys.platform == "darwin":
    root.attributes("-transparent", True)

def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings")
    win.geometry("200x200")
    win.transient(root)
    tk.Label(win, text="Hello").pack()
    
tk.Button(root, text="Settings", command=open_settings).pack()
root.geometry("100x100+100+100")
root.mainloop()

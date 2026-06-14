import sys
import os
import multiprocessing
from config_manager import load_config
from pet_sender import SerialPetSender, BLEPetSender
from desktop_pet_ui import DesktopPetUI
from tray_icon import run_tray_process

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

import socket

def get_lock():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 43210)) # AgyPet lock port
        return s
    except socket.error:
        return None

def main():
    if "--fireworks" in sys.argv:
        import fireworks_process
        fireworks_process.main()
        return

    lock_socket = get_lock()
    if not lock_socket:
        print("AgyPet is already running!")
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("AgyPet v0.1.2", "AgyPet is already running in the background!\nCheck your system tray (near the clock).")
        return

    config = load_config()
    sender = None
    
    if config.get("mode") == "serial":
        sender = SerialPetSender(port=config.get("serial_port", "COM3"), baudrate=int(config.get("serial_baudrate", 115200)))
    elif config.get("mode") == "ble":
        sender = BLEPetSender(ble_name=config.get("ble_name", "AgyPet"))
        
    import tkinter as tk
    root = tk.Tk()
    
    command_queue = multiprocessing.Queue()
    tray_process = multiprocessing.Process(target=run_tray_process, args=(command_queue,), daemon=True)
    tray_process.start()
    
    app = DesktopPetUI(root, sender=sender, command_queue=command_queue)
    root.mainloop()
    
    if tray_process.is_alive():
        tray_process.terminate()
        tray_process.join(timeout=1)
        if tray_process.is_alive():
            tray_process.kill()
        
    if sender:
        sender.close()
        
    # Force exit to prevent background threads/processes from hanging
    os._exit(0)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

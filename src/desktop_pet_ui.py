import sys
import math
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
import os
import subprocess
import asyncio
import pygame
from PIL import Image, ImageTk
from watchdog.observers import Observer
from bleak import BleakScanner

from state_parser import LogHandler, AntigravityState, get_latest_conversation_log, get_today_statistics
from config_manager import load_config, save_config

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AnimatedGif:
    def __init__(self, canvas, image_id, path, delay=100):
        self.canvas = canvas
        self.image_id = image_id
        self.path = path
        self.delay = delay
        self.frames = []
        self.current_frame = 0
        self.is_running = False
        self.load_frames()

    def load_frames(self):
        try:
            if not os.path.exists(self.path):
                return
            im = Image.open(self.path)
            i = 0
            while True:
                # Need to convert to RGBA to preserve transparency
                photo = ImageTk.PhotoImage(im.copy().convert("RGBA"))
                self.frames.append(photo)
                i += 1
                try:
                    im.seek(i)
                except EOFError:
                    break
        except Exception as e:
            print(f"Error loading GIF {self.path}: {e}")

    def start(self):
        self.is_running = True
        self.current_frame = 0
        self.next_frame()

    def stop(self):
        self.is_running = False

    def next_frame(self):
        if not self.is_running or not self.frames:
            return
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.canvas.itemconfig(self.image_id, image=self.frames[self.current_frame])
        self.canvas.after(self.delay, self.next_frame)

class DesktopPetUI:
    def __init__(self, root, sender=None, command_queue=None):
        self.root = root
        self.sender = sender
        self.command_queue = command_queue
        self.is_visible = True
        self._last_sent_state = None
        self.root.title("Agy Pet")
        
        # Frameless and always on top
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Transparent Background magic for Windows/macOS
        self.transparent_color = "#000001"
        try:
            if sys.platform == "win32":
                self.root.attributes("-transparentcolor", self.transparent_color)
            elif sys.platform == "darwin":
                self.root.attributes("-transparent", True)
                self.transparent_color = "systemTransparent"
        except Exception as e:
            print(f"Transparency not supported: {e}")
        self.root.configure(bg=self.transparent_color)
        
        self.width = 250
        self.height = 64
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - self.width - 30
        y_pos = 60
        self.root.geometry(f"{self.width}x{self.height}+{x_pos}+{y_pos}")
        
        self.current_win_x = x_pos
        self.current_win_y = y_pos
        
        self.state_queue = queue.Queue()
        self.current_state = None
        
        # Docking state
        self.is_docked = False
        self.dock_edge = None
        self.undocked_geometry = None
        self.dock_threshold = 40
        self.bar_thickness = 6
        self.dock_start_x = None
        self.dock_start_y = None
        
        # Local Enhancements State
        self.stats_file = os.path.join(os.path.dirname(__file__), "..", "pet_stats.json")
        self.stats = {"thinking_time": 0, "errors": 0, "uptime": 0}
        self.session_start = time.time()
        self.last_think_start = None
        self.load_stats()
        
        self.dashboard_window = None
        
        try:
            pygame.mixer.init()
            config = load_config()
            pygame.mixer.music.set_volume(config.get("volume", 1.0))
        except Exception as e:
            print(f"Audio init error: {e}")
        
        # Colors (Catppuccin Macchiato Theme)
        self.bg_color = "#24273A" # Base
        self.fg_color = "#CAD3F5" # Text
        
        # Initialize Ttk style once to prevent macOS blank screen bug
        self.style = ttk.Style()
        if "clam" in self.style.theme_names():
            self.style.theme_use('clam')
            
        self.settings_win = None
        
        # Main Canvas
        self.canvas = tk.Canvas(self.root, bg=self.transparent_color, highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw Rounded Pill
        self.draw_rounded_rect(0, 0, self.width, self.height, radius=16, fill=self.bg_color)
        
        # Draw Drag Grip
        grip_color = "#5B6078"
        for i in range(3):
            y = 22 + i*8
            self.canvas.create_oval(12, y, 15, y+3, fill=grip_color, outline="")
            self.canvas.create_oval(18, y, 21, y+3, fill=grip_color, outline="")
            
        # Canvas Elements
        # Pet Image Holder
        self.pet_image_item = self.canvas.create_image(45, 32, anchor="center")
        self.current_anim = None
        
        # Text Labels
        self.status_item = self.canvas.create_text(75, 20, text="IDLE", font=("Segoe UI", 12, "bold"), fill="#A6DA95", anchor="w")
        self.detail_item = self.canvas.create_text(75, 42, text="Startup", font=("Segoe UI", 9), fill="#8AADF4", anchor="w")
        
        self.close_item = self.canvas.create_text(self.width - 15, 15, text="✖", font=("Segoe UI", 10, "bold"), fill="#ED8796", activefill="#F5BDE6")
        self.conn_status_item = self.canvas.create_text(self.width - 15, 45, text="", font=("Segoe UI", 8, "bold"), anchor="e")
        
        # Event Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        
        # Bind right-click on both canvas and root to ensure it catches on macOS
        for widget in (self.canvas, self.root):
            widget.bind("<Button-2>", self.show_context_menu)
            widget.bind("<Button-3>", self.show_context_menu)
            widget.bind("<ButtonPress-2>", self.show_context_menu)
            widget.bind("<ButtonPress-3>", self.show_context_menu)
            widget.bind("<Control-Button-1>", self.show_context_menu)
            
            # Re-assert topmost when mouse hovers or clicks
            widget.bind("<Enter>", lambda e: self.root.attributes("-topmost", True), add="+")
            widget.bind("<ButtonPress-1>", lambda e: self.root.attributes("-topmost", True), add="+")

        
        # Context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="📊 Show Dashboard", command=self.toggle_dashboard)
        self.menu.add_separator()
        self.menu.add_command(label="⚙️ Settings", command=self.open_settings)
        self.menu.add_command(label="📂 Open AI Logs", command=self.open_log_folder)
        self.menu.add_command(label="📂 Open Hardware Log", command=self.open_hardware_log)
        test_hw_menu = tk.Menu(self.menu, tearoff=0)
        test_hw_menu.add_command(label="IDLE (0x01)", command=lambda: self.on_state_change(AntigravityState.IDLE, "Test Hardware"))
        test_hw_menu.add_command(label="THINKING (0x02)", command=lambda: self.on_state_change(AntigravityState.THINKING, "Test Hardware"))
        test_hw_menu.add_command(label="WAITING (0x03)", command=lambda: self.on_state_change(AntigravityState.WAITING_CONFIRM, "Test Hardware"))
        test_hw_menu.add_command(label="ERROR (0x04)", command=lambda: self.on_state_change(AntigravityState.ERROR, "Test Hardware"))
        test_hw_menu.add_separator()
        test_hw_menu.add_command(label="DRINK WATER (Audio)", command=self.test_drink_water)
        
        self.menu.add_cascade(label="🛠️ Test & Debug", menu=test_hw_menu)
        self.menu.add_command(label="🎆 Test Fireworks UI", command=self.show_fireworks)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Exit", command=lambda: self.root.destroy())

        self.start_background_listener()
        self.poll_queue()
        self.update_ui()
        self.update_appearance(AntigravityState.IDLE, "Startup")
        
        # Periodic canvas self-heal to prevent DWM transparency rendering loss
        self._last_canvas_heal = time.time()
        self._canvas_heal_interval = 30  # seconds
        self.schedule_canvas_heal()
        
        if self.sender:
            self.sender.set_status_callback(self.on_connection_status)

        # Water reminder setup
        self.last_water_reminder = time.time()
        self._last_minute_checked = -1
        self.check_water_reminder()

    def check_water_reminder(self):
        try:
            config = load_config()
            times_str = config.get("water_times", "")
            
            now = time.time()
            import datetime
            dt_now = datetime.datetime.now()
            current_minute = dt_now.hour * 60 + dt_now.minute
            
            should_remind = False
            
            # Check fixed times (trigger once per minute)
            if self._last_minute_checked != current_minute:
                self._last_minute_checked = current_minute
                
                if times_str:
                    time_parts = [t.strip() for t in times_str.split(',') if t.strip()]
                    for t in time_parts:
                        try:
                            h, m = map(int, t.split(':'))
                            if dt_now.hour == h and dt_now.minute == m:
                                should_remind = True
                                break
                        except Exception:
                            pass
                
            if should_remind:
                self.last_water_reminder = now
                self.test_drink_water()
        except Exception as e:
            print(f"Error checking water reminder: {e}")
            
        # Check every 10 seconds
        self.root.after(10000, self.check_water_reminder)

    def test_drink_water(self):
        try:
            config = load_config()
            voice_profile = config.get("voice_profile", "baba")
            base_dir = get_base_dir()
            self.play_sound(os.path.join(base_dir, "assets", "sounds", voice_profile, "drink.mp3"))
        except Exception as e:
            print(f"Error playing test drink water sound: {e}")

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                import json
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Reset if it's a new day
                    import datetime
                    last_date = data.get("date", "")
                    current_date = datetime.date.today().isoformat()
                    if last_date == current_date:
                        self.stats = data
                    else:
                        self.stats = {"thinking_time": 0, "errors": 0, "uptime": 0, "date": current_date}
            except:
                pass
        else:
            import datetime
            self.stats["date"] = datetime.date.today().isoformat()

    def save_stats(self):
        try:
            import json
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def toggle_dashboard(self, event=None):
        if self.dashboard_window and self.dashboard_window.winfo_exists():
            self.dashboard_window.destroy()
            self.dashboard_window = None
            return
            
        x = event.x_root if event else self.root.winfo_pointerx()
        y = event.y_root if event else self.root.winfo_pointery()
        
        self.dashboard_window = tk.Toplevel(self.root)
        self.dashboard_window.title("AgyPet Stats")
        self.dashboard_window.geometry(f"200x150+{x+10}+{y+10}")
        self.dashboard_window.configure(bg="#303446")
        self.dashboard_window.overrideredirect(True)
        self.dashboard_window.attributes("-topmost", True)
        
        ttk.Label(self.dashboard_window, text="Today's Workload", font=("Segoe UI", 10, "bold"), background="#303446", foreground="#A6DA95").pack(pady=5)
        
        config = load_config()
        stats = get_today_statistics(config.get("brain_dir", ""))
        
        ttk.Label(self.dashboard_window, text=f"User Requests: {stats['user_requests']}", background="#303446", foreground="#CAD3F5").pack(anchor="w", padx=15)
        ttk.Label(self.dashboard_window, text=f"AI Actions: {stats['model_steps']}", background="#303446", foreground="#CAD3F5").pack(anchor="w", padx=15)
        ttk.Label(self.dashboard_window, text=f"Tools Used: {stats['tool_calls']}", background="#303446", foreground="#CAD3F5").pack(anchor="w", padx=15)
        ttk.Label(self.dashboard_window, text=f"Errors: {stats['errors']}", background="#303446", foreground="#ED8796").pack(anchor="w", padx=15)
        
        # Close on click
        self.dashboard_window.bind("<Button-1>", lambda e: self.toggle_dashboard(None))

    def on_connection_status(self, mode, is_connected, message=""):
        def _update():
            if is_connected:
                text = f"{mode} ✅"
                color = "#A6DA95" # Green
            else:
                if "error" in message.lower() or "fail" in message.lower():
                    text = f"{mode} ❌" # Error
                    color = "#ED8796" # Red
                else:
                    text = f"{mode} ⌛" # Scanning/Waiting
                    color = "#F5A97F" # Orange
            self.canvas.itemconfig(self.conn_status_item, text=text, fill=color)
        self.root.after(0, _update)

    def draw_rounded_rect(self, x1, y1, x2, y2, radius=15, **kwargs):
        self.canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, style=tk.PIESLICE, outline="", **kwargs)
        self.canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, style=tk.PIESLICE, outline="", **kwargs)
        self.canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, style=tk.PIESLICE, outline="", **kwargs)
        self.canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, style=tk.PIESLICE, outline="", **kwargs)
        self.canvas.create_rectangle(x1+radius-1, y1, x2-radius+1, y2, outline="", **kwargs)
        self.canvas.create_rectangle(x1, y1+radius-1, x2, y2-radius+1, outline="", **kwargs)

    def on_click(self, event):
        item = self.canvas.find_withtag("current")
        if item and item[0] == self.close_item:
            self.root.withdraw()
            self.is_visible = False
        else:
            self.start_move(event)

    def poll_queue(self):
        if self.command_queue:
            import queue
            try:
                while True:
                    cmd = self.command_queue.get_nowait()
                    if cmd == "TOGGLE":
                        if self.is_visible:
                            self.root.withdraw()
                            self.is_visible = False
                        else:
                            self.root.deiconify()
                            self.is_visible = True
                            
                            # Recovery: If window is offscreen or lost due to drag bug, reset to center
                            screen_w = self.root.winfo_screenwidth()
                            screen_h = self.root.winfo_screenheight()
                            win_x = self.root.winfo_x()
                            win_y = self.root.winfo_y()
                            if (win_x < -self.width or win_x > screen_w) or \
                               (win_y < -self.height or win_y > screen_h):
                                new_x = (screen_w - self.width) // 2
                                new_y = (screen_h - self.height) // 2
                                self.current_win_x = new_x
                                self.current_win_y = new_y
                                self.root.geometry(f"{self.width}x{self.height}+{new_x}+{new_y}")
                    elif cmd == "QUIT":
                        self.root.destroy()
                    elif cmd == "SETTINGS":
                        self.open_settings()
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error in poll_queue: {e}")
            self.root.after(100, self.poll_queue)

    def open_log_folder(self):
        config = load_config()
        brain_dir = config.get("brain_dir", "")
        log_file = get_latest_conversation_log(brain_dir)
        if log_file and os.path.exists(log_file):
            if sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', log_file])
            else:
                subprocess.Popen(['explorer', '/select,', os.path.normpath(log_file)])
        elif brain_dir and os.path.exists(brain_dir):
            if sys.platform == 'darwin':
                subprocess.Popen(['open', brain_dir])
            else:
                subprocess.Popen(['explorer', os.path.normpath(brain_dir)])
        else:
            messagebox.showwarning("Not Found", "No active log directory found.\nPlease configure it in Settings.", parent=self.root)

    def open_hardware_log(self):
        try:
            if getattr(sys, 'frozen', False):
                log_dir = os.path.expanduser("~/.agypet")
                os.makedirs(log_dir, exist_ok=True)
            else:
                log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_file = os.path.join(log_dir, "agypet_hardware.log")
            if os.path.exists(log_file):
                if sys.platform == 'darwin':
                    subprocess.Popen(['open', log_file])
                else:
                    os.startfile(os.path.normpath(log_file))
            else:
                messagebox.showwarning("Not Found", "No hardware log found yet.\nLog will be created after the first BLE/Serial connection attempt.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open log: {e}", parent=self.root)

    def show_context_menu(self, event):
        import time
        if not hasattr(self, 'last_menu_time'):
            self.last_menu_time = 0
            
        # Debounce to prevent double-popup
        if time.time() - self.last_menu_time < 0.3:
            return "break"
            
        self.last_menu_time = time.time()
        
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
            
        return "break"

    def open_settings(self):
        if self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.lift()
            self.settings_win.focus_force()
            return
            
        settings_win = tk.Toplevel(self.root)
        self.settings_win = settings_win
        settings_win.title("AgyPet Settings")
        
        config = load_config()
        settings_x = config.get("settings_x", -1)
        settings_y = config.get("settings_y", -1)
        if settings_x != -1 and settings_y != -1:
            settings_win.geometry(f"+{settings_x}+{settings_y}")
            
        # We will auto-size the window height after all widgets are added
        settings_win.minsize(480, 500)
            
        if sys.platform != "darwin":
            settings_win.transient(self.root)
            settings_win.grab_set()
            
        settings_win.configure(bg="#ECEFF4")
        
        def on_close():
            config["settings_x"] = settings_win.winfo_x()
            config["settings_y"] = settings_win.winfo_y()
            save_config(config)
            # Fix macOS PRIMARY selection bug by removing focus from entries before destroy
            self.root.focus_set()
            settings_win.destroy()
            self.settings_win = None
            
        settings_win.protocol("WM_DELETE_WINDOW", on_close)
        
        padding_frame = ttk.Frame(settings_win, padding="20")
        padding_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(padding_frame, text="Connection Mode:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        mode_var = tk.StringVar(master=settings_win, value=config.get("mode", "none"))
        modes = [("No Hardware (Desktop Only)", "none"), ("Serial Port (USB/SPP)", "serial"), ("Bluetooth LE (BLE)", "ble")]
        for text, mode in modes:
            ttk.Radiobutton(padding_frame, text=text, value=mode, variable=mode_var).pack(anchor="w")
            
        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(padding_frame, text="Serial Settings (if Serial mode):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        serial_frame = ttk.Frame(padding_frame)
        serial_frame.pack(fill="x")
        ttk.Label(serial_frame, text="Port:").pack(side="left")
        
        port_var = tk.StringVar(master=settings_win, value=config.get("serial_port", "COM3"))
        ttk.Entry(serial_frame, textvariable=port_var, width=8).pack(side="left", padx=5)
        
        ttk.Label(serial_frame, text="Baud:").pack(side="left", padx=(10, 0))
        baud_var = tk.StringVar(master=settings_win, value=str(config.get("serial_baudrate", "115200")))
        ttk.Entry(serial_frame, textvariable=baud_var, width=8).pack(side="left", padx=5)

        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(padding_frame, text="BLE Settings (if BLE mode):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        ble_frame = ttk.Frame(padding_frame)
        ble_frame.pack(fill="x")
        ttk.Label(ble_frame, text="Name/MAC:").pack(side="left")
        
        ble_var = tk.StringVar(master=settings_win, value=config.get("ble_name", "AgyPet"))
        ble_cb = ttk.Combobox(ble_frame, textvariable=ble_var, values=[config.get("ble_name", "AgyPet")])
        ble_cb.pack(side="left", fill="x", expand=True, padx=5)
        
        scan_btn = ttk.Button(ble_frame, text="Scan", width=6)
        scan_btn.pack(side="left")
        
        def do_scan():
            scan_btn.config(text="...", state="disabled")
            def _bg_scan():
                async def scan():
                    devices = await BleakScanner.discover(timeout=3.0, return_adv=True)
                    results = []
                    for addr, (d, adv) in devices.items():
                        name = d.name or 'Unknown'
                        # Check if device broadcasts AgyPet UUID
                        if '4fafc201-1fb5-459e-8fcc-c5c9c331914b' in adv.service_uuids:
                            name = f"✅ [AgyPet] {name}"
                            
                        # Format the UUIDs for display to help identify unknown devices
                        uuid_str = ""
                        if adv.service_uuids:
                            short_uuids = [(u.split('-')[0].lstrip('0') or '0') for u in adv.service_uuids]
                            uuid_str = f" [UUID: {','.join(short_uuids)}]"
                            
                        results.append(f"{name} ({d.address}){uuid_str}")
                    
                    # Sort so that AgyPet devices appear at the top
                    results.sort(key=lambda x: (0 if "✅ [AgyPet]" in x else 1, x))
                    return results
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                names = loop.run_until_complete(scan())
                loop.close()
                self.root.after(0, _scan_done, names)
            threading.Thread(target=_bg_scan, daemon=True).start()
            
        def _scan_done(names):
            scan_btn.config(text="Scan", state="normal")
            if names:
                unique_names = list(set(names))
                ble_cb['values'] = unique_names
                if unique_names:
                    ble_cb.set(unique_names[0])
            else:
                messagebox.showinfo("Scan", "No devices found.", parent=settings_win)

        scan_btn.config(command=do_scan)
        
        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(padding_frame, text="Log Directory (Brain Dir):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        dir_frame = ttk.Frame(padding_frame)
        dir_frame.pack(fill="x")
        
        dir_var = tk.StringVar(master=settings_win, value=config.get("brain_dir", ""))
        ttk.Entry(dir_frame, textvariable=dir_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        from tkinter import filedialog
        def browse_dir():
            d = filedialog.askdirectory(parent=settings_win, initialdir=dir_var.get())
            if d:
                dir_var.set(os.path.normpath(d))
                
        ttk.Button(dir_frame, text="Browse", width=8, command=browse_dir).pack(side="left")
        
        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(padding_frame, text="Volume:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        vol_frame = ttk.Frame(padding_frame)
        vol_frame.pack(fill="x")
        
        vol_var = tk.DoubleVar(master=settings_win, value=config.get("volume", 1.0))
        
        def on_vol_change(val):
            pygame.mixer.music.set_volume(float(val))
            
        vol_scale = ttk.Scale(vol_frame, from_=0.0, to=1.0, variable=vol_var, command=on_vol_change)
        vol_scale.pack(side="left", fill="x", expand=True)
        
        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(padding_frame, text="Voice Profile (称呼方案):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        voice_frame = ttk.Frame(padding_frame)
        voice_frame.pack(fill="x")
        
        voice_var = tk.StringVar(master=settings_win, value=config.get("voice_profile", "baba"))
        voice_profiles = {
            "爸爸 (Papa)": "baba",
            "妈妈 (Mama)": "mama",
            "主人 (Master)": "zhuren",
            "老板 (Boss)": "laoban",
            "哥哥 (Brother)": "gege",
            "宝宝 (Honey)": "baobao",
            "董事长大人 (Chairman)": "dongshizhang",
            "国主陛下 (Monarch)": "guozhu",
            "皇上 (Emperor)": "huangshang"
        }
        voice_reverse = {v: k for k, v in voice_profiles.items()}
        
        voice_display_var = tk.StringVar(master=settings_win, value=voice_reverse.get(voice_var.get(), "爸爸 (Papa)"))
        voice_cb = ttk.Combobox(voice_frame, textvariable=voice_display_var, values=list(voice_profiles.keys()), state="readonly")
        voice_cb.pack(side="left", fill="x", expand=True)
        
        def on_voice_selected(event):
            selected_display = voice_display_var.get()
            voice_var.set(voice_profiles.get(selected_display, "baba"))
            
        voice_cb.bind("<<ComboboxSelected>>", on_voice_selected)
        
        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(padding_frame, text="Webhook URL (Optional):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        hook_frame = ttk.Frame(padding_frame)
        hook_frame.pack(fill="x")
        
        hook_var = tk.StringVar(master=settings_win, value=config.get("http_hook", ""))
        ttk.Entry(hook_frame, textvariable=hook_var).pack(side="left", fill="x", expand=True)

        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(padding_frame, text="Water Reminder Times (喝水提醒时间):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        water_frame = ttk.Frame(padding_frame)
        water_frame.pack(fill="x")
        ttk.Label(water_frame, text="24-Hour times (e.g. 10:30, 15:00):").pack(side="left")
        
        water_times_var = tk.StringVar(master=settings_win, value=config.get("water_times", "10:30, 15:00"))
        ttk.Entry(water_frame, textvariable=water_times_var).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        def save_and_close():
            config["mode"] = mode_var.get()
            config["serial_port"] = port_var.get()
            try:
                config["serial_baudrate"] = int(baud_var.get())
            except:
                pass
            config["ble_name"] = ble_var.get()
            config["brain_dir"] = dir_var.get()
            config["volume"] = vol_var.get()
            config["voice_profile"] = voice_var.get()
            config["http_hook"] = hook_var.get().strip()
            config["water_times"] = water_times_var.get().strip()

            config["settings_x"] = settings_win.winfo_x()
            config["settings_y"] = settings_win.winfo_y()
            save_config(config)
            
            if self.sender:
                self.sender.close()
                self.sender = None
            
            from pet_sender import SerialPetSender, BLEPetSender
            if config["mode"] == "serial":
                self.sender = SerialPetSender(port=config["serial_port"], baudrate=config["serial_baudrate"])
            elif config["mode"] == "ble":
                self.sender = BLEPetSender(ble_name=config["ble_name"])
            else:
                self.sender = None
                self.canvas.itemconfig(self.conn_status_item, text="")
                
            if self.sender:
                self.sender.set_status_callback(self.on_connection_status)
                
            if self.sender and self.current_state:
                self.sender.send_state(self.current_state)
                self._last_sent_state = self.current_state
                
            messagebox.showinfo("Saved", "Settings saved and applied successfully!", parent=settings_win)
            # Fix macOS PRIMARY selection bug
            self.root.focus_set()
            settings_win.destroy()
            self.settings_win = None
            
        ttk.Separator(padding_frame, orient='horizontal').pack(fill='x', pady=10)
        about_frame = ttk.Frame(padding_frame)
        about_frame.pack(fill="x", pady=5)
        ttk.Label(about_frame, text="About AgyPet", font=("Segoe UI", 10, "bold")).pack(anchor="center", pady=(0, 5))
        ttk.Label(about_frame, text="Version: v0.1.2", font=("Segoe UI", 9)).pack(anchor="center")
        ttk.Label(about_frame, text="Author: aning35", font=("Segoe UI", 9)).pack(anchor="center")
        
        def open_github(event):
            import webbrowser
            webbrowser.open("https://github.com/aning35/agy-pet")
            
        link = tk.Label(about_frame, text="GitHub: https://github.com/aning35/agy-pet", font=("Segoe UI", 9, "underline"), fg="#5E81AC", bg="#ECEFF4", cursor="hand2")
        link.pack(anchor="center")
        link.bind("<Button-1>", open_github)

        save_btn = tk.Button(padding_frame, text="Save & Apply", command=save_and_close, font=("Segoe UI", 11, "bold"), fg="#2E3440", bg="#8FBCBB", relief="raised", cursor="hand2")
        save_btn.pack(pady=(10, 20), fill="x", ipady=4)

        # Let tkinter calculate required dimensions
        settings_win.update_idletasks()
        req_width = max(480, settings_win.winfo_reqwidth())
        req_height = settings_win.winfo_reqheight()
        
        # Apply the exact calculated geometry
        if settings_x != -1 and settings_y != -1:
            settings_win.geometry(f"{req_width}x{req_height}+{settings_x}+{settings_y}")
        else:
            settings_win.geometry(f"{req_width}x{req_height}")

    def start_move(self, event):
        if self.is_docked:
            self.dock_start_x = event.x_root
            self.dock_start_y = event.y_root
        else:
            self.drag_offset_x = event.x_root - getattr(self, 'current_win_x', self.root.winfo_x())
            self.drag_offset_y = event.y_root - getattr(self, 'current_win_y', self.root.winfo_y())
            # Track when we last undocked to prevent immediate re-docking
            self.last_undock_time = getattr(self, 'last_undock_time', 0)

    def stop_move(self, event):
        if self.is_docked:
            self.dock_start_x = None
            self.dock_start_y = None
            return
            
        # Prevent immediate re-docking if we just undocked
        if time.time() - getattr(self, 'last_undock_time', 0) < 0.5:
            return
            
        # Check for docking using internal tracked coordinates to bypass Tkinter async geometry lag
        screen_w = self.root.winfo_screenwidth()
        
        win_x = getattr(self, 'current_win_x', self.root.winfo_x())
        win_y = getattr(self, 'current_win_y', self.root.winfo_y())
        
        # Only support edge docking on Windows as requested
        if sys.platform != "win32":
            return
            
        if win_x <= self.dock_threshold:
            self.dock_to_edge("left")
        elif win_x + self.width >= screen_w - self.dock_threshold:
            self.dock_to_edge("right")
        elif win_y <= self.dock_threshold:
            self.dock_to_edge("top")

    def do_move(self, event):
        if self.is_docked:
            if self.dock_start_x is not None and self.dock_start_y is not None:
                dx = event.x_root - self.dock_start_x
                dy = event.y_root - self.dock_start_y
                
                # Check if moved far enough to undock
                if (self.dock_edge == "left" and dx > 60) or \
                   (self.dock_edge == "right" and dx < -60) or \
                   (self.dock_edge == "top" and dy > 60):
                    self.undock(event.x_root, event.y_root)
            return

        x = event.x_root - self.drag_offset_x
        y = event.y_root - self.drag_offset_y
        
        # Prevent hiding completely off-screen left/right/top/bottom
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # Leave at least 30 pixels visible so it can be grabbed again
        if x < -self.width + 30:
            x = -self.width + 30
        elif x > screen_w - 30:
            x = screen_w - 30
            
        if y < 0:
            y = 0
        elif y > screen_h - 30:
            y = screen_h - 30

        self.current_win_x = x
        self.current_win_y = y
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def dock_to_edge(self, edge):
        self.is_docked = True
        self.dock_edge = edge
        self.undocked_geometry = self.root.geometry()
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # 1. Update geometry first to let the window resize
        if edge == "left":
            self.root.geometry(f"{self.bar_thickness}x{screen_h}+0+0")
        elif edge == "right":
            self.root.geometry(f"{self.bar_thickness}x{screen_h}+{screen_w - self.bar_thickness}+0")
        elif edge == "top":
            self.root.geometry(f"{screen_w}x{self.bar_thickness}+0+0")
            
        # Force geometry configuration to process
        self.root.update_idletasks()
        
        # 2. Hide pill elements
        for item in self.canvas.find_all():
            self.canvas.itemconfigure(item, state="hidden")
            
        if self.current_anim:
            self.current_anim.stop()
            
        # 3. Create dock bar on the resized canvas
        if edge == "left":
            self.dock_bar = self.canvas.create_rectangle(0, 0, self.bar_thickness, screen_h, fill="#A6DA95", outline="", tag="dock_bar")
        elif edge == "right":
            self.dock_bar = self.canvas.create_rectangle(0, 0, self.bar_thickness, screen_h, fill="#A6DA95", outline="", tag="dock_bar")
        elif edge == "top":
            self.dock_bar = self.canvas.create_rectangle(0, 0, screen_w, self.bar_thickness, fill="#A6DA95", outline="", tag="dock_bar")
            
        self.update_dock_color(self.current_state)
        self.root.update() # Force DWM repaint

    def undock(self, mouse_x, mouse_y):
        self.is_docked = False
        self.dock_edge = None
        
        # Center the restored window around the mouse pointer
        new_x = mouse_x - self.width // 2
        new_y = mouse_y - self.height // 2
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # Ensure new position does not trigger immediate dock again (padding)
        if new_x <= self.dock_threshold:
            new_x = self.dock_threshold + 5
        elif new_x >= screen_w - self.width - self.dock_threshold:
            new_x = screen_w - self.width - self.dock_threshold - 5
            
        if new_y <= self.dock_threshold:
            new_y = self.dock_threshold + 5
            
        # Prevent off-screen completely
        if new_y > screen_h - self.height:
            new_y = screen_h - self.height
            
        self.current_win_x = new_x
        self.current_win_y = new_y
        self.drag_offset_x = mouse_x - new_x
        self.drag_offset_y = mouse_y - new_y
        self.last_undock_time = time.time()
        
        # === NUCLEAR REBUILD ===
        # After prolonged docking (window at 6px height for 10+ minutes), 
        # Windows DWM discards the rendering surface for the tiny window.
        # Simply restoring geometry and toggling item states is NOT enough.
        # We must:
        # 1. withdraw() + deiconify() to force Windows to recreate the window surface
        # 2. Delete ALL canvas items and recreate them from scratch
        # 3. Force a full update_appearance with GIF reload
        
        # Step 1: Force window surface recreation
        self.root.withdraw()
        self.root.geometry(f"{self.width}x{self.height}+{new_x}+{new_y}")
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.update_idletasks()
        
        # Step 2: Destroy and rebuild all canvas content
        self._rebuild_canvas_content()
        
        # Step 3: Force full visual rebuild (GIF + text)
        saved_state = self.current_state or AntigravityState.IDLE
        self.current_state = None
        self.update_appearance(saved_state, "Restored from dock", force_silent=True)
        
        # Step 4: Final full repaint
        self.root.update()

    def _rebuild_canvas_content(self):
        """Delete all canvas items and recreate them from scratch.
        This is the nuclear option for recovering from DWM rendering surface loss."""
        # Stop any running animation
        if self.current_anim:
            self.current_anim.stop()
            self.current_anim = None
        
        # Delete everything
        self.canvas.delete("all")
        
        # Recreate rounded pill background
        self.draw_rounded_rect(0, 0, self.width, self.height, radius=16, fill=self.bg_color)
        
        # Recreate drag grip
        grip_color = "#5B6078"
        for i in range(3):
            y = 22 + i*8
            self.canvas.create_oval(12, y, 15, y+3, fill=grip_color, outline="")
            self.canvas.create_oval(18, y, 21, y+3, fill=grip_color, outline="")
        
        # Recreate pet image holder
        self.pet_image_item = self.canvas.create_image(45, 32, anchor="center")
        
        # Recreate text labels
        self.status_item = self.canvas.create_text(75, 20, text="IDLE", font=("Segoe UI", 12, "bold"), fill="#A6DA95", anchor="w")
        self.detail_item = self.canvas.create_text(75, 42, text="Startup", font=("Segoe UI", 9), fill="#8AADF4", anchor="w")
        
        # Recreate close button and connection status
        self.close_item = self.canvas.create_text(self.width - 15, 15, text="✖", font=("Segoe UI", 10, "bold"), fill="#ED8796", activefill="#F5BDE6")
        self.conn_status_item = self.canvas.create_text(self.width - 15, 45, text="", font=("Segoe UI", 8, "bold"), anchor="e")

    def update_dock_color(self, state):
        if state == AntigravityState.THINKING:
            color = "#7497DE"
        elif state == AntigravityState.WAITING_CONFIRM:
            color = "#D4BD8C"
        elif state == AntigravityState.ERROR:
            color = "#D47785"
        else: # IDLE
            color = "#91C282"
            
        if self.canvas.find_withtag("dock_bar"):
            self.canvas.itemconfig("dock_bar", fill=color)

    def play_sound(self, file_path):
        try:
            if os.path.exists(file_path):
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
        except Exception as e:
            print(f"Play error: {e}")

    def update_appearance(self, state, detail, force_silent=False):
        base_dir = get_base_dir()
        if state != self.current_state:
            # Check for fireworks trigger: transition from working state to IDLE
            if not force_silent and state == AntigravityState.IDLE and self.current_state in [AntigravityState.THINKING, AntigravityState.WAITING_CONFIRM]:
                self.show_fireworks()

            # Play Sound
            if not force_silent:
                config = load_config()
                voice_profile = config.get("voice_profile", "baba")
                if state == AntigravityState.IDLE and self.current_state is not None:
                    self.play_sound(os.path.join(base_dir, "assets", "sounds", voice_profile, "idle.mp3"))
                elif state == AntigravityState.THINKING:
                    self.play_sound(os.path.join(base_dir, "assets", "sounds", voice_profile, "thinking.mp3"))
                elif state == AntigravityState.WAITING_CONFIRM:
                    self.play_sound(os.path.join(base_dir, "assets", "sounds", voice_profile, "waiting.mp3"))
                elif state == AntigravityState.ERROR:
                    self.play_sound(os.path.join(base_dir, "assets", "sounds", voice_profile, "error.mp3"))
                
            # Change GIF Animation
            if self.current_anim:
                self.current_anim.stop()
                
            state_to_gif = {
                AntigravityState.IDLE: "idle.gif",
                AntigravityState.THINKING: "thinking.gif",
                AntigravityState.WAITING_CONFIRM: "waiting.gif",
                AntigravityState.ERROR: "error.gif"
            }
            gif_filename = state_to_gif.get(state, "idle.gif")
            gif_path = os.path.join(base_dir, "assets", "gifs", gif_filename)
            
            # Start new animation (250ms per frame)
            self.current_anim = AnimatedGif(self.canvas, self.pet_image_item, gif_path, delay=250)
            if not self.is_docked:
                self.current_anim.start()
            
            # Stats updates
            if state == AntigravityState.ERROR and self.current_state != AntigravityState.ERROR:
                self.stats["errors"] += 1
                self.save_stats()
            
            if self.current_state == AntigravityState.THINKING and self.last_think_start:
                self.stats["thinking_time"] += (time.time() - self.last_think_start)
                self.save_stats()
                
            if state == AntigravityState.THINKING:
                self.last_think_start = time.time()
            else:
                self.last_think_start = None
                
            self.current_state = state
            
            if self.is_docked:
                self.update_dock_color(state)
            
            if state == AntigravityState.THINKING:
                self.thinking_start_time = time.time()
            else:
                self.thinking_start_time = None

        # Text and Colors
        state_mapping = {
            AntigravityState.IDLE: {"text": "IDLE", "color": "#A6DA95"},
            AntigravityState.THINKING: {"text": "THINKING", "color": "#8AADF4"},
            AntigravityState.WAITING_CONFIRM: {"text": "WAITING", "color": "#EED49F"},
            AntigravityState.ERROR: {"text": "ERROR", "color": "#ED8796"}
        }
        config = state_mapping.get(state, {"text": "UNKNOWN", "color": "#CAD3F5"})
        
        self.canvas.itemconfig(self.status_item, text=config["text"], fill=config["color"])
        
        # truncate detail
        short_detail = detail[:22] + "..." if len(detail) > 22 else detail
        self.canvas.itemconfig(self.detail_item, text=short_detail)
        
        # Uptime Tracker
        now = time.time()
        self.stats["uptime"] = now - self.session_start

    def show_fireworks(self):
        base_dir = get_base_dir()
        gif_path = os.path.join(base_dir, "assets", "gifs", "fireworks.gif")
        if not os.path.exists(gif_path): 
            return
            
        # Play idle sound for fireworks feeling or default idle sound
        config = load_config()
        voice_profile = config.get("voice_profile", "baba")
        self.play_sound(os.path.join(base_dir, "assets", "sounds", voice_profile, "idle.mp3"))
        
        # Spawn independent process for fireworks to bypass macOS Toplevel transparency bugs
        import subprocess
        import sys
        if getattr(sys, 'frozen', False):
            # If frozen, sys.executable is the app itself
            subprocess.Popen([sys.executable, "--fireworks"])
        else:
            # If not frozen, use python to run app.py
            app_script = os.path.join(base_dir, "app.py")
            if not os.path.exists(app_script):
                app_script = os.path.join(base_dir, "src", "app.py")
            subprocess.Popen([sys.executable, app_script, "--fireworks"])
        
    def _cleanup_fireworks(self):
        if hasattr(self, 'fw_win') and self.fw_win:
            self.fw_win.destroy()
            self.fw_win = None
            self.fw_anim = None

    def update_ui(self):
        try:
            while True:
                state, reason = self.state_queue.get_nowait()
                self.update_appearance(state, reason)
        except queue.Empty:
            pass
        finally:
            if self.current_state == AntigravityState.THINKING and hasattr(self, 'thinking_start_time') and self.thinking_start_time:
                if time.time() - self.thinking_start_time >= 120:
                    base_dir = get_base_dir()
                    config = load_config()
                    voice_profile = config.get("voice_profile", "baba")
                    self.play_sound(os.path.join(base_dir, "assets", "sounds", voice_profile, "thinking_long.mp3"))
                    self.thinking_start_time = time.time()
            self.root.after(100, self.update_ui)

    def schedule_canvas_heal(self):
        """Periodically force-redraw all canvas items to recover from DWM transparency glitches.
        On Windows, the Desktop Window Manager can sometimes 'lose' rendered pixels
        on transparent-color windows, causing text/images to become invisible.
        This method forces Tkinter to re-submit all canvas pixels."""
        try:
            if not self.is_docked:
                now = time.time()
                if now - self._last_canvas_heal >= self._canvas_heal_interval:
                    self._last_canvas_heal = now
                    self._force_canvas_redraw()
        except Exception as e:
            print(f"Canvas heal error: {e}")
        self.root.after(5000, self.schedule_canvas_heal)

    def _force_canvas_redraw(self):
        """Force a full canvas redraw by briefly nudging the window geometry.
        This causes DWM to re-composite the window and Tkinter to repaint all items."""
        try:
            # Get current position
            geo = self.root.geometry()
            # Force Tkinter to re-render the canvas by toggling all items
            for item in self.canvas.find_all():
                current_state = self.canvas.itemcget(item, "state")
                if current_state != "hidden":
                    self.canvas.itemconfigure(item, state="hidden")
                    self.canvas.itemconfigure(item, state="normal")
            # Force geometry update cycle
            self.root.update_idletasks()
        except Exception:
            pass

    def on_state_change(self, new_state, reason):
        self.state_queue.put((new_state, reason))
        if self._last_sent_state != new_state:
            if self.sender:
                self.sender.send_state(new_state)
            
            # Fire webhook if configured
            config = load_config()
            hook_url = config.get("http_hook", "")
            if hook_url:
                def _send_hook():
                    try:
                        import urllib.request
                        import json
                        payload = json.dumps({
                            "state_code": new_state,
                            "state_name": {1: "IDLE", 2: "THINKING", 3: "WAITING_CONFIRM", 4: "ERROR"}.get(new_state, "UNKNOWN"),
                            "reason": reason
                        }).encode('utf-8')
                        req = urllib.request.Request(hook_url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
                        # Bypass system proxy (e.g. Clash) to ensure localhost webhooks work
                        handler = urllib.request.ProxyHandler({})
                        opener = urllib.request.build_opener(handler)
                        opener.open(req, timeout=2.0)
                    except Exception:
                        pass # Ignore HTTP errors
                threading.Thread(target=_send_hook, daemon=True).start()
                
            self._last_sent_state = new_state

    def background_task(self):
        config = load_config()
        brain_dir = config.get("brain_dir", "")
        log_file = get_latest_conversation_log(brain_dir)

        event_handler = LogHandler(callback=self.on_state_change)
        observer = Observer()
        
        try:
            if log_file:
                event_handler.set_file(log_file)
                observer.schedule(event_handler, os.path.dirname(log_file), recursive=False)
                observer.start()
            else:
                self.state_queue.put((AntigravityState.ERROR, "No logs found"))
        except Exception as e:
            print(f"[-] Error initializing log observer: {e}")
            self.state_queue.put((AntigravityState.ERROR, f"Observer init error: {e}"))

        try:
            while True:
                try:
                    time.sleep(5)
                    config = load_config()
                    brain_dir = config.get("brain_dir", "")
                    latest_log = get_latest_conversation_log(brain_dir)
                    
                    if latest_log and latest_log != event_handler.current_file:
                        event_handler.set_file(latest_log)
                        if observer.is_alive():
                            try:
                                observer.unschedule_all()
                            except Exception:
                                pass
                        else:
                            try:
                                observer.start()
                            except Exception:
                                pass
                        
                        try:
                            observer.schedule(event_handler, os.path.dirname(latest_log), recursive=False)
                        except Exception as e:
                            print(f"[-] Error scheduling observer watch: {e}")
                except Exception as e:
                    print(f"[-] Error in background task loop: {e}")
                    time.sleep(2)
        finally:
            try:
                if observer.is_alive():
                    observer.stop()
                    observer.join()
            except Exception:
                pass

    def start_background_listener(self):
        t = threading.Thread(target=self.background_task, daemon=True)
        t.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopPetUI(root)
    root.mainloop()

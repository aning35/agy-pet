import json
import os
import sys

def get_config_path():
    if getattr(sys, 'frozen', False):
        # If running as an EXE compiled by PyInstaller
        base_dir = os.path.dirname(sys.executable)
    else:
        # If running as a normal Python script (from src/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config.json")

DEFAULT_CONFIG = {
    "mode": "none", # none, serial, ble
    "serial_port": "COM3",
    "serial_baudrate": 115200,
    "ble_name": "AgyPet",
    "brain_dir": r"C:\Users\Administrator\.gemini\antigravity\brain",
    "voice_profile": "baba",
    "settings_x": -1,
    "settings_y": -1
}

def load_config():
    config_file = get_config_path()
    if not os.path.exists(config_file):
        return DEFAULT_CONFIG.copy()
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    config_file = get_config_path()
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

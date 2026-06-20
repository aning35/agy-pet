import os
import sys
import platform

APP_NAME = "AgyPet"

def get_executable_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        script_path = os.path.abspath(sys.argv[0])
        return f"{sys.executable} {script_path}"

def set_autostart(enable: bool):
    system = platform.system()
    exec_path = get_executable_path()
    
    if system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if enable:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exec_path)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error setting autostart on Windows: {e}")

    elif system == "Darwin": # macOS
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.aning35.{APP_NAME.lower()}.plist")
        if enable:
            # Detect .app bundle path for frozen builds
            if getattr(sys, 'frozen', False):
                # sys.executable is like /path/to/AgyPet.app/Contents/MacOS/AgyPet
                exe = sys.executable
                # Walk up to find the .app bundle
                app_bundle = None
                path = exe
                while path and path != "/":
                    if path.endswith(".app"):
                        app_bundle = path
                        break
                    path = os.path.dirname(path)
                
                if app_bundle:
                    # Use 'open -a' to launch the .app bundle properly
                    program_arguments = f"""
        <string>open</string>
        <string>-a</string>
        <string>{app_bundle}</string>"""
                else:
                    # Fallback: direct executable
                    program_arguments = f"\n        <string>{exe}</string>"
            else:
                program_arguments = f"\n        <string>{sys.executable}</string>\n        <string>{os.path.abspath(sys.argv[0])}</string>"

            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aning35.{APP_NAME.lower()}</string>
    <key>ProgramArguments</key>
    <array>{program_arguments}
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            with open(plist_path, "w") as f:
                f.write(plist_content)
        else:
            if os.path.exists(plist_path):
                try:
                    os.remove(plist_path)
                except Exception as e:
                    print(f"Error removing macOS autostart: {e}")

    elif system == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, f"{APP_NAME.lower()}.desktop")
        
        if enable:
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_content = f"""[Desktop Entry]
Type=Application
Exec={exec_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name={APP_NAME}
Comment=Start {APP_NAME} on login
"""
            with open(desktop_file, "w") as f:
                f.write(desktop_content)
        else:
            if os.path.exists(desktop_file):
                try:
                    os.remove(desktop_file)
                except Exception as e:
                    print(f"Error removing Linux autostart: {e}")

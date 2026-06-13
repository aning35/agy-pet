import time
import os
from watchdog.observers import Observer
from colorama import init, Fore, Style
import argparse

from state_parser import LogHandler, AntigravityState, get_latest_conversation_log, BRAIN_DIR
from pet_sender import SerialPetSender, BLEPetSender

# Initialize colorama for Windows console colors
init()

def main():
    parser = argparse.ArgumentParser(description="Antigravity Pet State Bridge")
    parser.add_argument("--mode", choices=["serial", "ble"], default="serial", help="Connection mode: 'serial' or 'ble'")
    parser.add_argument("--port", default="COM3", help="COM port for Serial mode")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baudrate for Serial mode")
    parser.add_argument("--ble-name", default="AgyPet", help="Target Bluetooth device name for BLE mode")
    args = parser.parse_args()

    print(Fore.CYAN + "=== Antigravity IDE Desktop Pet Bridge ===" + Style.RESET_ALL)
    
    # 1. Initialize Serial/Bluetooth sender
    if args.mode == "ble":
        print(Fore.CYAN + f"[*] Starting in BLE Mode (Target: {args.ble_name})" + Style.RESET_ALL)
        sender = BLEPetSender(ble_name=args.ble_name)
    else:
        print(Fore.CYAN + f"[*] Starting in Serial Mode (Port: {args.port})" + Style.RESET_ALL)
        sender = SerialPetSender(port=args.port, baudrate=args.baudrate)
        
    current_state = None

    def on_state_change(new_state, reason):
        nonlocal current_state
        # Only broadcast if state actually changes, to avoid spamming the ESP32
        if new_state != current_state:
            state_str = AntigravityState.to_string(new_state)
            print(Fore.MAGENTA + f"[STATE CHANGE] {state_str} (Reason: {reason})" + Style.RESET_ALL)
            sender.send_state(new_state)
            current_state = new_state

    # 2. Find the latest log file
    log_file = get_latest_conversation_log()
    if not log_file:
        print(Fore.RED + "[-] Could not find any Antigravity conversation logs. Are you running the IDE?" + Style.RESET_ALL)
        return

    # 3. Setup Watchdog Observer
    event_handler = LogHandler(callback=on_state_change)
    event_handler.set_file(log_file)
    
    # We monitor the directory containing the log file
    log_dir = os.path.dirname(log_file)
    observer = Observer()
    observer.schedule(event_handler, log_dir, recursive=False)
    observer.start()

    print(Fore.GREEN + f"[*] Listening for Antigravity AI state changes... (Press Ctrl+C to stop)" + Style.RESET_ALL)
    
    # Set initial state
    on_state_change(AntigravityState.IDLE, "Startup")

    try:
        while True:
            # Periodically check if a newer conversation was started
            time.sleep(5)
            latest_log = get_latest_conversation_log()
            if latest_log and latest_log != event_handler.current_file:
                print(Fore.YELLOW + f"[*] New conversation detected. Switching to: {latest_log}" + Style.RESET_ALL)
                event_handler.set_file(latest_log)
                
                # Unschedule old and schedule new
                observer.unschedule_all()
                observer.schedule(event_handler, os.path.dirname(latest_log), recursive=False)
                
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[*] Stopping service..." + Style.RESET_ALL)
        observer.stop()
    
    observer.join()
    sender.close()

if __name__ == "__main__":
    main()

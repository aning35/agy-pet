import serial
import time
import threading
import asyncio
import queue
from colorama import Fore, Style

try:
    from bleak import BleakClient, BleakScanner
    BLE_AVAILABLE = True
except ImportError:
    BLE_AVAILABLE = False

import logging
import os
import sys

# Configure dedicated hardware logger (won't pollute bleak/other libs)
if getattr(sys, 'frozen', False):
    _log_dir = os.path.expanduser("~/.agypet")
    os.makedirs(_log_dir, exist_ok=True)
else:
    _log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = os.path.join(_log_dir, "agypet_hardware.log")

hw_logger = logging.getLogger("agypet.hardware")
hw_logger.setLevel(logging.INFO)
if not hw_logger.handlers:
    _fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    _fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    hw_logger.addHandler(_fh)

class BasePetSender:
    def __init__(self):
        self.status_callback = None
        self.current_mode = "NONE"
        self.is_connected = False
        
    def set_status_callback(self, callback):
        self.status_callback = callback
        self._update_status(self.current_mode, self.is_connected)
        
    def _update_status(self, mode, is_connected, message=""):
        self.current_mode = mode
        self.is_connected = is_connected
        if self.status_callback:
            self.status_callback(mode, is_connected, message)
            
    def send_state(self, state_code: int):
        pass
    def close(self):
        pass

class SerialPetSender(BasePetSender):
    def __init__(self, port="COM3", baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            msg = f"Connected to Serial Pet on {self.port} at {self.baudrate} baud"
            print(Fore.GREEN + f"[+] {msg}" + Style.RESET_ALL)
            hw_logger.info(msg)
            self._update_status("COM", True, "Connected")
            time.sleep(2) # Wait for ESP32 to reset if using USB
        except serial.SerialException as e:
            msg = f"Failed to connect to {self.port}: {e}"
            print(Fore.RED + f"[-] {msg}" + Style.RESET_ALL)
            hw_logger.error(msg)
            print(Fore.YELLOW + f"[*] Running in simulation mode." + Style.RESET_ALL)
            self.ser = None
            self._update_status("COM", False, str(e))

    def send_state(self, state_code: int):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(bytes([state_code]))
            except serial.SerialException as e:
                msg = f"Serial Error: {e}"
                print(Fore.RED + f"[-] {msg}" + Style.RESET_ALL)
                hw_logger.error(msg)
                self.ser.close()
                self.ser = None
                self._update_status("COM", False, msg)

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(Fore.GREEN + "[+] Serial Connection closed." + Style.RESET_ALL)

# Standard ESP32 BLE UUIDs
DEFAULT_SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
DEFAULT_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class BLEPetSender(BasePetSender):
    def __init__(self, ble_name="AgyPet"):
        super().__init__()
        if not BLE_AVAILABLE:
            print(Fore.RED + "[-] 'bleak' library not found. Please pip install bleak." + Style.RESET_ALL)
            return
            
        self.ble_identifier = ble_name
        self.msg_queue = queue.Queue()
        self.running = True
        self._update_status("BLE", False)
        
        # Start the asyncio event loop in a separate background thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._ble_task())

    async def _ble_task(self):
        import re
        mac_match = re.search(r'\((([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))\)', self.ble_identifier)
        target_mac = mac_match.group(1).upper() if mac_match else None
        
        client = None
        
        def handle_disconnect(_):
            msg = "BLE Device disconnected. Reconnecting..."
            print(Fore.YELLOW + f"[-] {msg}" + Style.RESET_ALL)
            hw_logger.warning(msg)
            self._update_status("BLE", False, "Disconnected")
            
        while self.running:
            self._update_status("BLE", False, "Scanning...")
            print(Fore.YELLOW + f"[*] Scanning for BLE device '{self.ble_identifier}'..." + Style.RESET_ALL)
            device = None
            try:
                devices = await BleakScanner.discover(timeout=3.0, return_adv=True)
                for addr, (d, adv) in devices.items():
                    if DEFAULT_SERVICE_UUID in adv.service_uuids:
                        device = d
                        break
                    elif target_mac and d.address and d.address.upper() == target_mac:
                        device = d
                        break
                    elif d.name and self.ble_identifier.lower() in d.name.lower():
                        device = d
                        break
            except Exception as e:
                msg = f"Scan Error: {e}"
                print(Fore.RED + f"[-] {msg}" + Style.RESET_ALL)
                hw_logger.error(msg)
                self._update_status("BLE", False, msg)
                    
            if not device:
                # Discard queue so it doesn't pile up while disconnected
                while not self.msg_queue.empty():
                    try:
                        self.msg_queue.get_nowait()
                    except:
                        pass
                await asyncio.sleep(2.0)
                continue
                
            msg = f"Found {device.name} [{device.address}]. Connecting..."
            print(Fore.GREEN + f"[+] {msg}" + Style.RESET_ALL)
            hw_logger.info(msg)
            self._update_status("BLE", False, "Connecting...")
            
            try:
                client = BleakClient(device, disconnected_callback=handle_disconnect, timeout=60.0)
                await client.connect()
                msg = f"Successfully connected to BLE Pet! ({device.address})"
                print(Fore.GREEN + f"[+] {msg}" + Style.RESET_ALL)
                hw_logger.info(msg)
                self._update_status("BLE", True, "Connected")
                
                import time
                last_ping = time.time()
                
                while self.running and client.is_connected:
                    try:
                        state_code = self.msg_queue.get_nowait()
                        try:
                            await client.write_gatt_char(DEFAULT_CHAR_UUID, bytes([state_code]), response=False)
                            hw_logger.info(f"BLE Write (No Resp) OK: {state_code}")
                        except Exception:
                            await client.write_gatt_char(DEFAULT_CHAR_UUID, bytes([state_code]), response=True)
                            hw_logger.info(f"BLE Write (With Resp) OK: {state_code}")
                        last_ping = time.time()
                    except queue.Empty:
                        if time.time() - last_ping > 10.0:
                            try:
                                # Keep-alive ping to prevent Windows dropping the link
                                await client.write_gatt_char(DEFAULT_CHAR_UUID, bytes([0x00]), response=False)
                                last_ping = time.time()
                            except Exception as e:
                                hw_logger.warning(f"BLE Keep-alive ping failed: {e}. Disconnecting...")
                                break
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        msg = f"BLE Write Error: {e}"
                        print(Fore.RED + f"[-] {msg}" + Style.RESET_ALL)
                        hw_logger.error(msg)
                        self._update_status("BLE", True, f"Write error: {e}")
                        await asyncio.sleep(1.0)
                        
                if client.is_connected:
                    await client.disconnect()
            except Exception as e:
                msg = f"BLE Connection Error: {e}"
                print(Fore.RED + f"[-] {msg}" + Style.RESET_ALL)
                hw_logger.error(msg)
                self._update_status("BLE", False, msg)
                await asyncio.sleep(2.0)
            finally:
                if client and client.is_connected:
                    try: await client.disconnect()
                    except: pass

    def send_state(self, state_code: int):
        self.msg_queue.put(state_code)

    def close(self):
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1)
        print(Fore.GREEN + "[+] BLE Sender stopped." + Style.RESET_ALL)

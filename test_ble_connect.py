import asyncio
from bleak import BleakScanner, BleakClient

UUID_SVC = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
UUID_CHR = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

async def main():
    print("=== Bleak Client Connection Test ===")
    print("Scanning for AgyPet-ESP32S3...")
    
    device = await BleakScanner.find_device_by_name("AgyPet-ESP32S3", timeout=10.0)
    if not device:
        print("Device not found!")
        return
        
    print(f"Found: {device.name} [{device.address}]")
    print("Connecting...")
    
    try:
        async with BleakClient(device, timeout=15.0) as client:
            print("Connected!")
            
            # Read to stabilize connection
            val = await client.read_gatt_char(UUID_CHR)
            print(f"Read initial value: {val}")
            
            # Send data
            for state in [0x01, 0x02, 0x03, 0x04]:
                label = {1: "IDLE", 2: "THINKING", 3: "WAITING", 4: "ERROR"}[state]
                print(f"Sending {label} (0x{state:02X})...")
                await client.write_gatt_char(UUID_CHR, bytes([state]), response=True)
                await asyncio.sleep(2.0)
                
            print("=== TEST COMPLETE ===")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

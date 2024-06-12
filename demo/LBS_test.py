import asyncio
from bleak import BleakClient, BleakScanner

# UUIDs for the LED and Button characteristics (blefund_less4_exer2)
LBS_LED_UUID = "00001525-1212-efde-1523-785feabcd123"
LBS_BUTTON_UUID = "00001524-1212-efde-1523-785feabcd123"

# Function to write to the LED characteristic
async def write_led(address, state):
    async with BleakClient(address) as client:
        await client.write_gatt_char(LBS_LED_UUID, bytearray([state]))
        print(f"LED state set to {state}")

# Function to read the Button characteristic
async def read_button(address):
    async with BleakClient(address) as client:
        button_state = await client.read_gatt_char(LBS_BUTTON_UUID)
        print(f"Button state: {int(button_state[0])}")

# Main function to scan for devices and perform read/write operations
async def main():
    devices = await BleakScanner.discover()
    for device in devices:
        print(device)

    address = input("Enter the address of the device you want to connect to: ")
    
    state = int(input("Enter LED state (0 or 1): "))
    await write_led(address, state)
    
    await read_button(address)

if __name__ == "__main__":
    asyncio.run(main())

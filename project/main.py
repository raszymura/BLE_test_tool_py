#!/usr/bin/python3

"""
main.py
CDS Service Test Tool 
-------------
Interactive terminal for BLE Calculator Application with nRF Connect SDK on Nordic Devkit
"""
import asyncio
import sys
import struct
import calculator  # calculator.py

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

SERVICE_UUID = "6e7e652f-0b5d-4de6-bcd9-a071d34c3e9f"
WRITE_UUID   = "448e4b02-b99a-4f57-a76d-d283933c2fd5"
NOTIFY_UUID  = "4d19fe91-2164-49a8-9022-55ba662ce6fc"


async def calculator_terminal():
    """
    This is a simple "terminal" program to use the Calculator Data Service on the Nordic Board.
    It reads operands and operation from stdin and sends data to the device.
    Result received from the device is printed to stdout.
    """
    notify_event = asyncio.Event()
    
    def match_cds_uuid(device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the Calculator Data Service (CDS) UUID in the advertising data.
        if SERVICE_UUID.lower() in adv.service_uuids:
            return True
        return False

    device = await BleakScanner.find_device_by_filter(match_cds_uuid)

    if device is None:
        print("No matching device found, you may need to edit match_cds_uuid().")
        sys.exit(1)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye!")
        # Cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_notification(_: BleakGATTCharacteristic, data: bytearray):
        nonlocal notify_event
        
        if calc.mode == 0:
            result = struct.unpack('f', data)[0]  # Unpack little-endian byte order, [0] retrieves the first (and only) value from the tuple
        elif calc.mode == 1:
            result = struct.unpack('i', data)[0]  # unpack little-endian byte order, [0] retrieves the first (and only) value from the tuple
            result = result / float(1 << 31)
        
        print("--------> Received operation result:", result)
        calc.result = result  # Update result
        notify_event.set()  # Set the event when notification is received
        

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        # Start receiving notifications
        await client.start_notify(NOTIFY_UUID, handle_notification)  # Receive data
        print("Connected!")
        
        cds = client.services.get_service(SERVICE_UUID)
        write_data = cds.get_characteristic(WRITE_UUID)

        calc = calculator.Calculator()
        while True:
            data = calc.run_calculator()
            
            if data == 'mode' or data == 'go_again':
                continue
            if data == 'goodbye':
                break

            await client.write_gatt_char(write_data, data, response=False)  # Send data
            # print("sent:", data)
            
            await notify_event.wait()  # Wait for notification before proceeding to the next iteration
            notify_event.clear()  # Reset the event for the next notification


if __name__ == "__main__":
    try:
        asyncio.run(calculator_terminal())
    except asyncio.CancelledError:
        # Task is cancelled on disconnect, so we ignore this error
        pass

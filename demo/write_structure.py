"""
CDS Service
-------------

An example showing how to send structure

"""

import asyncio
import sys
import struct

from itertools import count, takewhile
from typing import Iterator

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

SERVICE_UUID = "6e7e652f-0b5d-4de6-bcd9-a071d34c3e9f"
WRITE_UUID = "448e4b02-b99a-4f57-a76d-d283933c2fd5"
NOTIFY_UUID = "4d19fe91-2164-49a8-9022-55ba662ce6fc"
# SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
# WRITE_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
# NOTIFY_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# TIP: you can get this function and more from the ``more-itertools`` package.
def sliced(data: bytes, n: int) -> Iterator[bytes]:
    """
    Slices *data* into chunks of size *n*. The last slice may be smaller than
    *n*.
    """
    return takewhile(len, (data[i : i + n] for i in count(0, n)))


async def calculator_terminal():
    """This is a simple "terminal" program that uses the Nordic Semiconductor
    (nRF) UART service. It reads from stdin and sends each line of data to the
    remote device. Any data received from the device is printed to stdout.
    """

    def match_cds_uuid(device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the Calculator Data Service (CDS) UUID in the advertising data.
        if SERVICE_UUID.lower() in adv.service_uuids:
            return True

        return False

    device = await BleakScanner.find_device_by_filter(match_cds_uuid)

    if device is None:
        print("no matching device found, you may need to edit match_cds_uuid().")
        sys.exit(1)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # Cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_notification(_: BleakGATTCharacteristic, data: bytearray):
        print("received:", data)

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(NOTIFY_UUID, handle_notification)

        print("Connected, start typing and press ENTER...")

        loop = asyncio.get_running_loop()
        cds = client.services.get_service(SERVICE_UUID)
        write_data = cds.get_characteristic(WRITE_UUID)

        while True:
            operation = 5         # For example, 1 could represent an addition operation
            q31_operand = 1.23456  # Fixed-point operand
            mode = 0              # 1 for fixed-point, 0 for floating-point
            
            
            # Waits until you type a line and press ENTER.
            # data = await loop.run_in_executor(None, sys.stdin.buffer.readline)
            data = struct.pack('<BfB', operation, q31_operand, mode)  # Convert the values to a byte array
            # data = struct.pack('<BfB', operation, q31_operand, mode)  # Convert the values to a byte array
            # '<BIB': This is the data format which tells the pack function how to pack the values. Here's what it means:
            # '<': Indicates that the data will be packed in little-endian order (the least significant byte is first).
            # B: Means that the first value (operation) will be represented as a single byte.
            # I: Means that the second value (q31_operand) will be represented as a 32-bit unsigned integer.
            #   f: represents a 32-bit floating-point number.
            # B: Means that the third value (mode) will be represented as a single byte.
            
            """
            /* struct template in C */
            struct calculator_task {
                uint8_t operation;
                union {
                    float f_operand;
                    int32_t q31_operand;
                };
                bool mode;
            };
            """
            
            print("send data:")
            print(data)
            await client.write_gatt_char(write_data, data, response=False)

            # if not data: # data will be empty on EOF (e.g. CTRL+D on *nix)
            #     break
            
            # Writing without response requires that the data can fit in a single BLE packet.
            # We use the max_write_without_response_size property (default value of 20)
            # to split the data into chunks that will fit.

            # for s in sliced(data, write_data.max_write_without_response_size):
            #     await client.write_gatt_char(write_data, s, response=False)  # Send data to Nordic
            # Write without response (sometimes called Command)

            print("sent:", data)


if __name__ == "__main__":
    try:
        asyncio.run(calculator_terminal())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
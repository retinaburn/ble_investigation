import sys

# ruff: noqa: E402
sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

async def find_devices():
    devices = {}
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            print("Result: ",result)
            print("Name: ",result.name(), "RSSI:",result.rssi)
            if result.name() not in devices:
                print("adding ", result.name(), result.device)
                devices[result.name()] = result.device
    print("Found: ",devices)
    return devices


async def main():
    devices = await find_devices()

    for device in devices:
        try:
            print("Connecting to", device)
            connection = await devices.get(device).connect()
            print("Services: ", connection.services())
            #await connection.services()._start()
        except asyncio.TimeoutError:
            print("Timeout during connection")
            return

        await asyncio.sleep_ms(1000)
        serviceUUIDs = set()
        async for service in connection.services():
            print("Service: ",service)    
            serviceUUIDs.add(service.uuid)
    # 0x1800 GAP Service
        #0x2a01 BLE_UUID_GAP_CHARACTERISTIC_APPEARANCE
        #0x2a00 BLE_UUID_GAP_CHARACTERISTIC_DEVICE_NAME
        #0x2a03 BLE_UUID_GAP_CHARACTERISTIC_RECONN_ADDR
        #0x2a04 BLE_UUID_GAP_CHARACTERISTIC_PPCP 
    # 0x1801 GATT Service
        #0x2a05 BLE_UUID_GATT_CHARACTERISTIC_SERVICE_CHANGED  
    # 0x180a Device Information Service
        #0x2a26 BLE_UUID_FIRMWARE_REVISION_STRING_CHAR
        #0x2a24 BLE_UUID_MODEL_NUMBER_STRING_CHAR
        #0x2a29 BLE_UUID_MANUFACTURER_NAME_STRING_CHAR
        #0x2a28 BLE_UUID_SOFTWARE_REVISION_STRING_CHAR
        #0x2a27 BLE_UUID_HARDWARE_REVISION_STRING_CHAR
        #0x2a50 BLE_UUID_PNP_ID_CHAR
    # '98186d60-2f47-11e6-8899-0002a5d5c51b'

#     uuid = bluetooth.UUID('98186d60-2f47-11e6-8899-0002a5d5c51b')
#     service = await connection.service(uuid)
#     print("Service:", service)
#     async for char in service.characteristics():
#         print(char)
    
asyncio.run(main())

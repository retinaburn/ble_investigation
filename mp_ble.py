import sys

# ruff: noqa: E402
sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
#_ELLIPTICAL_UUID = bluetooth.UUID(0x3c17ae30)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)


# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

async def find_device():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == "SCHWINN 470":
                print("Result: ",result)
                print("Name: ",result.name(), "RSSI:",result.rssi, "Services: ",result.services(), "Mfg: ",result.manufacturer())
#                 dump(result)
#                 print("Services: ")
#                 dump(result.services())
#                 print ("Device: ")
#                 dump(result.device)

            # See if it matches our name and the environmental sensing service.
            #if result.name() == "SCHWINN 470" and _ENV_SENSE_UUID in result.services():
            if result.name() == "SCHWINN 470":
                return result.device
    return None


async def main():
    device = await find_device()
    if not device:
        print("Device not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
        print("Services: ", connection.services())
        #await connection.services()._start()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    await asyncio.sleep_ms(1000)
    serviceUUIDs = set()
    async for service in connection.services():
        print("Service: ",service)
        #dump(service)
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
    
    print("\nTrying to read\n")
    print("UUIDs: ", serviceUUIDs)
    for uuidString in serviceUUIDs:
        uuid = bluetooth.UUID(uuidString)
        print("uuidString", uuidString,"UUID: ", uuid)
        if uuid in [bluetooth.UUID(0x1801), bluetooth.UUID(0x1800), bluetooth.UUID(0x180a)]:
            print("  Skip")
        else:
            try:
                service = await connection.service(uuid)
                async for char in service.characteristics():
                    print("  ",char)
                    try:
                        result = await char.read(timeout_ms=1000)
                        print("    ", result)
                        await char.write(0)
                    except TypeError:
                        print("    ","??NoneType??") 
                    except ValueError:
                        print("    ","No read")
                    except asyncio.TimeoutError:
                        print("    ","Timeout")
            except TypeError:
                print("  ","??NoneType??") 

    print("\nTrying to write\n")
    for uuidString in serviceUUIDs:
        uuid = bluetooth.UUID(uuidString)
        print("uuidString", uuidString,"UUID: ", uuid)
        if uuid in [bluetooth.UUID(0x1801), bluetooth.UUID(0x1800), bluetooth.UUID(0x180a)]:
            print("  Skip")
        else:
            try:
                service = await connection.service(uuid)
                async for char in service.characteristics():
                    print("  ",char)
                    try:
                        await char.write(0)
                    except TypeError:
                        print("    ","??NoneType??") 
                    except ValueError:
                        print("    ","No read")
                    except asyncio.TimeoutError:
                        print("    ","Timeout")
            except TypeError:
                print("  ","??NoneType??") 

    print("\nTrying to read\n")
    print("UUIDs: ", serviceUUIDs)
    for uuidString in serviceUUIDs:
        uuid = bluetooth.UUID(uuidString)
        print("uuidString", uuidString,"UUID: ", uuid)
        if uuid in [bluetooth.UUID(0x1801), bluetooth.UUID(0x1800), bluetooth.UUID(0x180a)]:
            print("  Skip")
        else:
            try:
                service = await connection.service(uuid)
                async for char in service.characteristics():
                    print("  ",char)
                    try:
                        result = await char.read(timeout_ms=1000)
                        print("    ", result)
                        await char.write(0)
                    except TypeError:
                        print("    ","??NoneType??") 
                    except ValueError:
                        print("    ","No read")
                    except asyncio.TimeoutError:
                        print("    ","Timeout")
            except TypeError:
                print("  ","??NoneType??") 

asyncio.run(main())
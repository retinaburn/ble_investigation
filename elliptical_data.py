import sys
import network
import ntptime
# ruff: noqa: E402
sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
import time
import random
import struct


def read_characteristic(char):
    try:
        print("Try read")
        result = await char.read(timeout_ms=5000)
        print("Read")
        #print("Type: ",type(result))
        if (type(result) == bytes):
            #time.time() + (31557600000 * 30)
            #print("    ",((time.time_ns() // 1_000_000)+(31557600000 * 30))," Read: ","".join("\\x%02x" % i for i in result))
            readTime = ((time.time_ns() // 1_000_000)+(31557600000 * 30))
            readData = "".join("\\x%02x" % i for i in result)
            return (readTime, readData)
        else:
            print("    ",((time.time_ns() // 1_000_000)+(31557600000 * 30))," Read:", result)
    except TypeError as e:
        print("      ","??NoneType??,",e) 
    except ValueError:
        print("      ","No read")
    except asyncio.TimeoutError:
        print("      ","Timeout")

async def find_device():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == "SCHWINN 470":
                print("Result: ",result)
                print("Name: ",result.name(), "RSSI:",result.rssi)

            # See if it matches our name and the environmental sensing service.
            #if result.name() == "SCHWINN 470" and _ENV_SENSE_UUID in result.services():
            if result.name() == "SCHWINN 470":
                return result.device
    return None

__SERVICE_UUID = '98186d60-2f47-11e6-8899-0002a5d5c51b'
serviceUUIDs = set()
serviceUUIDs.add(__SERVICE_UUID)

# e3f9af20-2674-11e3-879e-0002a5d5c51b - 02  31 32    (Flag Read) - UniqueId Desc
# 5ec4e520-9804-11e3-b4b9-0002a5d5c51b - 10  34 35    (GATTC Service Done)  - LinkTest
# 4e349c00-999e-11e3-b341-0002a5d5c51b - 02  37 38    (Flag Read) - Status Desc
# 1717b3c0-9803-11e3-90e1-0002a5d5c51b - 08  40 41    (Flag Write) - Command Record
# 35ddd0a0-9803-11e3-9a8b-0002a5d5c51b - 18  43 45    (GATTC Notify) - Ack Record
# 4ed124e0-9803-11e3-b14c-0002a5d5c51b - 02  47 48    (Flag Read) - Data Record              
# 5c7d82a0-9803-11e3-8a6c-0002a5d5c51b - 16  50 52    (GATTC READ Done) - Event REcord
# 6be8f580-9803-11e3-ab03-0002a5d5c51b - 16  54 56    (GATTC READ Done) - Streaming Read Data 0
# a46a4a80-9803-11e3-8f3c-0002a5d5c51b - 16  58 60    (GATTC READ Done) - Descriptor
# b8066ec0-9803-11e3-8346-0002a5d5c51b - 16  62 64    (GATTC READ Done) - Streaming Read Data 2 
# d57cda20-9803-11e3-8426-0002a5d5c51b - 16  66 68    (GATTC READ Done) - Streaming Read Data 3
# ec865fc0-9803-11e3-8bf6-0002a5d5c51b - 04  70 71    (Flag Write No Response) - Streaming Write Data 0
# 7241b880-a560-11e3-9f31-0002a5d5c51b - 02  73 65535 (Flag Read) - Debug Status

__RECORD_READ_UUID_1 = '5c7d82a0-9803-11e3-8a6c-0002a5d5c51b'

readUUIDs = [__RECORD_READ_UUID_1,
             ]

def calc_energy(res, cadence):    
    if (res == 1) and (cadence > 14): #integral delta 0.76%
        return (cadence - 14) * 49 / 87
    if (res == 2) and (cadence > 18): #integral delta 0.7%
        return (cadence - 18) * 80 / 95
    if (res == 3) and (cadence > 17): #integral delta 0.7%
        return (cadence - 17) * 104 / 103
    if (res == 4) and (cadence > 18): #integral delta 2.6% (сглажены всплески assiom)
        return (cadence - 18) * 99 / 87
    if (res == 5) and (cadence > 21): #integral delta 0.03%
        return (cadence - 21) * 137 / 89
    if (res == 6) and (cadence > 20): #integral delta 0.94%
        return (cadence - 20) * 140 / 82
    if (res == 7) and (cadence > 22): #integral delta 0.46%
        return (cadence - 22) * 166 / 83
    if (res == 8) and (cadence > 22): #integral delta 0.03%
        return (cadence - 22) * 178 / 79
    if (res == 9) and (cadence > 23): #integral delta 0.78%
        return (cadence - 23) * 199 / 79
    if (res == 10) and (cadence > 26): #integral delta 0.62%
        return (cadence - 26) * 287 / 96
    if (res == 11) and (cadence > 22): #integral delta 0.46%
        return (cadence - 22) * 285 / 98
    if (res == 12) and (cadence > 21): #integral delta 0.58%
        return (cadence - 21) * 265 / 79
    if (res == 13) and (cadence > 20): #integral delta 1.25% (сглажены всплески assiom)
        return (cadence - 20) * 312 / 85
    if (res == 14) and (cadence > 22): #integral delta 1.4%
        return (cadence - 22) * 340 / 88
    if (res == 15) and (cadence > 20): #integral delta 1.8%
        return (cadence - 20) * 343 / 80
    if (res == 16) and (cadence > 21): #integral delta 0.21%
        return (cadence - 21) * 315 / 69
    if (res == 17) and (cadence > 20): #integral delta 1.3%
        return (cadence - 20) * 325 / 70
    if (res == 18) and (cadence > 18): #integral delta 1.8%
        return (cadence - 18) * 260 / 52
    if (res == 19) and (cadence > 21): #integral delta 2%
        return (cadence - 21) * 340 / 64
    if (res == 20) and (cadence > 17): #integral delta 1.8%
        return (cadence - 17) * 315 / 63

    if (res == 24) and (cadence > 15): #integral delta 1.7%
        return (cadence - 15) * 295 / 47
    if (res == 25) and (cadence > 17): #integral delta 0.96%
        return (cadence - 17) * 535 / 73
    return 0



last_device_time = 0
last_delta_time = 0
last_crank = 0
not_first = False
start_time = 0

def calculate(data):
    global last_device_time, last_delta_time, last_crank, not_first, start_time
    
    if not (data[0] == 17 and data[1] == 32):
        return ""
    device_time    = data[8] + 256 * data[9]
    corrected_time = device_time
    crank = (data[3] + 256 * data[4] + 65536 * data[5]) / 256.0
    resistance = data[16]
        
    while corrected_time < last_device_time:
        corrected_time += 65536
    
    delta_time = (corrected_time - last_device_time) / 1024.0

    if (delta_time > 2.0): # Filtering out too small of a difference in time?
        delta_time = last_delta_time
    last_delta_time = delta_time
    
    if not_first:
        
        if delta_time == 0:
            cadence = 0
        else:
            cadence = (crank - last_crank) * 60.0 / delta_time
        
        last_crank = crank
        last_device_time = corrected_time
        
        energy = calc_energy(resistance, cadence)
        start_time += delta_time
       
        return (start_time, delta_time, cadence, resistance, energy, energy * delta_time)
        
    not_first = True
    return (0, 0, 0, 0, 0, 0)

async def main():
    device = await find_device()
    if not device:
        print("Device not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    await asyncio.sleep_ms(1000)

    for uuidString in serviceUUIDs:
        uuid = bluetooth.UUID(uuidString)
        print("uuidString", uuidString,"UUID: ", uuid)

        try:
            service = await connection.service(uuid)

                
            print(f"{readUUIDs[0]},",
                  )

            print("start_time, delta_time, cadence, resistance, energy, energy * delta_time, data")
            while True:

                readInfo = []

                for readUUID in readUUIDs:                
                    uuid = bluetooth.UUID(readUUID)
                    
                    notify_char = await service.characteristic(uuid)
                    #(readTime, readData) = await read_characteristic(read_char)
                    
                    #readInfo.append(await read_characteristic(read_char))
                    await notify_char.subscribe()
                    #print("Subscribed")	
                    while True:
                        data = await notify_char.notified()
                        current_time = ((time.time_ns() // 1_000_000)+(31557600000 * 30))
                        #print("    ",((time.time_ns() // 1_000_000)+(31557600000 * 30))," Data: ","".join("\\x%02x" % i for i in data))
                        
                        translated = calculate(data)
                        if translated != "":
                            print(f"{current_time},{translated[0]}, {translated[1]}, {translated[2]}, {translated[3]}, {translated[4]}, {translated[5]},{"".join('\\x%02x' % i for i in data)}")

        except TypeError as e:
                print("??TypeError??,",e) 


asyncio.run(main())                
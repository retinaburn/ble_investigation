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

def dstTime():
    year = time.localtime()[0] #get current year
    # print(year)
    HHMarch = time.mktime((year,3 ,(14-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of March change to DST
    HHNovember = time.mktime((year,10,(7-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of November change to EST
    # print(HHNovember)
    now=time.time()
    if now < HHMarch : # we are before last sunday of march
        dst=time.localtime(now-18000) # EST: UTC-5H
    elif now < HHNovember : # we are before last sunday of october
        dst=time.localtime(now-14400) # DST: UTC-4H
    else: # we are after last sunday of october
        dst=time.localtime(now-18000) # EST: UTC-5H
    return(dst)


def read_characteristic(char):
    try:
        result = await char.read(timeout_ms=5000)
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

                    # 5ec4e520-9804-11e3-b4b9-0002a5d5c51b - 10  (GATTC Service Done)  
                    # e3f9af20-2674-11e3-879e-0002a5d5c51b - x2  (Flag Read)          - never returns anything
                    # 4e349c00-999e-11e3-b341-0002a5d5c51b - x2  (Flag Read)          - never returns anything
                    # 4ed124e0-9803-11e3-b14c-0002a5d5c51b - x2  (Flag Read)          - never returns anything
                    # 1717b3c0-9803-11e3-90e1-0002a5d5c51b - x8  (Flag Write)         - gets a timeout on write
                    # 35ddd0a0-9803-11e3-9a8b-0002a5d5c51b - 18  (GATTC Notify)
                    # 5c7d82a0-9803-11e3-8a6c-0002a5d5c51b - 16  (GATTC READ Done)
                    # 6be8f580-9803-11e3-ab03-0002a5d5c51b - 16  (GATTC READ Done)
                    # a46a4a80-9803-11e3-8f3c-0002a5d5c51b - 16  (GATTC READ Done)
                    # d57cda20-9803-11e3-8426-0002a5d5c51b - 16  (GATTC Read Done)
                    # ec865fc0-9803-11e3-8bf6-0002a5d5c51b - x4  (Flag Write No Response)
                    # 7241b880-a560-11e3-9f31-0002a5d5c51b - x2  (Flag Read)

__FLAG_READ_UUID_1 = 'e3f9af20-2674-11e3-879e-0002a5d5c51b'
__FLAG_READ_UUID_2 = '4e349c00-999e-11e3-b341-0002a5d5c51b'
__FLAG_READ_UUID_3 = '4ed124e0-9803-11e3-b14c-0002a5d5c51b'
__FLAG_READ_UUID_4 = '7241b880-a560-11e3-9f31-0002a5d5c51b'

readUUIDs = [__FLAG_READ_UUID_1,
             __FLAG_READ_UUID_2,
             __FLAG_READ_UUID_3,
             __FLAG_READ_UUID_4]


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

                
            print(f"{readUUIDs[0]},,",
                  f"{readUUIDs[1]},,",
                  f"{readUUIDs[2]},,",
                  f"{readUUIDs[3]},,",)

            while True:

                readInfo = []

                for readUUID in readUUIDs:                
                    uuid = bluetooth.UUID(readUUID)
                    
                    read_char = await service.characteristic(uuid)
                    #(readTime, readData) = await read_characteristic(read_char)
                    
                    readInfo.append(await read_characteristic(read_char))
                
                print(f"{readInfo[0][0]},{readInfo[0][1]},",
                      f"{readInfo[1][0]},{readInfo[1][1]},",
                      f"{readInfo[2][0]},{readInfo[2][1]},",
                      f"{readInfo[3][0]},{readInfo[3][1]}")


        except TypeError as e:
                print("??TypeError??,",e) 


asyncio.run(main())                
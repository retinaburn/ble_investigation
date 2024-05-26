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


def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

def read_characteristic(char):
    try:
        result = await char.read(timeout_ms=5000)
        #print("Type: ",type(result))
        if (type(result) == bytes):
            #time.time() + (31557600000 * 30)
            print("    ",((time.time_ns() // 1_000_000)+(31557600000 * 30))," Read: ","".join("\\x%02x" % i for i in result))
        else:
            print("    ",((time.time_ns() // 1_000_000)+(31557600000 * 30))," Read:", result)
    except TypeError as e:
        print("      ","??NoneType??,",e) 
    except ValueError:
        print("      ","No read")
    except asyncio.TimeoutError:
        print("      ","Timeout")
        
async def write_characteristic(char, msg):
    print("writing...")
    try:
        print("    Write: ", msg)
        result = await char.write(msg)
        print("    Written:", result)
    except TypeError as e:
        print("      ","??NoneType??,",e) 
    except ValueError:
        print("      ","No write")
    except asyncio.TimeoutError:
        print("      ","Timeout")
        
        
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
        
    # UUID Definition
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
    
    print("UUIDs: ", serviceUUIDs)
    noitifyUUID=""
    for uuidString in serviceUUIDs:
        uuid = bluetooth.UUID(uuidString)
        print("uuidString", uuidString,"UUID: ", uuid)
        if uuid in [bluetooth.UUID(0x1801), bluetooth.UUID(0x1800), bluetooth.UUID(0x180a)]:
            print("  Skip")
        else:
            try:
                service = await connection.service(uuid)
                async for char in service.characteristics():
                    # 
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
                    typeOfOp = ""
                    if char.properties == 10:
                        typeOfOp = "GATTC Service Done"
                    elif char.properties == 2:                    
                        typeOfOp = "Flag Read"
                    elif char.properties == 4:
                        typeOfOp = "Flag Write No Response"
                    elif char.properties == 8:
                        typeOfOp = "Flag Write"
                    elif char.properties == 18:
                        typeOfOp = "GATTC Notify"
                    elif char.properties == 16:
                        typeOfOp = "GATTC Read Done"
                    else:
                        typeOfOp = "Unknown"
                    
                    print(f"  {char} {typeOfOp}")
                    
                    ## Skip List of Characteristics
                    if char.uuid in [
                            bluetooth.UUID('5ec4e520-9804-11e3-b4b9-0002a5d5c51b'),
                            bluetooth.UUID('e3f9af20-2674-11e3-879e-0002a5d5c51b'),
                            bluetooth.UUID('4e349c00-999e-11e3-b341-0002a5d5c51b'),
                            #bluetooth.UUID('1717b3c0-9803-11e3-90e1-0002a5d5c51b'), #Flag Write
                            #bluetooth.UUID('35ddd0a0-9803-11e3-9a8b-0002a5d5c51b'), #Notify
                            bluetooth.UUID('5c7d82a0-9803-11e3-8a6c-0002a5d5c51b'),  #GATTC READ Done
                            bluetooth.UUID('6be8f580-9803-11e3-ab03-0002a5d5c51b'),  #GATTC READ Done
                            bluetooth.UUID('4ed124e0-9803-11e3-b14c-0002a5d5c51b'),
                            #bluetooth.UUID('ec865fc0-9803-11e3-8bf6-0002a5d5c51b'),  #Flag Write No Response
                        ]:
                        print("  ","Skipped")
                        next
                    else:
                        if char.properties == 18:
                            notifyUUID = char.uuid
                        elif char.properties == 8: # char.properties == 4: -- if write no response, no data comes back
                            writeUUID = char.uuid
                        elif char.properties == 2 and char.uuid == bluetooth.UUID('7241b880-a560-11e3-9f31-0002a5d5c51b'):
                            readUUID = char.uuid
                        else:
                            print ("Do other stuff")
                            #print("     - Reading")                        
                            #await read_characteristic(char)

                            #print("     - Writing")
                            #await write_characteristic(char)
                            
                            #print("     - Reading")                        
                            #await read_characteristic(char)
                            
                print ("Read: ", readUUID)
#                 while True:
#                     read_char = await service.characteristic(uuid=readUUID)
#                     await read_characteristic(read_char)
                read_char = await service.characteristic(uuid=readUUID)
                await read_characteristic(read_char)



                print ("Notifies: ", notifyUUID)
                notify_char = await service.characteristic(uuid=notifyUUID)
                await notify_char.subscribe()
                print("Subscribed!")
                
                print ("Write: ", writeUUID)
                write_char = await service.characteristic(uuid=writeUUID)
                print ("Write_char: ",write_char)

                msg = bytearray(b'\x00')
                await write_characteristic(write_char, msg)
                
                print("Will wait for data...")
                data = await notify_char.notified()
                print("Data: ",data)
                            
                msg = bytearray(b'\x00')
                await write_characteristic(write_char, msg)                    
                
                dataInt = 0
                #while data != bytearray(b'\x00\x00\x00\x00'):
                while True:
                    msg = bytearray(dataInt.to_bytes(2, 'big'))
                    await write_characteristic(write_char, msg)
                    
                    data = await notify_char.notified()
                    print("Data: ",data)
                    dataInt = dataInt + 1
                
            except TypeError as e:
                print("??TypeError??,",e) 

s = network.WLAN(network.STA_IF)
s.active(True)
s.disconnect()
print("Scanned: ", s.scan())
s.connect("MOYNES", "good4bart") # Connect to an AP
print("Connected: ", s.isconnected())

for i in range(5):
    time.sleep(5)
    print("checking is connected: ", s.isconnected()," ",s.status())
    if s.isconnected():
        break

try:
    if s.isconnected():
        ntptime.settime()
except OSError as e:
    print("OSError: ",e)
print(time.localtime()," vs ",dstTime())            

asyncio.run(main())
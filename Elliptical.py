import sys
import uasyncio as asyncio
import aioble
import bluetooth
import time

class Elliptical:
    __DEVICE_NAME = "SCHWINN 470"
    __SERVICE_UUID = '98186d60-2f47-11e6-8899-0002a5d5c51b'
    __RECORD_READ_UUID_1 = '5c7d82a0-9803-11e3-8a6c-0002a5d5c51b'

    __last_device_time = 0
    __last_delta_time = 0
    __last_crank = 0
    __not_first = False
    __start_time = 0   

    def __init__(self):
        pass

    def __read_characteristic(self, char):
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

    async def __find_device(self):
        # Scan for 5 seconds, in active mode, with very low interval/window (to
        # maximise detection rate).
        async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                if result.name() == self.__DEVICE_NAME:
                    print("Result: ",result)
                    print("Name: ",result.name(), "RSSI:",result.rssi)

                # See if it matches our name and the environmental sensing service.
                #if result.name() == "SCHWINN 470" and _ENV_SENSE_UUID in result.services():
                if result.name() == self.__DEVICE_NAME:
                    return result.device
        return None
    
    def __calc_energy(self, res, cadence):    
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

    def __calculate(self, data):
        
        if not (data[0] == 17 and data[1] == 32):
            return ""
        device_time    = data[8] + 256 * data[9]
        corrected_time = device_time
        crank = (data[3] + 256 * data[4] + 65536 * data[5]) / 256.0
        resistance = data[16]
            
        while corrected_time < self.__last_device_time:
            corrected_time += 65536
        
        delta_time = (corrected_time - self.__last_device_time) / 1024.0

        if (delta_time > 2.0): # Filtering out too small of a difference in time?
            delta_time = self.__last_delta_time
        self.__last_delta_time = delta_time
        
        if self.__not_first:
            
            if delta_time == 0:
                cadence = 0
            else:
                cadence = (crank - self.__last_crank) * 60.0 / delta_time
            
            self.__last_crank = crank
            self.__last_device_time = corrected_time
            
            energy = self.__calc_energy(resistance, cadence)
            self.__start_time += delta_time
        
            return (self.__start_time, delta_time, cadence, resistance, energy, energy * delta_time)
            
        self.__not_first = True
        return (0, 0, 0, 0, 0, 0)
    
    def __get_filename(self):
        now = time.localtime()
        filename = ""+str(now[0])+"-"+str(now[1])+"-"+str(now[2])+"T"+str(now[3])+str(now[4])+str(now[5])+".csv"
        print(f"Filename: {filename}")
        return filename
    


    async def run(self):
        device = await self.__find_device()
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

        uuid = bluetooth.UUID(self.__SERVICE_UUID)
        print("uuidString", self.__SERVICE_UUID,"UUID: ", uuid)

        try:
            service = await connection.service(uuid)

                
            print(f"Reading: {self.__RECORD_READ_UUID_1},")
                
            #file.write(header+"\n")
            while True:

                readInfo = []

                        
                uuid = bluetooth.UUID(self.__RECORD_READ_UUID_1)
                
                notify_char = await service.characteristic(uuid)
                #(readTime, readData) = await read_characteristic(read_char)
                
                #readInfo.append(await read_characteristic(read_char))
                print("Waiting for notifcation...")
                await notify_char.subscribe()
                
                start_detected = False
                end_detected = False
                data_received = False
                filename = ""
                
                #inner while loop
                while True: 
                    data = await notify_char.notified()
                    if filename == "":
                        filename = self.__get_filename()
                        file = open(filename, "w")
                        header = "start_time, delta_time, cadence, resistance, energy, energy * delta_time, data"
                        print(f"{header}\n")
                        
                    current_time = ((time.time_ns() // 1_000_000)+(31557600000 * 30))
                    #print("    ",((time.time_ns() // 1_000_000)+(31557600000 * 30))," Data: ","".join("\\x%02x" % i for i in data))
                    
                    translated = self.__calculate(data)
                    if translated != "":
                        print(f"{current_time},{translated[0]}, {translated[1]}, {translated[2]}, {translated[3]}, {translated[4]}, {translated[5]},{"".join('\\x%02x' % i for i in data)}")
                        file.write(str(current_time)+","+str(translated[0])+","+str(translated[1])+","+str(translated[2])+","+str(translated[3])+","+str(translated[4])+","+str(translated[5])+","+"".join('\\x%02x' % i for i in data)+"\n")
                        if translated[4] != 0 and translated[5] != 0.0 and start_detected:
                            data_received = True
                        if translated[4] == 0 and translated[5]==0.0 and start_detected and data_received:
                            end_detected = True
                            print("End detected")
                        if translated[4] == 0 and translated[5]==0.0 and not start_detected:
                            start_detected = True
                            print("Start detected")
                    if end_detected:
                        file.close()
                        break
                #end inner while loop
                
        except KeyboardInterrupt as e:
            return
        except TypeError as e:
            print("??TypeError??,",e) 

# e = Elliptical()
# asyncio.run(e.run())
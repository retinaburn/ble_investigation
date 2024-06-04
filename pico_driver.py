import asyncio
from Webserver2 import Webserver2
#from Webserver import Webserver
#from Elliptical import Elliptical
from machine import UART, Pin
import time

async def uart_poll():
    print(f"Waiting for uart data...")
    uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

    while True:
#         data = uart1.readline()
#         while data == None:
#             await asyncio.sleep(1)
#             data = uart1.readline()
        data = uart1.any()
        while data == 0:
            #print("Sleeping on uart...")
            await asyncio.sleep(5)
            data = uart1.any()
        data = uart1.readline()

        #Append data until newline reached
        while data[-1] != 10:
            readData = uart1.readline()
            while readData == None:
                readData = uart1.readline()
            data += str(readData)

        RECEIVED_FIRST_LINE = False
        RECEIVED_DATA = False
        RECEIVED_END = False
        FILE_NAME = ""
        DATA_SIZE = 0
        file = None

        while True:
            #print(f"First Line: {RECEIVED_FIRST_LINE}, Received Data: {RECEIVED_DATA}, Received End: {RECEIVED_END}")
            if data != None:
                print(f"Read: {str(len(data))} bytes, last 10: {data[-10:]}")          

            if (data != None and not RECEIVED_FIRST_LINE and not RECEIVED_END):
                RECEIVED_FIRST_LINE = True
                FILE_NAME = data.decode("utf-8")
                FILE_NAME = FILE_NAME.strip()
                uart1.write("ACK\n")
                print(f"Opening file: {FILE_NAME}")
                file = open(FILE_NAME, "w")
            elif (data == b'EOF\n' and RECEIVED_DATA):
                RECEIVED_FIRST_LINE = False
                RECEIVED_DATA = False
                RECEIVED_END = True
                uart1.write("ACK\n")
                
            elif (data != None and RECEIVED_FIRST_LINE and not RECEIVED_DATA):
                RECEIVED_DATA = True
                str_data = data.decode("utf-8")
                DATA_SIZE += len(str_data)
                file.write(str_data)
                uart1.write("ACK\n")
            elif (data != None and RECEIVED_DATA):
                str_data = data.decode("utf-8")
                DATA_SIZE += len(str_data)
                file.write(str_data)
                uart1.write("ACK\n")


            if (RECEIVED_END):
                RECEIVED_END = False
                uart1.write("DONE\n")
                file.close()
                print(f"Wrote {FILE_NAME}")
                break


            #await asyncio.sleep(1)
            data = None
            while data == None:
                data = uart1.readline()
            
            print(f"Data: {data}")
            #Append data until newline reached
            while data[-1] != 10:
                readData = uart1.readline()
                while readData == None:
                    readData = uart1.readline()
                data += readData
            print(f"Additional Data: {data}")
            
            print(f"Read length: {str(len(data))}")
            read_length = int(data[0:len(data)-1])
            print(f"Read Size Expected: {read_length}")
            
            data = bytearray()
            CHUNK_SIZE = read_length
            while len(data) < CHUNK_SIZE:
                print(f"{len(data)} vs {read_length}")
                read_data = uart1.read(CHUNK_SIZE - len(data))
                while read_data == None:
                    print(f"Sleeping...{len(data)} vs {read_length}")
                    await asyncio.sleep(0.1)
                    read_data = uart1.read(read_length - len(data))
                data.extend(bytearray(read_data))
            print(f"Read {len(data)} bytes, last 10: {data[-10:]}")
            read_data = 0
        
        # data = str(data)
        # print(f"Read: {data}")

        print(f"Filename: {str(FILE_NAME)}")
        print(f"File Data Size: {str(DATA_SIZE)}")
#         print(f"File Data: {FILE_DATA}")

        #file = open(FILE_NAME, "w")
        #file.write(FILE_DATA)
        #file.close()
        #print(f"Wrote {FILE_NAME}")

#asyncio.run(uart_poll())
#asyncio.run(main())
        
        
w = Webserver2()

asyncio.create_task(w.serve())
asyncio.create_task(uart_poll())
#asyncio.create_task(w.idle())
print("Done?")
loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
print("Done")        
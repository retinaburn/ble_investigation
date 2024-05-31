import asyncio
from Webserver import Webserver
#from Elliptical import Elliptical
from machine import UART, Pin
import time

async def main():
    uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
    
    w = Webserver()
    t1 = asyncio.create_task(w.serve())
    print("Started Webserver.")    
    #e = Elliptical()
    #t2 = asyncio.create_task(e.run())
    t2 = asyncio.create_task(uart_poll())
    #print("Started Elliptical.")
    await asyncio.gather(t1, t2)
    #await asyncio.gather(t1, t2)

async def uart_poll():
    uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

    data = uart1.readline()
    while data == None:
        await asyncio.sleep(1)
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
    FILE_DATA = ""

    while True:
        #print(f"First Line: {RECEIVED_FIRST_LINE}, Received Data: {RECEIVED_DATA}, Received End: {RECEIVED_END}")
        
        if (data != None and not RECEIVED_FIRST_LINE and not RECEIVED_END):
            RECEIVED_FIRST_LINE = True
            FILE_NAME = data.decode("utf-8")
            FILE_NAME = FILE_NAME.strip()
            uart1.write("ACK\n")
        elif (data == b'EOF\n' and RECEIVED_DATA):
            RECEIVED_FIRST_LINE = False
            RECEIVED_DATA = False
            RECEIVED_END = True
            uart1.write("ACK\n")
            
        elif (data != None and RECEIVED_FIRST_LINE and not RECEIVED_DATA):
            RECEIVED_DATA = True
            FILE_DATA += data.decode("utf-8")
            uart1.write("ACK\n")
        elif (data != None and RECEIVED_DATA):
            FILE_DATA += data.decode("utf-8")
            uart1.write("ACK\n")


        if (RECEIVED_END):
            RECEIVED_END = False
            uart1.write("DONE\n")
            break

        if data != None:
            print(f"Read: {str(len(data))} bytes,   {data}")          

        #await asyncio.sleep(1)
        data = None
        while data == None:
            data = uart1.readline()
        
        #Append data until newline reached
        while data[-1] != 10:
            readData = uart1.readline()
            while readData == None:
                readData = uart1.readline()
            data += readData
    
    # data = str(data)
    # print(f"Read: {data}")

    print(f"Filename: {str(FILE_NAME)}")
    print(f"File Data Size: {str(len(FILE_DATA))}")
    print(f"File Data: {FILE_DATA}")

asyncio.run(uart_poll())
#asyncio.run(main())
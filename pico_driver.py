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
    data = uart1.read(5)
    while data != None:
        print(f"Read: {data}")
        uart1.write("hello")
        await asyncio.sleep(1)
        

asyncio.run(main())
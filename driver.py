import asyncio
from Elliptical import Elliptical
from machine import UART, Pin
import time
async def main():
#    w = Webserver()
#    t1 = asyncio.create_task(w.serve())
#    print("Started Webserver.")
#    asyncio.run(w.serve())
    t1 = asyncio.create_task(uart_poll())
    e = Elliptical()
    t2 = asyncio.create_task(e.run())
    print("Started Elliptical.")
    await asyncio.gather(t1, t2)
    #await asyncio.gather(t1, t2)

async def uart_poll():
    uart1 = UART(1, baudrate=9600, tx=Pin(21), rx=Pin(5))
    while True:
        print(f"Wrote: {uart1.write('hello')}")
        #print(f"Read: {uart1.read(5)}")
        await asyncio.sleep(5)



asyncio.run(main())
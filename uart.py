from machine import UART, Pin
import time
uart1 = UART(1, baudrate=9600, tx=Pin(21), rx=Pin(5))
#uart2 = UART(2, baudrate=9600, tx=Pin(6), rx=Pin(7))
print("Hello")
while True:
    print(f"Wrote: {uart1.write('hello')}")
    print(f"Read: {uart1.read(5)}")
    time.sleep(1)
data = uart1.read(5)
print(f"Read: {data}")
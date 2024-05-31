from machine import UART, Pin
import time
uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
print("Hello")
uart1.write('hello')
while True:
    #
    data = uart1.read(5)
    while data != None:
        print(f"Read: {data}")
        uart1.write("hello")
    time.sleep(1)

import asyncio
from Webserver2 import Webserver2
#from Webserver import Webserver
#from Elliptical import Elliptical
from machine import UART, Pin
import time
uart1 = None

async def uart_poll():
    #debug_file = open("debug.csv", "w")
    #debug_file.write(b'')
    #debug_file.close()
    

    uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
    
    while True:

        #Wait for UART data
        any_data = uart1.any()
        print(f"Waiting for uart data...")
        while any_data == 0:
            #print("Sleeping on uart...")
            await asyncio.sleep(0.1)
            any_data = uart1.any()
                
        #Get filename
        data = uart1.readline()
        print(f"Data found: {data}")

        #Append data until newline reached
        while data[-1] != 10:
            readData = uart1.readline()
            while readData == None:
                readData = uart1.readline()
            data += str(readData)

        FILE_NAME = ""
        DATA_SIZE = 0
        file = None
        
        print(f"Filename: {data[0:len(data)-1]}")
        FILE_NAME = data[0:len(data)-1]
        file = open(FILE_NAME, "w")
        
        #ACK Filename
        uart1.write('ACK\n')
        MAX_LOOP_FOR_CHUNK = 20
        
        while True:

            #Read chunk size
            data = uart1.readline()
            loop_for_chunk = 0
            while data == None:
                loop_for_chunk += 1
                time.sleep(0.1)
                if loop_for_chunk == MAX_LOOP_FOR_CHUNK:
                    loop_for_chunk = 0
                    print("Sending NACK for CHUNK...")
                    uart1.write('NACK\n')
                data = uart1.readline()
            #Append data until newline reached
            while data[-1] != 10:
                readData = uart1.readline()
                while readData == None:
                    readData = uart1.readline()
                data += str(readData)
            uart1.write('ACK\n') #ACK Chunk Size
            
            #Set chunk size            
            CHUNK_SIZE = int(data[0:len(data)-1])

            #Try to read chunk size worth of bytes
            data = uart1.read(CHUNK_SIZE)
            #Loop until there is data
            while data == None:
                data = uart1.read(CHUNK_SIZE)
                        
            #if we read less data than the chunk size
            #Send a NACK, to try reading that chunk again
            actual_size = len(data)
            while actual_size < CHUNK_SIZE:
                print(f"Actual Size: {str(actual_size)}")
                if actual_size < CHUNK_SIZE:
                    print("Sending NACK for data...")
                    uart1.write('NACK\n')
                    time.sleep(0.1)
                data = uart1.read(CHUNK_SIZE)
                while data == None:
                    data = uart1.read(CHUNK_SIZE)
                actual_size = len(data)
            
            DATA_SIZE += actual_size 
            if data == b'EOF\n':
                break      
            
            #Write chunk of data to filesystme
            file.write(data)
            
            #ACK chunk of data            
            uart1.write('ACK\n')            
            

        #ACK EOF
        uart1.write('ACK\n') 
        file.close()
        print(f"Read {ACTUAL_SIZE} bytes")

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
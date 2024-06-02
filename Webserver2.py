import usocket as socket
import network
import gc
import sys
import os
import asyncio
from machine import UART, Pin
import time
#gc.collect()

import ujson
import time

class Webserver2:
    
    def __init(self):
        try:
            fp = open('secrets.json')
            secretsString = fp.read()
            secrets = ujson.loads(secretsString)
        except OSError as e:
            print("Error reading secret: ", e)
            sys.exit()
            
        station = network.WLAN(network.STA_IF)
        station.active(True)
        #station.config(pm = 0xa11140) causes a wifi unknown error
        station.connect(secrets['wifi']['ssid'], secrets['wifi']['password'])
        while station.isconnected() == False:
            print(f"Waiting for connection to wifi...")
            time.sleep(1)
            pass

        print(f"Connection successful: {station.ifconfig()}")

    def __getFiles(self):
        files = []
        for file in os.listdir():        
            if file.endswith(".csv"):
                print(f"{file}")
                files.append(file)
        files_with_mtime = [(file, os.stat(file)[8]) for file in files]
        sorted_files = sorted(files_with_mtime, key=lambda x: x[1], reverse=True)
        for file in sorted_files:
            print(f"{file[0],file[1]}")
            
        ## Keep only last 5 files
        for file in sorted_files[10-len(sorted_files):len(sorted_files)]:
            print(f"Removing {file[0]}")
            #os.remove(file[0])
        return [file[0] for file in sorted_files]
    def __getPage(self):
        files = self.__getFiles()
        print(f"{files}")
        
        html = """
            <html>
            <head><title>Elliptical Data</title><head>
        """
        for file in files:
            html += "<a href=" + file + " download>" + file + "</a>"
            html += "<br/>\r\n"
        html +="""
            </html>
        """
        return html
    

    async def serve_client(self, reader, writer):
        try:
            request = await reader.readline()
            print(f"Content: {request}")
            if (len(str(request)) == 0 or request == b''):
                print("Skipping request...")
                await writer.wait_closed()
                return
            
            split_request = str(request).split()
            print(f"Content: 1={split_request[0]},2={split_request[1]},3={split_request[2]}")
            if split_request[1] == "/":
                response = self.__getPage()
                writer.write("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: " + str(len(response)) + "\r\n\r\n\r\n")
                writer.write(response)
                print(f"Response: {response}")
            elif split_request[1] == "/favicon.ico" or split_request[1] == "HNAP1/" or split_request[1] == "/JNAP/":
                writer.write("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 2\r\n\r\n\r\n")
            else:
                requested_file = split_request[1][1:len(split_request[1])]
                print(f"Requested: {requested_file}")
                f = open(requested_file, "rb")
                size = os.stat(requested_file)[6]
                #print(f"Read: {data}")
                print(f"Size: {size}")
                            
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n" + \
                           "Content-Disposition: attachment; filename=\""+requested_file+"\"\r\n" + \
                           "Content-Length: " + str(size) + "\r\n" \
                           "Connection: Close \r\n\r\n"
                print(f"Response: {response}")
                writer.write(response)
                while True:
                    data = f.read(32768)
                    print(f"{time.localtime()}, Data Size: {str(len(data))}")
                    if data == b'':
                        break
                    writer.write(data)
                    await writer.drain()

            print("Closing")
            await writer.drain()
            writer.close()
            
            print("Closed")
        except MemoryError as e:
            print(f"Error: {e}")

    async def serve(self):
        print("Serving")
        self.__init()
        asyncio.create_task(asyncio.start_server(self.serve_client,"0.0.0.0", 80))

    async def idle(self):
        while True:
            print("Idle...")
            await asyncio.sleep(5)


# w = Webserver2()
# 
# asyncio.create_task(w.serve())
# #asyncio.create_task(w.idle())
# asyncio.create_task(uart_poll())
# print("Done?")
# loop = asyncio.get_event_loop()
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     loop.close()
# print("Done")

import usocket as socket
import network
import gc
import sys
import os
import asyncio

#gc.collect()

import ujson
import time

class Webserver2:
    s = 0
    conn = ''
    
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
            if file.endswith(".py"):
                print(f"{file}")
                files.append(file)
        files_with_mtime = [(file, os.stat(file)[8]) for file in files]
        sorted_files = sorted(files_with_mtime, key=lambda x: x[1], reverse=True)
        for file in sorted_files:
            print(f"{file[0],file[1]}")
            
        ## Keep only last 5 files
        for file in sorted_files[3-len(sorted_files):len(sorted_files)]:
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
            html += "<br/>"
        html +="""
            </html>
        """
        return html
    

    async def serve_client(self, reader, writer):
        #1. Never seems to get the request reliably....
        request = await reader.readline()
        print(f"Content: {request}")
        split_request = str(request).split()
        print(f"Content: 1={split_request[0]},2={split_request[1]},3{split_request[2]}")
        if split_request[1] == "/":
            response = self.__getPage()
            writer.write("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 2\r\n\r\n\r\n")
            writer.write(response)
            print(f"Response: {response}")
        else:
            requested_file = split_request[1][1:len(split_request[1])]
#             requested_file = request
            print(f"Requested: {requested_file}")
            f = open(requested_file)
            data = f.read()
            print(f"Read: {data}")
            writer.write(data)
            writer.write('\r\n')

        print("Closing")
        await writer.drain()
        #await writer.wait_closed()
        print("Closed")

    async def serve(self):
        print("Serving")
        self.__init()
        asyncio.create_task(asyncio.start_server(self.serve_client,"0.0.0.0", 80))
#         while True:
#             #print("heartbeat")
#             await asyncio.sleep(5)

    async def idle(self):
        while True:
            #print("Idle...")
            await asyncio.sleep(5)
try:
    w = Webserver2()
    #asyncio.run(w.serve())
    asyncio.create_task(w.serve())
    asyncio.run(w.idle())
    print("Done?")
except OSError as e:
    print("Error ", e)
finally:
    asyncio.new_event_loop()
    

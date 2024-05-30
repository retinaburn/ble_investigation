import usocket as socket
import network
import gc
import sys
import os
import asyncio

gc.collect()

import ujson
import time

class Webserver:
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

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(('',80))
            self.s.listen(5)
        except OSError as e:
            print("Error", e)
            if self.s:
                self.s.close()
            raise(e)


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
    
    async def serve(self):
        print("Serving")
        #asyncio.create_task(self.server())
        await self.server()
        

    async def server(self):
        
        self.__init()
                
        try:
            while True:
                print(f"Waiting for connection...")
                self.conn, addr = self.s.accept()
                self.conn.setblocking(True)
                #1. Never gets a connection anymore ...what is going on ???
                print(f"Got a connection from {str(addr)}")
                request = self.conn.recv(1024)
                request = str(request)
                print(f"Content: {request}")
                split_request = request.split()
                requested_file = split_request[1][1:len(split_request[1])]
                if split_request[1] == "/":
                    response = self.__getPage()
                    self.conn.send("HTTP/1.1 200 OK\n")
                    self.conn.send("Content-Type: text/html\n")
                    self.conn.send("Connection: close\n\n")
                    self.conn.sendall(response)

                elif split_request[1] == "/favicon.ico":
                    self.conn.send("HTTP/1.1 200 OK\n")
                    self.conn.send("Content-Type: text/html\n")
                    self.conn.send("Connection: close\n")
                elif split_request[1] == "HNAPI/":
                    self.conn.send("HTTP/1.1 200 OK\n")
                    self.conn.send("Content-Type: text/html\n")
                    self.conn.send("Connection: close\n")                    

                else:
                    print(f"Requested: {requested_file}")
                    f = open(requested_file, "rb")
                    data = f.read()
                    print(f"Read: {str(len(data))}")                    
                    #print(f"Read: {data}")
                    self.conn.send("HTTP/1.1 200 OK\r\n")                    
                    self.conn.send("Content-Type: text/plain\r\n")
                    self.conn.send("Content-Disposition: attachment; filename=\"" + requested_file + "\"\n")
                    self.conn.send("Content-Length: " + str(len(data)) + "\r\n")
                    self.conn.send("Connection: close\r\n")                    
                    #self.conn.sendall(data)
                    self.conn.write("\r\n")
                    wrote_bytes = self.conn.write(data)                
                    print(f"Wrote: {wrote_bytes}")
                    #await asyncio.sleep(10)
                    print(f"{requested_file} sent")                    
                self.conn.close()
        except OSError as e:
            print("OSError: ", e)
            self.__close()
        except KeyboardInterrupt:
            self.__close()
            
    def __close(self):
        print("Cleaning up")
        if self.conn:
            self.conn.close()
        if self.s:
            self.s.close()
            
try:
    w = Webserver()
    asyncio.run(w.serve())
    #asyncio.create_task(w.serve())
    #w.server()
    print("Done?")
#     while True:
#         pass
except OSError as e:
    print("Error ", e)
finally:
    asyncio.new_event_loop()
    
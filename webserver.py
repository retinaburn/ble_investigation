import usocket as socket
import network
import gc
import sys
import os

gc.collect()

import ujson
import time

try:
    fp = open('secrets.json')
    secretsString = fp.read()
    secrets = ujson.loads(secretsString)
except OSError as e:
    print("Error reading secret: ", e)
    sys.exit()
    
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(secrets['wifi']['ssid'], secrets['wifi']['password'])
while station.isconnected() == False:
    print(f"Waiting for connection to wifi...")
    time.sleep(1)
    pass

print(f"Connection successful: {station.ifconfig()}")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('',80))
    s.listen(5)
except OSError as e:
    print("Error", e)
    if s:
        s.close()
    raise(e)


def getFiles():
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
def getPage():
    files = getFiles()
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

conn = ''
try:
    while True:
        print(f"Waiting for connection...")
        conn, addr = s.accept()
        print(f"Got a connection from {str(addr)}")
        request = conn.recv(1024)
        request = str(request)
        print(f"Content: {request}")
        response = getPage()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
        conn.close()
except OSError as e:
    print("OSError: ", e)
    s.close()
except KeyboardInterrupt:
    if conn:
        conn.close()
    if s:
        s.close()

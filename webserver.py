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
    print(f"Waiting for connection...")
    time.sleep(1)
    pass

print(f"Connection successful: {station.ifconfig()}")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(('',80))
    s.listen(5)
except OSError as e:
    print("Error", e)
    s.close()
    raise(e)


def getFiles():
    files = []
    for file in os.listdir():        
        if file.endswith(".py"):
            print(f"{file}")
            files.append(file)
    return files
def getPage():
    files = getFiles().sort()
    
    html = """
        <html>
        <head><title>Elliptical Data</title><head>
    """
    for file in files:
        html += "<a href=" + file + " download>" + file + "</a>"
        html += "<a href='./"
        html += "<br/>"
    html +="""
        </html>
    """
    return html

try:
    while True:
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
except KeyboardInterrupt:
    if s:
        s.close()

#files = getFiles()
import asyncio
import network
import ujson

async def serve_client(reader, writer):
    print("Reading...")
    data = await reader.readline()
    print("Read")
    print(f"received {data}")
    writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 2\r\n\r\n\r\n')
    writer.drain()
    print("drained")
    
    #1. If we do this the connection gets closed seemingly before we sent the response
    # But we drain so that should be impossible
    #await writer.wait_closed()
    
    #2 Connection never closes, curl request never completes
    #writer.close()

async def do_connect():
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
        await asyncio.sleep(1)
        pass

    print(f"Connection successful: {station.ifconfig()}")
    
async def main():
    print(f"Starting...")
    await do_connect()
    #loop = asyncio.get_event_loop()
    #loop.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    #loop.run_forever()
    
    asyncio.run(asyncio.start_server(serve_client, "0.0.0.0", 80))
    
    #server = await asyncio.start_server(serve_client, "0.0.0.0", 80)
    #await asyncio.gather(server)
    while True:
        ## I swear heartbeat was printing out frequently, now it only prints out once... what is going on
        print("heartbeat")
        await asyncio.sleep(1)
    
print("Starting main")    
asyncio.run(main())
#main()
print("Finished")
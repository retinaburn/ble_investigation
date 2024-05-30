import asyncio
from Webserver import Webserver
from Elliptical import Elliptical

async def main():
    w = Webserver()
    t1 = asyncio.create_task(w.serve())
    #asyncio.run(w.serve())
    e = Elliptical()
    t2 = asyncio.create_task(e.run())
    print("Started Elliptical.")
    await asyncio.gather(t1, t2)

asyncio.run(main())
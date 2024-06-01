import asyncio
from Elliptical import Elliptical

e = Elliptical()
e.__enable_send_file(True)
asyncio.run(e.run())
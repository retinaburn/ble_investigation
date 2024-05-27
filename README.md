# ble_investigation

## mp_ble.py

### MicroPython BLE Experiment

An investigation into using [aioble](https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble)

1. Connects to LAN and gets time
2. Scans for the Schwinn 470 device (based on name), 
3. Connects to the device and scans for characteristics
    * Can skip a list of known characteristics
4. Reads Data, Sets up a subscription, and Writes Data 

## elliptical.py

### MicroPython BLE Experiment

Reading multiple data characteristics from a BLE device.

## elliptical_data.py

### Working example of calculations from Record Data for Schwinn 470 Elliptical

Connects to specific device by name, a specific service id, and specific GATTC Read characteristic. Reads the data and performs required calculations. Based on some wonderful code I found from ursoft [here](https://github.com/ursoft/zwift-offline/blob/4b0cff1270465d375f8f73c918f212e29e1cf0e0/storage/schwinn_csv.py)

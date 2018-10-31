import bluetooth
import PyOBEX

name = "Europa"
dev_address = None
service = None

devices = bluetooth.discover_devices()

for device in devices:
    print(device)
    print(bluetooth.lookup_name(device))
    if (bluetooth.lookup_name(device) == name):
        dev_address = device
        break
        
if (dev_address != None):
    services = bluetooth.find_service(address = dev_address, uuid = "0008")
    port = services[0]["port"]
    print("Port", port)
    from PyOBEX.client import BrowserClient 
    client = BrowserClient(dev_address, port)
    directories = client.listdir()
    print(directories)
    client.disconnect()
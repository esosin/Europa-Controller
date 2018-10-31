import bluetooth
import sys
import subprocess

target_name = "Europa"
Europa = 'D8:68:C3:94:47:DE'
cat = "/home/pi/Documents/cat.jpg"

def check_connection(device_name = "Europa"):
    dev_address = None
    devices = bluetooth.discover_devices()
    for device in devices:
        print(bluetooth.lookup_name(device))
        if (bluetooth.lookup_name(device) == device_name):
            dev_address = device
            break
    if (dev_address == None):
        sys.exit(device_name + " not found. Ensure that the name is correct, and that Bluetooth is available")
    return dev_address

def start_bluetooth_server(server_sock):
    port = bluetooth.PORT_ANY
    server_sock.bind(("", port))
    server_sock.listen(1)
    print("listening for connections")
    uuid = "00000000-0000-1000-8000-00805f9b34fb"
    bluetooth.advertise_service(server_sock, "Europa Interface",service_id = uuid, service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                   profiles=[bluetooth.SERIAL_PORT_PROFILE])
    client_sock, address = server_sock.accept()
    print(address)
    '''
    if (address != Europa):
        client_sock.close()
        server_sock.close()
        print("unrecognized bluetooth address connected to the hardware")
        sys.exit()
    '''
    #else:
    #print("Connected to " + address.toString())
    return client_sock
    
def repeat(europa_sock):
    # check to see what needs to be done
    command  = europa_sock.recv(1024)
    command = command.decode('ascii')
    #have all the actions sent at one time only push bluetooth info when action is nessecary
    print(command)  

#Europa = check_connection()
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
europa_sock = start_bluetooth_server(server_sock)
europa_sock.send("AAAHHHHHHHHHH")
process = subprocess.Popen('sudo bt-obex -p ' + Europa + ' ' + cat, shell=True)
for i in range(10):
    repeat(europa_sock)
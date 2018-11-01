from PIL import Image
from PIL import ImageDraw
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO
import bluetooth
import cv2
import numpy as np
from pypylon import pylon
import matplotlib.pyplot as plt
import sys
import os
from os import path
import subprocess
import time
import math
import select

#bluetooth config
target_name = "Europa"
#Europa = 'D8:68:C3:94:47:DE' #tablet
Europa = '94:76:B7:E3:11:CC'
# Europa = '34:2D:0D:AD:D4:1D'
# holds the MAC address for the Device

# Raspberry Pi GPIO configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0
backlight = 3
UV = 2
SPEED_HZ = 4000000

# Create TFT LCD display object.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

#Initialize Digital Output pins
GPIOcontroller = GPIO.RPiGPIOAdapter( RPi.GPIO, mode = RPi.GPIO.BCM)
GPIOcontroller.setup(pin = UV, mode = GPIO.OUT)
GPIOcontroller.setup(pin = backlight, mode = GPIO.OUT)
GPIOcontroller.output(UV, GPIO.LOW)
GPIOcontroller.output(backlight, GPIO.LOW);

# Initialize ST7735 display and variables used in its operation
WIDTH = 128 
HEIGHT = 160
x0 = 40
y0 = 40
calibrationWidth = 50
calibrationHeight = 50
exposure = 180
default_diam = 1.0
current_diam = default_diam
disp.begin()


def get_image(savePath):
    global GPIOcontroller
    try:
        GPIOcontroller.output(backlight, GPIO.HIGH)
        img = camera.GrabOne(4000)
        img = cv2.cvtColor(img.Array, cv2.COLOR_RGB2BGR)
        print("image taken")
        cv2.imwrite(savePath, img)
        print("image saved to " + savePath)
        GPIOcontroller.output(backlight, GPIO.LOW)
        # return img
    
    except Exception:
        sys.exit("Camera is unconnected or uninitialized. Check connection or implementation")

def initialize_camera():
## add a try catch block for camera first line
    cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    print("Camera Connected : ", cam.GetDeviceInfo().GetModelName())
    cam.Open()
    cam.ExposureTime.SetValue(400)
    cam.Width.SetValue(1750)
    cam.Height.SetValue(1684)
    cam.OffsetX.SetValue(430)
    cam.OffsetY.SetValue(260)
    '''
    pylon.FeaturePersistence.Save('initial.pfs', cam.GetNodeMap())
    pylon.FeaturePersistence.Load('NodeMap.pfs', cam.getNodeMap(), False)
    '''
    cam.PixelFormat.SetValue('RGB8')
    
    return cam

def check_connection(device_name = "Europa"):
    dev_address = None
    devices = bluetooth.discover_devices()
    for device in devices:
        if (bluetooth.lookup_name(device) == device_name):
            dev_address = device
            break
    if (dev_address == None):
        sys.exit(device_name + " not found. Ensure that the name is correct, and that Bluetooth is available")
    return dev_address

def send_image(file_location, dev_address):
    process = subprocess.Popen('sudo bt-obex -p ' + dev_address + ' ' + file_location, stdout=subprocess.PIPE,shell=True)
    #CompletedProcess(args = ['sudo bt-obex -p ' + dev_address + ' ' + file_location], returncode = 0) 

    #print(dev_address)
    print("Attempting to send image")
'''
def send_image(socket,sendPath,packageSize = 1024):
    """
    Sends file to the device
    @param sendPath is file path address @ host device
    @param packageSize is packet size of pure data @BluetoothSocket
    """
    if (packageSize == None):
        packageSize = 1024
    f = open(sendPath,'rb')
    socket.send(sendPath)##send EXACT name of file 
    packet = 1
    print(sendPath ,"is", os.path.getsize(sendPath), "starts @", time.ctime())
    while (packet):
        packet = f.read(1024)
        socket.send(packet)
    print("Send @:", time.ctime())
    isFileSent = True
    f.close()
'''
def calibration_screen():
    image = Image.new("P",(WIDTH,HEIGHT),255)
    pen = ImageDraw.Draw(image)
    pen.rectangle([(x0,y0), (x0 + calibrationWidth, y0 + calibrationHeight)], fill =255, outline = 0)
    pen.rectangle([(x0 + 3, y0),(x0 + calibrationWidth - 3, y0+calibrationHeight)], fill=255, outline = 255)
    pen.rectangle([(x0 , y0+3),(x0 + calibrationWidth , y0+calibrationHeight-3)], fill=255, outline = 255) 
    disp.display(image)


def open_ellipse(x, y, w, h, outline = True):
    # x,y refer to the center point of the ellipse
    # w and h are height and width in mm, limited by min pixel size for ST_7735 (230 microns)
    width = float(w)
    height = float(h)
    a = width / 2.0
    b = height / 2.0
    pix_w =  mm_to_pix(a) 
    pix_h = mm_to_pix(b)
    print("pixel radius == " + str(pix_h))
    
    if (outline):
        image = Image.new("P", (WIDTH, HEIGHT), 255)
    else:
        image = Image.new("P", (WIDTH, HEIGHT), 0)
    pen = ImageDraw.Draw(image)
    #pen.rectangle([(x0,y0), (x0 + calibrationWidth, y0 + calibrationHeight)], fill = 0, outline = 255)
    if(pix_w <= 1 or pix_h <= 1):
        print("opening point")
        pen.point([x,y] , fill = 255)
    else:
       print("Opening circle")
       pen.ellipse([(x - pix_w, y - pix_h), (x + pix_w, y + pix_h)], fill = 255, outline = 0)
    image.save('last ROI.bmp')
    disp.display(image)
    
def open_circle(x, y, diam, outline = True):
    # x,y  refer to the center of the circle
    # diam refers to the diameter in mm, limited by min pixel size for ST_7735 (230 microns)
    open_ellipse(x,y, diam, diam, outline)

def open_rect(x, y, w, h):
    image = Image.new("P", (WIDTH, HEIGHT), 0)
    pen =  ImageDraw.Draw(image)
    w = w/2
    h = h/2
    pix_w = floor(w / .230)
    pix_h = floor(h / .230)
    if(pix_w <= 1 and pix_h <= 1):
        pen.point(x,y, fill = 255)
    else:
        pen.rectangle([(x - w, y - h), (x + w, y + h)], fill = 255)
    disp.display(image)
    
def open_square(x,y,w):
    open_rect(x, y, w, w)

def complex_Mask(points):
    image = Image.new("P", (WIDTH, HEIGHT), 0);
    pen =  ImageDraw.Draw(image)
    pen.polygon(points, fill = 255)
    
def start_bluetooth_server(server_sock):
    port = bluetooth.PORT_ANY
    server_sock.bind(("", port))
    server_sock.listen(1)
    print("listening for connections")
    uuid = "00000000-0000-1000-8000-00805f9b34fb"
    bluetooth.advertise_service(server_sock, "Europa Interface",service_id = uuid, service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                   profiles=[bluetooth.SERIAL_PORT_PROFILE])
    client_sock, address = server_sock.accept()
    print("Connected")
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

def start(controller):
    calibration_screen()

def listen(sock,controller):
    print("listening for commands")
    # check to see what needs to be done
    command  = sock.recv(1)
    #print(command)
    #print(type(command))
    command = command.decode('ascii')
    #have all the actions sent at one time only push bluetooth info when action is nessecary
    
    decision_tree(command, controller, sock)
    
    
    # choose action based on the command

def decision_tree(char, controller, sock):
    controller.output(backlight, GPIO.LOW)
    print("command == " + char)
    if (char == 'd'):
        openROI(sock, controller)
        
    elif (char == 'e'):
        settings()
        
    elif (char == 'f'):
        start(controller)
        get_image(file_location)
        #send_image(file_location, Europa)
        send_image(file_location, Europa)
    elif(char == 'q'):
        sock.send("Shutting Down")
        sys.exit()
    
    listen(sock,controller)

def openROI(sock, controller):
    print("open ROI")
    x = sock.recv(1)#WHAT HAPPENS
    x = int.from_bytes(x, byteorder = 'big')
    x = float (x)
    x = x / 100.0
    x = 1.0 - x
    print ("X: " + str(x))
    y = sock.recv(1)
    y = int.from_bytes(y, byteorder = 'big')
    y = float(y)
    y = y / 100.0
    y = 1.0 - y
    print("Y: " + str(y))
    X = int(math.floor(x0 + (x * calibrationWidth)))
    Y = int(math.floor(y0 + (y * calibrationHeight)))
    print("pixel local (x,y) : (" + str(X) + ", " + str(Y) + ")")
    print("Open ROI DIAM: " + str(current_diam));
    open_circle(X, Y, current_diam, outline = True)
    controller.output(backlight, GPIO.HIGH)
    # how do I know when to abort during an illumination period
    proceed = sock.recv(1)
    proceed = proceed.decode('ascii')
    print ("Proceed command == " + str (proceed))
    controller.output(backlight, GPIO.LOW)
    if (proceed == 'l'):
        open_circle(X, Y, current_diam, outline = False)
        illuminate(10, controller, sock)
    elif (proceed == 'm'):
        print("user opted out of illumination, use app to retake picture")
    clear_buffer = sock.recv(1024)
   
def settings():
    print("accessing settings menu; listening for settings command")
    command = europa_sock.recv(1)
    command = command.decode('ascii')
    global current_diam
    print("settings command == " + command)
    if (command == 'a'):
        current_diam = .230
    elif (command == 'b'):
        current_diam = default_diam
    elif (command == 'c'):
        current_diam = 2.0
        print("current diam (settings)" + str(current_diam))
    elif (command == 'd'):
        current_diam = 5.0
    else :
        print(" unknown setting recieved, ROI diameter returned to default 1.0 mm setting")
        current_diam = default_diam
    time.sleep(2);

def illuminate(seconds, controller, sock):
    timer = seconds;
    controller.output(backlight, GPIO.LOW)
    controller.output(UV , GPIO.HIGH)
    while(timer > 0):
        ready = select.select([sock], [], [], 1)
        if (ready[0]):
            command = sock.recv(1024)
            command = command.decode('ascii')
            print("Illuminate command == " + command)
            if (command == 'q'):
                controller.output(UV, GPIO.LOW)
                break
        timer = timer - 1
        print("time remaining : " + str(timer)) 
    controller.output(UV, GPIO.LOW)
    controller.output(backlight, GPIO.HIGH)

def mm_to_pix(mm):
    mm_float = float(mm)
    pix = int(math.floor(mm_float / .230))
    return pix


#calibration_screen()
# Initialize camera and image storage location
camera = initialize_camera()
#Europa = check_connection()
file_location = '/home/pi/Documents/Europa.jpg'
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
europa_sock = start_bluetooth_server(server_sock)
listen(europa_sock, GPIOcontroller)
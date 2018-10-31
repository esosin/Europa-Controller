from PIL import Image
from PIL import ImageDraw
from pypylon import pylon
import matplotlib.pyplot as plt
import numpy as np
import cv2
import bluetooth
import subprocess
import os

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
    process = subprocess.Popen('sudo bt-obex -p ' + dev_address + ' ' + file_location, shell=True)
    print("Attempting to send image")

photo_address = '/home/pi/Documents/Test_gray.jpg'
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
print("Camera Connected : ", camera.GetDeviceInfo().GetModelName())
camera.Open()
camera.PixelFormat.SetValue('RGB8')
img = camera.GrabOne(4000)
img = cv2.cvtColor(img.Array, cv2.COLOR_RGB2BGR)
cv2.imwrite(photo_address, img)

address = check_connection()
send_image(photo_address, address)


    
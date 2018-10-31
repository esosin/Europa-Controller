from PIL import Image
from PIL import ImageDraw
from pypylon import pylon
import matplotlib.pyplot as plt
import numpy as np
import cv2

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
print("Camera Connected : ", camera.GetDeviceInfo().GetModelName())
camera.Open()
camera.PixelFormat.SetValue('RGB8')
img = camera.GrabOne(4000)
img = cv2.cvtColor(img.Array, cv2.COLOR_RGB2BGR)
cv2.imwrite('/home/pi/Documents/Test_gray.jpg', img)




    
    
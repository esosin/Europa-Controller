from PIL import Image
from PIL import ImageDraw
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO
import cv2
from pypylon import pylon
import math

# Raspberry Pi GPIO configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0
backlight =4
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

def initialize_camera():
    cam= pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    print("Camera Connected : ", cam.GetDeviceInfo().GetModelName())
    cam.Open()
    cam.PixelFormat.SetValue('RGB8')
    return cam

def get_image(savePath):
    try:
        img = camera.GrabOne(4000)
        img = cv2.cvtColor(img.Array, cv2.COLOR_RGB2BGR)
        print("image taken")
        cv2.imwrite(savePath, img)
        print("image saved to " + savePath)
        # return img
    
    except Exception:
        sys.exit("Camera is unconnected or uninitialized. Check connection or implementation")
        
def openROI(a,b, diam):
    x = float (a)
    x = x / 100.0
    print ("X: " + str(x))
    y = float(b)
    y = y / 100.0
    print("Y: " + str(y))
    X = int(math.floor(x0 + (x * calibrationWidth)))
    Y = int(math.floor(y0 + (y * calibrationHeight)))
    #print("x: " + X + ", y: " + Y)
    # print("Open ROI DIAM: " + str(current_diam));
    open_circle(X, Y, diam)
    # how do I know when to abort during an illumination period

def open_ellipse(x, y, w, h):
    # x,y refer to the center point of the ellipse
    # w and h are height and width in mm, limited by min pixel size for ST_7735 (230 microns)
    
    width = float(w)
    height = float(h)
    a = width / 2.0
    b = height / 2.0
    pix_w =  mm_to_pix(a) 
    pix_h = mm_to_pix(b)
    print("radius == " + str(pix_h))
    image = Image.new("P", (WIDTH, HEIGHT), 0)
    pen =  ImageDraw.Draw(image)
    pen.rectangle([(x0,y0), (x0 + calibrationWidth, y0 + calibrationHeight)], fill = 0, outline = 255)
    if(pix_w <= 1 or pix_h <= 1):
        print("opening point")
        pen.point([x,y] , fill = 255)
    else:
       print("Opening circle")
       pen.ellipse([(x - pix_w, y - pix_h), (x + pix_w, y + pix_h)], fill = 255, outline = 255)
    image.save('last ROI.bmp')
    disp.display(image)

def mm_to_pix(mm):
    mm_float = float(mm)
    pix = int(math.floor(mm_float / .230))
    return pix
    
def open_circle(x, y, diam):
    # x,y  refer to the center of the circle
    # diam refers to the diameter in mm, limited by min pixel size for ST_7735 (230 microns)
    open_ellipse(x,y, diam, diam)

def calibration_screen():
    image = Image.new("P",(WIDTH,HEIGHT),255)
    pen = ImageDraw.Draw(image)
    pen.rectangle([(x0,y0), (x0 + calibrationWidth, y0 + calibrationHeight)], fill =255, outline = 0)
    pen.rectangle([(x0 + 3, y0),(x0 + calibrationWidth - 3, y0+calibrationHeight)], fill=255, outline = 255)
    pen.rectangle([(x0 , y0+3),(x0 + calibrationWidth , y0+calibrationHeight-3)], fill=255, outline = 255)
    pen.ellipse([(x0 + calibrationWidth, y0),(x0 + calibrationWidth + 3, y0 + 3)],fill = 255, outline= 0)
    disp.display(image)

openROI(-20, 80,15.0)

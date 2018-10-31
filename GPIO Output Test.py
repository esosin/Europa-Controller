from PIL import Image
from PIL import ImageDraw
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO

def calibration_screen():
    image = Image.new("P",(WIDTH,HEIGHT),255)
    pen = ImageDraw.Draw(image)
    pen.rectangle([(x0,y0), (x0 + calibrationWidth, y0 + calibrationHeight)], fill =255, outline = 0)
    pen.rectangle([(x0 + 3, y0),(x0 + calibrationWidth - 3, y0+calibrationHeight)], fill=255, outline = 255)
    pen.rectangle([(x0 , y0+3),(x0 + calibrationWidth , y0+calibrationHeight-3)], fill=255, outline = 255) 
    disp.display(image)

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

WIDTH = 128 
HEIGHT = 160
x0 = 40
y0 = 40
calibrationWidth = 50
calibrationHeight = 50
exposure = 180
disp.begin()

controller = GPIO.RPiGPIOAdapter( RPi.GPIO, mode = RPi.GPIO.BCM)
controller.setup(pin = UV, mode = GPIO.OUT)
controller.setup(pin = backlight, mode = GPIO.OUT)
controller.output(UV, GPIO.LOW)
controller.output(backlight, GPIO.HIGH)
calibration_screen();
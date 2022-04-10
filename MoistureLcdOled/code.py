# Some LCD Docs
# https://learn.sparkfun.com/tutorials/pic-based-serial-enabled-character-lcd-hookup-guide/all

# https://github.com/jimblom/Serial-LCD-Kit/wiki/Serial-Enabled-LCD-Kit-Datasheet

import time
import board
import busio
import neopixel
import displayio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from adafruit_seesaw.seesaw import Seesaw
from board import SCL, SDA
from microcontroller import Pin
import terminalio
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon

print('getting I2C')
i2c_bus = board.I2C()  # This works better than explicitly giving pins, why?

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=True)

pixel[0] = 0x00

uart = busio.UART(board.TX, board.RX, baudrate=9600)

# Set up OLED
i2c = i2c_bus
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3d)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Set up Moisture Sensor
ss = Seesaw(i2c_bus, addr=0x36)

# LCD utilities
def clearLcd():
    b = bytes([0xFE, 0x01])
    uart.write(b)

def nextLine():
    b = bytes([0xFE, 192])
    uart.write(b)
    
def write(val):
    s = str(val)
    bytes = str.encode(s)
    uart.write(bytes)

def off():
    b = bytes([0xFE, 0x08])
    uart.write(b)

def on():
    b = bytes([0xFE, 0x0C])
    uart.write(b)

def dim():
    print('dim')
    b = bytes(18)
    uart.write(b)
    

# DISPLAY NONSENSE
if True:
    WIDTH = 128
    HEIGHT = 64
    BORDER = 3
    
    displayGroup = displayio.Group(max_size=10)
    display.show(displayGroup)

    # x, y, x, y, radius
    roundrect = RoundRect(0, 0, WIDTH, HEIGHT, 5, fill=0x000000, outline=0xFFFFFF, stroke=2)
    displayGroup.append(roundrect)
 
    # Draw a label, used like a group
    text = "Hello World!"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=10)
    displayGroup.append(text_area)

    
#LCD
on()

while True:
    clearLcd()
    pixel[0] = 0x00400
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()

    # read temperature from the temperature sensor
    tempC  = ss.get_temp()
    tempF  = (tempC * 1.8) + 32
    tS = "{:0.2f}".format(tempF)
    print("temp: " + str(tS) + "\nmoisture: " + str(touch))
    write('Moisture: ')
    write(touch)
    nextLine()
    write('Temp: ')
    write(tS)
    print()
    pixel[0] = 0x00


    text = "Temp: " + str(tS) + "\nMoisture: " + str(touch)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=28, y= int(HEIGHT/3))
    displayGroup.pop()
    displayGroup.append(text_area)
    time.sleep(1)


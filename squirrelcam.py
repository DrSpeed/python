import time
import board
import busio
import neopixel 
import math
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

from microcontroller import Pin
import microcontroller
import digitalio
import adafruit_tsl2591
import adafruit_amg88xx

led = neopixel.NeoPixel(board.NEOPIXEL, 1)

RED = (55, 0, 0)
YELLOW = (50, 25, 0)
GREEN = (0, 50, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 55)
PURPLE = (180, 0, 255)
BLACK = (0, 0, 0)

# Turn off neopixel
led[0] = (0,0,0)

uart = busio.UART(board.TX, board.RX, baudrate=31250)

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA

# Initialize the sensor.
lightSensor = adafruit_tsl2591.TSL2591(i2c)

print('created sensor')

#analog_in = AnalogIn(board.A0)
# CAMERA
cameraPin = DigitalInOut(board.D8)
cameraPin.direction = Direction.OUTPUT

print('Got camera pin')
cameraPin.value = True
time.sleep(5.0) # wait for camera to initialize, seems to help cheap a$$ camera

# THERMAL SENSOR
amg = adafruit_amg88xx.AMG88XX(i2c)
print('Got Thermal Sensor')
time.sleep(1.0)
TAB = '\t'

#--------------------------------------------
# Thermal Sensor
#-------------------------------------------

THERMAL_DIFF = 2.5

def testThermal():
    allCells = []
    for row in amg.pixels:
        for c in row:
            allCells.append(c)
        
    print('--')
    #print(allCells)
    allMax = max(allCells)
    avg = sum(allCells)/len(allCells)
    print(str(min(allCells)) + TAB + str(max(allCells)) + TAB + str(avg))
    print('----')
    if (avg + THERMAL_DIFF < allMax):
        print('thermal')
        return True
    else:
        print('no thermal diff')
        return False

def isLight():
    #lux = lightSensor.lux
    #print("Total light: {0}lux".format(lux))
    # You can also read the raw infrared and visible light levels.
    # These are unsigned, the higher the number the more light of that type.
    # There are no units like lux.
    # Infrared levels range from 0-65535 (16-bit)
    infrared = lightSensor.infrared
    #print("Infrared light: {0}".format(infrared))
    # Visible-only levels range from 0-2147483647 (32-bit)
    visible = lightSensor.visible
    print("Visible light: {0}".format(visible))
    # Full spectrum (visible + IR) also range from 0-2147483647 (32-bit)
    #full_spectrum = lightSensor.full_spectrum
    #print("Full spectrum (IR + visible) light: {0}".format(full_spectrum))

    LIGHT_THRESHOLD = 20000000

    print('--------------')
                 
    if visible >= LIGHT_THRESHOLD: 
        print('is light')
        return True
    else:
        print('too dark')
        return False

def takePicture():        
    led[0] = BLUE
    cameraPin.value=False
    time.sleep(0.05)
    cameraPin.value=True
    led[0] = YELLOW
    print('Done taking picture, waiting')
    time.sleep(15.0)    # main sleeper, camera really wants a little time to save picture.



while True:
    if  testThermal():
        if isLight():
            print('Taking picture')
            takePicture()
            led[0] = GREEN
        else:
            print('Not taking picture')
            led[0] = RED
    else:
        print('No thermal')
        led[0] = BLACK
        
    time.sleep(1.0)

    
    








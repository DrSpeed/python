#------------------------------------------------------    
# Simple lidar/light/camera project
# ---------
# 2022 sjw
#
#------------------------------------------------------
import time
import board
import busio
import neopixel 
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from microcontroller import Pin
import microcontroller
import digitalio
import adafruit_tsl2591
import adafruit_vl53l4cd
import adafruit_apds9960.apds9960


# Single on-board neopixel
led = neopixel.NeoPixel(board.NEOPIXEL, 1)

# CAMERA
# Just the worlds simples camera
cameraPin = DigitalInOut(board.D8)
cameraPin.direction = Direction.OUTPUT
print('Got camera pin')
cameraPin.value = True
time.sleep(1.0) # wait for camera to initialize, seems to help cheap a$$ camera

# COLOR CONSTANTS
RED = (55, 0, 0)
YELLOW = (50, 25, 0)
GREEN = (0, 50, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 55)
PURPLE = (180, 0, 255)
BLACK = (0, 0, 0)

# Turn off neopixel
led[0] = (0,0,0)

# serial LCD uses the UART, very old school but hey, whatever
uart = busio.UART(board.TX, board.RX, baudrate=9600)

# LCD STUFF----------
def LcdCmd(b):
    uart.write( bytearray(b) )
    time.sleep(0.1)

def Clear():
    LcdCmd([0xFE, 0x01]) 

def LcdOn():
    LcdCmd([0xFE, 0x42, 0x00]) 

def LcdOff():
    LcdCmd([0x80, 0x00]) 

def SetCursor(col, row):  # col, row starting at 1
    LcdCmd([0xFE, 0x47, col, row])

def WriteString(text):
    LcdCmd(text)
# END LCD --------------------

Clear()
WriteString('Initializing...') # We can only do this after we actually have the LCD
time.sleep(1.0)

# Create sensor object, communicating over the board's default I2C bus
Clear()
WriteString('I2C, sensors, camera...') # We can only do this after we actually have the LCD
print('creating i2c')
i2c = board.I2C()  # uses board.SCL and board.SDA
print('created first i2c')
print('attemping light sensor on first i2c')
lightSensor = adafruit_tsl2591.TSL2591(i2c)
print('created light sensor')
Clear()

#--------------------------------------------
# Time Of Flight
#-------------------------------------------
# Creating new I2C because of address conflict

THERMAL_DIFF = 0.1
# This is magic here!
# Use the Analog inputs as a secondary I2C!
# On metro M4 board, typically you can find alternative I2Cs on atmel m series boards
# A4 = (blue) = SDA  (data)
# A5 = (yellow or green) = SDC  (clock)
print ('attempting 2nd i2c')
I2C2 = busio.I2C(board.A5, board.A4) # Monkey around until you get a pair
print('got 2nd i2c port using A5, A4') 

adp9960 = adafruit_apds9960.apds9960.APDS9960(I2C2)
print('got gesture sensor')
adp9960.enable_proximity = True

print('attempting vl53l4cd on 2nd i2c')
vl53 = adafruit_vl53l4cd.VL53L4CD(I2C2)
print('aquired 53L4CD lidar')

# OPTIONAL: can set non-default values
vl53.inter_measurement = 0
vl53.timing_budget = 200

print("VL53L4CD")
print("--------------------")
model_id, module_type = vl53.model_info
print("Model ID: 0x{:0X}".format(model_id))
print("Module Type: 0x{:0X}".format(module_type))
print("Timing Budget: {}".format(vl53.timing_budget))
print("Inter-Measurement: {}".format(vl53.inter_measurement))
print("--------------------")

vl53.start_ranging()

#lastAvg = getAvgTherm()
lastAvg = None

# TODO:  Update this use lidar
def testThermal():
    global lastAvg
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
    
    retval = (avg - THERMAL_DIFF ) > lastAvg # got brighter

    #avgDiff = avg - lastAvg
    #WriteString(str(avgDiff))

    print(str(avg) + ',' + str(lastAvg))

    lastAvg = avg

    if retval:
        return True
    else:
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
    #print("Visible light: {0}".format(visible))
    # Full spectrum (visible + IR) also range from 0-2147483647 (32-bit)
    #full_spectrum = lightSensor.full_spectrum
    #print("Full spectrum (IR + visible) light: {0}".format(full_spectrum))

    LIGHT_THRESHOLD = 20000000

    print('--------------')
                 
    if visible >= LIGHT_THRESHOLD: 
        #print('is light')
        return True
    else:
        #print('too dark')
        return False

def takePicture():        
    led[0] = BLUE
    cameraPin.value=False
    time.sleep(0.05)
    cameraPin.value=True
    led[0] = YELLOW
    msg = 'Done taking picture, waiting'
    WriteString(msg)
    print(msg)
    time.sleep(10.0)    # main sleeper, camera really wants a little time to save picture.

lastFail = False

while True:
    while not vl53.data_ready:
        #print('.', end='')
        pass
    #print('\n')

    d = vl53.distance # get distance at this point in time, it may change
    vl53.clear_interrupt()

    Clear() # LCD

    


    # if seems that 0.0 means 'too far' and the following value is
    # also invalid
    if lastFail == True:
        lastFail = False
        #print('failed last')
        time.sleep(0.1)
        continue

    if  d < 0.01: #no math.isclose() in this python
        lastFail = True
        #print('failed this' + str(d))
        time.sleep(0.1)
        continue
    else:
        lastFail = False

    WriteString(" {} cm".format(d))  # LCD
    print("Distance: {} cm".format(d))
    print("Proximity: {} ".format(adp9960.proximity)) 
 
    if isLight():
        print('*')
 

    time.sleep(0.5)


while True:
    print('clear')
    Clear()
    if  testThermal():
        WriteString('Thermal pass')
        if isLight():
            Clear()
            WriteString('Taking picture')
            takePicture()
            Clear()
            WriteString('Done taking picture')
            led[0] = GREEN
        else:
            WriteString(', too dark')
            print('Not taking picture')
            led[0] = RED
    else:
        WriteString('Thermal fail')
        print('No thermal')
        led[0] = BLACK
        
    time.sleep(1.0)

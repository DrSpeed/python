import os
import time
import board
import busio
import microcontroller
import adafruit_pm25
import adafruit_sdcard
import microcontroller
import board
import busio
import digitalio
import storage
import adafruit_gps
from analogio import AnalogIn
import board
import busio
from microcontroller import Pin
from digitalio import DigitalInOut, Direction, Pull 
import neopixel

doLogPin = DigitalInOut(board.D8)     
doLogPin.direction = Direction.INPUT
doLogPin.pull = Pull.UP

# Grand Central default UART
uart = busio.UART(board.TX, board.RX, baudrate=9600)
i2c = busio.I2C(board.SCL, board.SDA)


# Initilialize globals
pm25   = None
i2cGps = None

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixels.brightness = 0.1

lastLat = None
lastLon = None

def pixelRed():
    pixels[0] = (255, 0, 0)
    pixels.show()

def pixelYellow():
    pixels[0] = (255, 0, 0)
    pixels.show()


def pixelGreen():
    pixels[0] = (0, 255, 0)
    pixels.show()

def pixelBlue():
    pixels[0] = (0, 0, 255)
    pixels.show()

def pixelBlack():
    pixels[0] = (0, 0, 0)
    pixels.show()

def InitGps():
    global i2cGps


    i2cGps = adafruit_gps.GPS_GtopI2C(i2c, debug=False) # Use I2C interface
    print('I2C gps initialized')

    i2cGps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
    i2cGps.send_command(b"PMTK220,2000")

    print('Done initializing GPS')
    time.sleep(2)


def ReadGps(g):
    print('reading gps')

    ret = g.update()
    print('gps update(): ', ret)

    if not g.has_fix:
        # Try again if we don't have a fix yet.
        print("Waiting for fix...")
        data = g.read(64)  # read up to 32 bytes
        print(data)  # this is a bytearray type
        return
    else:
        print('has fix')

    if ret == False:
        Clear()
        data = g.read(32)  # read up to 32 bytes
        print(data)  # this is a bytearray type
        WriteString('GPS update() fail')
        print('gps update false, returning')
        return

    Clear()
    SetCursor(0,0)        

    if not g.has_fix:
        print('no fix')
    else:
        print('Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}'.format(
                g.timestamp_utc.tm_mon,   # Grab parts of the time from the
                g.timestamp_utc.tm_mday,  # struct_time object that holds
                g.timestamp_utc.tm_year,  # the fix time.  Note you might
                g.timestamp_utc.tm_hour,  # not get all data like year, day,
                g.timestamp_utc.tm_min,   # month!
                g.timestamp_utc.tm_sec))
        print('Latitude: {} degrees'.format(g.latitude))
        print('Longitude: {} degrees'.format(g.longitude))
        print('Fix quality: {}'.format(g.fix_quality))
        # Some attributes beyond latitude, longitude and timestamp are optional
        # and might not be present.  Check if they're None before trying to use!
        if g.satellites is not None:
            print('# satellites: {}'.format(g.satellites))
        if g.altitude_m is not None:
            print('Altitude: {} meters'.format(g.altitude_m))
        if g.track_angle_deg is not None:
            print('Speed: {} knots'.format(g.speed_knots))
        if g.track_angle_deg is not None:
            print('Track angle: {} degrees'.format(g.track_angle_deg))
        if g.horizontal_dilution is not None:
            print('Horizontal dilution: {}'.format(g.horizontal_dilution))

        lat = ("{0:.1f}".format(g.latitude))
        lon = ("{0:.1f}".format(g.longitude))
        s = "{}, {}".format(lat, lon)
        Clear()
        print(s)
        #WriteString(s)
        #WriteString(' ')
    
    if g.satellites is not None:
        print("{} Sats".format(g.satellites))
        WriteString(g.satellites)
    else:
        print('no satellites')
        WriteString('0')
 



 
# Connect to the card and mount the filesystem.
def InitSdCard():
    spi = busio.SPI(board.SD_SCK, board.SD_MOSI, board.SD_MISO)
    cs = digitalio.DigitalInOut(board.SD_CS)
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")

print('Done setting up SD Card')
# ---------------------------------------------







def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000
 
        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)
 
        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))
 
        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)




def InitPm25():
    reset_pin = None
    global pm25
    pm25 = adafruit_pm25.PM25_UART(uart, reset_pin)

def LcdCmd(b):
    uart.write( bytearray(b) )
    time.sleep(.01)

def WriteString(text):
    LcdCmd(text)

def Clear():
    LcdCmd([0xFE, 0x58])

def LcdOn():
    LcdCmd([0xFE, 0x42, 0x00]) 

def LcdOff():
    LcdCmd([0xFE, 0x46]) 

def SetCursor(col, row):  # col, row starting at 1
    LcdCmd([0xFE, 0x47, col, row])

def BacklightWhite():
    LcdCmd([0xFE, 0xD0, 0xFF, 0xFF, 0xFF])

def BacklightRed():
    LcdCmd([0xFE, 0xD0, 0xFF, 0x0, 0x0])

def BacklightYellow():
    LcdCmd([0xFE, 0xD0, 0xFF, 0xFF, 0x0])

def BacklightGreen():
    LcdCmd([0xFE, 0xD0, 0x0, 0x0F, 0x00])

def BacklightBlue():
    LcdCmd([0xFE, 0xD0, 0x0, 0x00, 0xFF])

def SetBrightness(b):
    LcdCmd([0xFE, 0x99, b])

def SetCursorHome():
    LcdCmd([0xFE, 0x48])

def TurnOnBacklight():
    LcdCmd([0xFE, 0x42])

def WriteString(text):
    ba = str(text)
    LcdCmd(ba)

def SetContrast(c):
    LcdCmd([0xFE, 0x50, c])

def PrintAQData(aqdata):
    print()
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
    )
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
    )
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
    print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
    print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
    print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
    print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
    print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
    print("---------------------------------------")


def GetSmoke(aqdata):
    #print(type(aqdata["particles 03um"]))
    #return aqdata["particles 03um"]
    return aqdata["pm100 standard"]


def LogToSdCard():
    with open("/sd/temperature.txt", "a") as file:
        temperature = microcontroller.cpu.temperature
        print("Temperature = %0.1f" % temperature)
        file.write("%0.1f\n" % temperature)
    # File is saved
    time.sleep(1)


Clear()
WriteString('PM Logger')

pixelRed()

SetBrightness(150)
SetContrast(150)
BacklightWhite()
LcdOn()
print('Init PM25')
InitPm25()
print('Done init pm25')

print(pm25)

InitSdCard()
LogToSdCard()
print('wrote to sd card')

InitGps()

pixelGreen()

print("Files on filesystem:")
print("====================")
#print_directory("/sd")



def LogInfoToSdCard(timestr, lat, lon, part):
    # add feedback (led?)
    with open("/sd/log.csv", "a") as file:
        #file.write("%0.1f\n" % temperature)
        file.write("{}, {}, {}, {} \n".format(timestr, lat, lon, part))
    # File is saved
    time.sleep(1)


def testGps(gps):

    gps.update()
    # Every second print out current location details if there's a fix.
    if not gps.has_fix:
        # Try again if we don't have a fix yet.
        print("Waiting for fix...")
    else:
        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.
        print("=" * 40)  # Print a separator line.
        print(
            "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,  # month!
                gps.timestamp_utc.tm_sec,
            )
        )
        print("Latitude: {0:.6f} degrees".format(gps.latitude))
        print("Longitude: {0:.6f} degrees".format(gps.longitude))
        print("Fix quality: {}".format(gps.fix_quality))
        # Some attributes beyond latitude, longitude and timestamp are optional
        # and might not be present.  Check if they're None before trying to use!
        if gps.satellites is not None:
            print("# satellites: {}".format(gps.satellites))
        if gps.altitude_m is not None:
            print("Altitude: {} meters".format(gps.altitude_m))
        if gps.speed_knots is not None:
            print("Speed: {} knots".format(gps.speed_knots))
        if gps.horizontal_dilution is not None:
            print("Horizontal dilution: {}".format(gps.horizontal_dilution))
        if gps.height_geoid is not None:
            print("Height geo ID: {} meters".format(gps.height_geoid))




while True:

    pixelBlue()
    try:
        i2cGps.update()
        i2cGps.update()
        i2cGps.update()
        i2cGps.update()
    except:
        print('Error with GPS')
        pixelRed()
        continue

    pixelGreen()
    try:
        ReadGps(i2cGps)    
    except:
        print('error reading gps')
        Clear()
        WriteString('Error Read GPS')
        pixelRed()
        continue

    g = i2cGps

    if g is None or g.timestamp_utc is None:
        Clear()
        print("Can't read gps object")
        WriteString('No GPS or GPS time')
        pixelRed()
        continue
    
    if g.latitude is None or g.longitude is None:
        print("Can't read gps object")
        Clear()
        print("Can't read gps position")
        WriteString('No GPS position')
        pixelRed()
        continue

    if int(g.timestamp_utc.tm_mon)  == 0 or int(g.timestamp_utc.tm_mday) == 0 or int(g.timestamp_utc.tm_year) == 0 or int(g.timestamp_utc.tm_hour) == 0:
        print('Invalid time, skipping')
        Clear()
        continue
    else:
        try:
            year =   int(g.timestamp_utc.tm_year)
            month =  int(g.timestamp_utc.tm_mon)
            day =    int(g.timestamp_utc.tm_mday)
            hour =   int(g.timestamp_utc.tm_hour)
            minute = int(g.timestamp_utc.tm_min)
        except:
            print("Can't read gps object")
            pixelRed()
            continue

    LcdOn()
    pixelGreen()
    timeString = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(year, month, day, hour, minute)
    showTimeString = "{:02d}:{:02d} utc".format(hour, minute)
    print(timeString)
    print('Latitude: {} degrees'.format(g.latitude))
    print('Longitude: {} degrees'.format(g.longitude))
    ltd = ("{0:.3f}".format(g.latitude))
    lng = ("{0:.3f}".format(g.longitude))

    SetCursor(1,1)
    WriteString("GPS {} sats".format(g.satellites))
    SetCursor(1,2)
    WriteString("{},{}".format(ltd, lng))
    time.sleep(1.0)

    SetCursor(1,1)
    WriteString("                ");
    SetCursor(1,1)
    WriteString(showTimeString)

    aqdata = pm25.read()
    smoke = GetSmoke(aqdata) 
    print("{},{},{},{}".format(timeString, ltd, lng, smoke))

    if doLogPin.value:
        print('NOT logging')
    else:  # Logging
        if lastLat is None:
            lastLat = ltd
            lastLon = lng
            pixelBlue()
            print('logging first time')
            SetCursor(1,1)
            WriteString('Writing 1st log ')
            LogInfoToSdCard(timeString, ltd, lng, smoke)
        elif lastLat is not None and lastLat != ltd and lastLon != lng:
            pixelBlue()
            print('logging')
            SetCursor(1,1)
            WriteString('Writing log...')
            LogInfoToSdCard(timeString, ltd, lng, smoke)
            lastLat = ltd
            lastLon = lng
        else: # just skip same location
            print('not logging, same or missing')

    print('-----------')

    s = str('Particles: {}   '.format(smoke))  # sjw: clear one line?
    print(s)
    SetCursor(1,2)
    WriteString(s)

    pixelBlack()
    time.sleep(2.0)
    pixelGreen()

import time
import board
import neopixel
import os
import random
import busio
import digitalio
from digitalio import DigitalInOut
import adafruit_vl53l4cd
from random import randint

# Import Adafruit IO REST client.
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import json

import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi


# COLOR CONSTANTS for use w/LED, dimmed for final product
RED    = (5, 0, 0)
YELLOW = (5, 5, 0)
GREEN  = (0, 5, 0)
CYAN   = (0, 255, 255)
BLUE   = (0, 0, 5)
PURPLE = (180, 0, 255)
BLACK  = (0, 0, 0)

FEED_NAME = "sump"

SLEEP_SECS = 10.0


print("Importing secrets...")
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print("Done Importing secrets...")


print("Initializing WIFI...")    
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
print("done Initializing WIFI")        

#
# Send a measurement to the AdafruitIO feed 
#
def sendIO(sump_val):
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

    print("Connecting to AP...")
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
            pixels.fill(BLACK)
        except RuntimeError as e:
            print("could not connect to AP, retrying: ", e)
            continue
        print("Connected to", str(esp.ssid, "utf-8"), "\tRcvSigStrnIndic:", esp.rssi)

    pixels.fill(YELLOW)
    socket.set_interface(esp)
    pixels.fill(BLACK)

    pixels.fill(YELLOW)
    requests.set_socket(socket, esp)
    pixels.fill(BLACK)

    # get/set io user/pwd from secrets
    aio_username = secrets["io_username"]
    aio_key = secrets["io_key"]

    # Initialize an Adafruit IO HTTP API object
    io = IO_HTTP(aio_username, aio_key, requests)

    # Send sump value to IO
    print("Sending {0} to sump feed...".format(sump_val))
    pixels.fill(YELLOW)
    io.send_data(FEED_NAME, sump_val)
    pixels.fill(BLACK)
    print("Data sent!")






print('Initializing I2C...')
i2c = board.I2C()
print('Done Initializing I2C')

print('Initializing Range Sensor...')
vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)
print('Done Initializing Range Sensor')

# OPTIONAL: can set non-default values
vl53.inter_measurement = 0
vl53.timing_budget = 200



print("VL53L4CD Information")
print("--------------------")
model_id, module_type = vl53.model_info

print("Model ID: 0x{:0X}".format(model_id))
print("Module Type: 0x{:0X}".format(module_type))
print("Timing Budget: {}".format(vl53.timing_budget))
print("Inter-Measurement: {}".format(vl53.inter_measurement))
print("--------------------")

print ('Initializing ranging...')
vl53.start_ranging()
print ('Done Initializing ranging')

print ('Initializing neopixel...')
led = digitalio.DigitalInOut(board.D4)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# NEOPIXEL CODE
pixel_pin = board.D4
num_pixels = 1
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
print ('Done Initializing neopixel...')



#
# showData() Write data to host console
#
def showData(s):
        print(s) 
        print("--------")

while True:
    try:
        if vl53.data_ready:
            pixels.fill(BLUE)
            vl53.clear_interrupt()
            s =  "{} cm".format(vl53.distance)
            showData(s)
            pixels.fill(YELLOW)
            sendIO(vl53.distance)
            pixels.fill(BLACK)
        else:  # NOT READY YET
            pixels.fill(RED)

    except:
        print('error')
        pixels.fill(RED)

    pixels.fill(GREEN)
    print('sleeping...')
    time.sleep(SLEEP_SECS)
    print('done sleeping.')


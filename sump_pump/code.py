import time
import board
import neopixel
import os
import random
import busio
import digitalio
from digitalio import DigitalInOut
import adafruit_ds3231
import adafruit_vl53l4cd

# Import Adafruit IO REST client.
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import json

import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi


# My connection to Adafruit IO
# IO_USERNAME  "drspeed"
# IO_KEY       "0312d30c3baba2a2ad61163d440343b73b33660e"

def getWifi():
    # Get wifi details and more from a secrets.py file
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    print("ESP32 SPI webclient test")

    TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
    JSON_URL = "http://api.coindesk.com/v1/bpi/currentprice/USD.json"


    # If you are using a board with pre-defined ESP32 Pins:
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)

    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

    requests.set_socket(socket, esp)

    if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
        print("ESP32 found and in idle mode")
        print("Firmware vers.", esp.firmware_version)
        print("MAC addr:", [hex(i) for i in esp.MAC_address])

    for ap in esp.scan_networks():
        print("\t%s\t\tRSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))

    print("Connecting to AP...")
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
        except OSError as e:
            print("could not connect to AP, retrying: ", e)
            continue

    print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
    print("My IP address is", esp.pretty_ip(esp.ip_address))
    print("IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com")))
    print("Ping google.com: %d ms" % esp.ping("google.com"))

    # esp._debug = True
    print("Fetching text from", TEXT_URL)
    r = requests.get(TEXT_URL)
    print("-" * 40)
    print(r.text)
    print("-" * 40)
    r.close()

    print()
    print("Fetching json from", JSON_URL)
    r = requests.get(JSON_URL)
    print("-" * 40)
    print(r.json())
    print("-" * 40)
    r.close()

    print("Done!")
    time.sleep(60.0)


getWifi()


print('-I2C-')
i2c = board.I2C()

print('getting clock')

print('getting range sensor')
vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)

# OPTIONAL: can set non-default values
vl53.inter_measurement = 0
vl53.timing_budget = 200


# set the time (do this once) 
 #                     year, mon, date, hour, min, sec, wday, yday, isdst




print("VL53L4CD Simple Test.")
print("--------------------")

model_id, module_type = vl53.model_info

print("Model ID: 0x{:0X}".format(model_id))

print("Module Type: 0x{:0X}".format(module_type))

print("Timing Budget: {}".format(vl53.timing_budget))

print("Inter-Measurement: {}".format(vl53.inter_measurement))

print("--------------------")


vl53.start_ranging()


if False:
    while not i2c.try_lock():
        pass
    try:
        while True:
            print(
                "I2C addresses found:",
                [hex(device_address) for device_address in i2c.scan()],
            )
            time.sleep(2)

    finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
        i2c.unlock()



RED    = (5, 0, 0)
YELLOW = (255, 150, 0)
GREEN  = (0, 5, 0)
CYAN   = (0, 255, 255)
BLUE   = (0, 0, 5)
PURPLE = (180, 0, 255)

led = digitalio.DigitalInOut(board.D4)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# NEOPIXEL CODE
pixel_pin = board.D4
num_pixels = 1
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
print ('done with neopixel')
print('------------')


def showData(s):
    for row in range(0, 4):
        print(s) 
        print("--------")



while True:
    try:
        if vl53.data_ready:
            vl53.clear_interrupt()
            s =  "{} cm".format(vl53.distance)
            showData(s)
            pixels.fill(BLUE)
        else:
            s = 'nr'
            pixels.fill(RED)

        time.sleep(0.5)

        #print('.', end=' ')  # feedback, it's working
        pixels.fill(GREEN)
   
    except:
        print('error')
        pixels.fill(RED)

    time.sleep(0.5)

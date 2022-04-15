
import time

import board
import busio
import digitalio
import neopixel

import adafruit_si4713

RED    = (10, 0, 0)
YELLOW = (25, 15, 0)
GREEN  = (0, 25, 0)
CYAN   = (0, 25, 25)
BLUE   = (0, 0, 55)
PURPLE = (18, 0, 25)
BLACK  = (0, 0, 0)



# Specify the FM frequency to transmit on in kilohertz.  As the datasheet
# mentions you can only specify 50khz steps!
FREQUENCY_KHZ = 101700 #101.7   # 102.300mhz

pixels = neopixel.NeoPixel(board.D10, 1)

pixels[0] = YELLOW


# Initialize I2C bus.
i2c = board.I2C()
si_reset = digitalio.DigitalInOut(board.D9)

print("initializing si4713 instance")
si4713 = adafruit_si4713.SI4713(i2c, reset=si_reset, timeout_s=0.5)
print("done")

# Measure the noise level for the transmit frequency (this assumes automatic
# antenna capacitance setting, but see below to adjust to a specific value).
noise = si4713.received_noise_level(FREQUENCY_KHZ)
# Alternatively measure with a specific frequency and antenna capacitance.
# This is not common but you can specify antenna capacitance as a value in pF
# from 0.25 to 47.75 (will use 0.25 steps internally).  If you aren't sure
# about this value, stick with the default automatic capacitance above!
# noise = si4713.received_noise_level(FREQUENCY_KHZ, 0.25)
print("Noise at {0:0.3f} mhz: {1} dBuV".format(FREQUENCY_KHZ / 1000.0, noise))

# Tune to transmit with 115 dBuV power (max) and automatic antenna tuning
# capacitance (default, what you probably want).
si4713.tx_frequency_khz = FREQUENCY_KHZ
si4713.tx_power = 115

# Configure RDS broadcast with program ID 0xADAF (a 16-bit value you specify).
# You can also set the broadcast station name (up to 96 bytes long) and
# broadcast buffer/song information (up to 106 bytes long).  Setting these is
# optional and you can later update them by setting the rds_station and
# rds_buffer property respectively.  Be sure to explicitly specify station
# and buffer as byte strings so the character encoding is clear.
si4713.configure_rds(0xADAF, station=b"912C Radio", rds_buffer=b"Radio Free Albany")

# Print out some transmitter state:
print("Transmitting at {0:0.3f} mhz".format(si4713.tx_frequency_khz / 1000.0))
print("Transmitter power: {0} dBuV".format(si4713.tx_power))
print(
    "Transmitter antenna capacitance: {0:0.2} pF".format(si4713.tx_antenna_capacitance)
)

# Set GPIO1 and GPIO2 to actively driven outputs.
si4713.gpio_control(gpio1=True, gpio2=True)



# Main loop will print input audio level and state and blink the GPIOs.
print("Broadcasting...")

while True:
    try:
        # Print input audio level and state.
        # print("Input level: {0} dBfs".format(si4713.input_level))
        #print("ASQ status: 0x{0:02x}".format(si4713.audio_signal_status))
            
        if si4713.input_level < -20:
            pixels[0] = BLUE
            continue

        # 'Blink' GPIO1 and GPIO2 alternatively on and off.
        si4713.gpio_set(gpio1=True, gpio2=False)  # GPIO1 high, GPIO2 low
        if pixels[0] == RED:
            pixels[0] = BLACK
        else:
            pixels[0] = RED

    except:
        print("An exception occurred") 
        pixels[0] = YELLOW

    time.sleep(0.5)

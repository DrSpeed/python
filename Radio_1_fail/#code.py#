import time
import board
import neopixel
import busio
import sdcardio
import storage
import os
import digitalio

import audiomixer

pixel_pin = board.D4
num_pixels = 1

#pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)
#pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
#pixels = neopixel.NeoPixel(board.A1, 1)
#pixels = neopixel.NeoPixel(board.D0, 10, pixel_order=neopixel.RGBW)

# Doc says RGB
#pixels = neopixel.NeoPixel(pixel_pin, num_pixels, pixel_order=neopixel.RGB)
#pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixels = neopixel.NeoPixel(board.D10, 1)

pixels[0] = (30, 0, 0)
pixels.show()

# Use the board's primary SPI bus
spi = board.SPI()
# Or, use an SPI bus on specific pins:
#spi = busio.SPI(board.SD_SCK, MOSI=board.SD_MOSI, MISO=board.SD_MISO)

# For breakout boards, you can choose any GPIO pin that's convenient:
cs = board.D8
# Boards with built in SPI SD card slots will generally have a
# pin called SD_CS:
#cs = board.SD_CS

print ('done with SPI')
print('------------')

mp3files = []

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
        else:
            if file.lower().endswith("mp3"):
                mp3files.append(path + "/" + file)

sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)


print ('initialized storage')
print('------------')

storage.mount(vfs, "/sd")
print ('mounted storage')
print('------------')

print("Files on filesystem:")
print("====================")
print_directory("/sd")

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

from audiomp3 import MP3Decoder


print('mp3 files: ')
#print(mp3files)



# You have to specify some mp3 file when creating the decoder
mp3 = open(mp3files[0], "rb")

decoder = MP3Decoder(mp3)
audio = AudioOut(board.A0, right_channel=board.A1)

#sr = decoder.sample_rate
#print("Sample Rate")
#print(sr)

# SJW MIXER TESTING
mixer = audiomixer.Mixer(voice_count=1, sample_rate=44100, channel_count=2,
                         bits_per_sample=16, samples_signed=True)
print('*******')
print('Done with mixer--')
#------

#mixer.voice[0].level = 0.5
audio.play(mixer)


while True:
    for filename in mp3files:
        print("Playing", filename)
        
        # Updating the .file property of the existing decoder
        # helps avoid running out of memory (MemoryError exception)
        decoder.file = open(filename, "rb")

        #audio.play(decoder)  # SJW TEST works
        # TEST

        mixer.voice[0].play(decoder)
        mixer.voice[0].level = 0.05
        
        # This allows you to do other things while the audio plays!
        #while audio.playing:
         #   time.sleep(1)
        time.sleep(60)

print('showd pixels')
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

while True:
    pixels.fill(RED)
    pixels.show()
    print('r')
    time.sleep(0.5)
    pixels.fill(BLUE)
    pixels.show()
    print('b')
    time.sleep(0.5)



while True:
    pixels.fill(RED)
    pixels.show()
    # Increase or decrease to change the speed of the solid color change.
    time.sleep(1)
    pixels.fill(GREEN)
    pixels.show()
    time.sleep(1)
    pixels.fill(BLUE)
    pixels.show()
    time.sleep(1)

    color_chase(RED, 0.1)  # Increase the number to slow down the color chase
    color_chase(YELLOW, 0.1)
    color_chase(GREEN, 0.1)
    color_chase(CYAN, 0.1)
    color_chase(BLUE, 0.1)
    color_chase(PURPLE, 0.1)
    print('.')
    rainbow_cycle(0)  # Increase the number to slow down the rainbow
1

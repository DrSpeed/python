import board
import busio
import sdcardio
import storage
import os
import audiomixer
import time
import random
import gc
import digitalio
import neopixel


# NEOPIXEL

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)


def neoYellow():
    pixels.fill((1, 1, 0))    

def neoOff():
    pixels.fill((0, 0, 0, 0))

def neoRed():
    pixels.fill((1, 0, 0))    
        


spi = busio.SPI(board.SD_SCK, MOSI=board.SD_MOSI, MISO=board.SD_MISO)
cs = board.SD_CS

sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")


print("--------------")
print("Mounted Filesystem")
print("--------------")


ID_FILE    = "/sd/ids.txt"
INDEX_FILE = "/sd/index.txt"

def isMp3(fn):
    if fn.lower().endswith("mp3"):
        return True
    else:
        return False

# global file handle that gets used in recursive index file
indexFile = None
idFile = None

def countIdLines():
    fname = ID_FILE
    count = 0
    with open(fname, 'r') as f:
        for line in f:
            count += 1
    return count

def getIdFileName(lineNo):
    print('getting id file name' + str(lineNo))
    fname = ID_FILE
    count = 0
    with open(fname, 'r') as f:
        for line in f:
            if count >= lineNo:
                return line
            count += 1

# Write both index files
def writeIndecies():

    print('writing ID file index')
    idFile = open(ID_FILE, "w")
    writeIndex("/sd/ids", idFile )
    idFile.close()

    print('writing music file index')
    indexFile = open(INDEX_FILE, "w")
    writeIndex("/sd", indexFile )
    indexFile.close()
    print('done writing music index')

def countIndexLines():
    fname = INDEX_FILE
    count = 0
    with open(fname, 'r') as f:
        for line in f:
            count += 1
    return count

def getFileName(lineNo):
    fname = INDEX_FILE
    count = 0
    with open(fname, 'r') as f:
        for line in f:
            if count >= lineNo:
                return line
            count += 1

def writeIndex(path, fileObject):

    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        isdir = stats[0] & 0x4000

        if isdir:
            writeIndex(path + "/" + file, fileObject)
        else:
            if (file.lower().startswith(".") == False) and file.lower().endswith("mp3"):
                #print('writing ' + path + "/" + file)
                fileObject.write(path + "/" + file + '\n')

from audiomp3 import MP3Decoder

print('writing index file..')
neoOff()
neoYellow()
writeIndecies()
fileLines =  countIndexLines()
idLines = countIdLines()

print('ID LINES: ' + str(idLines))
print('MUSIC LINES: ' + str(fileLines))

neoOff()

print('getting a test filename')
fileNo = round( random.random() * fileLines )
fn = getFileName(fileNo)
print('got # '+ str(fileNo) + '--->'  + fn)
print('done writing index file')


mp3File = fn

# You have to specify some mp3 file when creating the decoder
mp3 = open(mp3File, "rb")

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

decoder = MP3Decoder(mp3)
audio = AudioOut(board.A0, right_channel=board.A1)

#sr = decoder.sample_rate
#print("Sample Rate")
#print(sr)

def getRandIndex(maxVal):
    return round(random.random() * maxVal)

nSongsPlayed = 0
while True:
    try:
        # ID File
        neoYellow()
        #print('getting ID File')
        fileNo = round( random.random() * idLines )
        fn = getIdFileName(fileNo)
        print('ID File: ' + fn)
        neoOff()
        # helps avoid running out of memory (MemoryError exception)
        decoder.file = open(fn, "rb")
        audio.play(decoder) 
        # This allows you to do other things while the audio plays!
        while audio.playing:
            time.sleep(0.5)
            
        # MUSIC FILE
        neoYellow()
        fileNo = round( random.random() * fileLines )
        fn = getFileName(fileNo)
        print('got # '+ str(fileNo) + '--->'  + fn)

        # helps avoid running out of memory (MemoryError exception)
        decoder.file = open(fn, "rb")
        audio.play(decoder) 
        # This allows you to do other things while the audio plays!
        neoOff()
        while audio.playing:
            time.sleep(0.5)
    except:
        neoRed()
        print('Error playing file')



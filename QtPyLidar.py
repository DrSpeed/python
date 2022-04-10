import time
import adafruit_dotstar
import board
import neopixel
import random
import board
import busio
import adafruit_dotstar


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)



pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

uart = busio.UART(board.TX, board.RX, baudrate=115200)




def showColor(c):
    pixels[0] = c
    pixels.show()

print('Starting LIDAR program')

                               
while(True):
    data = uart.read(18)

    for x in range(9):
        if data[x] == 0x59 and data[x+1] == 0x59:
            if data[x + 7] == 0x59 or data[x + 8] == 0x59:
                break
            dst  = data[x+2] + data[x+3]*256 # distance in next two bytes

            if dst < 10:
                showColor(RED)
            elif dst < 50:
                showColor(YELLOW)
            elif dst < 200:
                showColor(GREEN)
            else :
                showColor(BLUE)
            

            strn = data[x+4] + data[x+5]*256 # signal strength in next two bytes

            # debugging code
            if True:
                continue
            
            print('D: ' + str(dst), end=', ')
            print('S: ' + str(strn))
            for y in range(9):
                b = data[x+y]
                print(hex(b), end=' ')
            print('')
            for y in range(9):
                b = data[x+y]
                print(int(b), end=' ')

            print('')
            print('')
            

    time.sleep(0.1)



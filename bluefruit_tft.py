
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
import microcontroller
import busio
import board
import time
from math import sin, cos, atan2, degrees
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33

import adafruit_l3gd20
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import adafruit_lis3mdl

from adafruit_circuitplayground import cp


from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon

print('starting')

COMPASS_X = 180
COMPASS_Y = 120
COMPASS_R = 30

# Does not work on this microcontroller
#I2C = busio.I2C(board.SCL, board.SDA)

I2C = busio.I2C(board.A2, board.A1) # Monkey around until you get a pair
print('got I2c')
sensor = LSM6DS33(I2C)
mag = adafruit_lis3mdl.LIS3MDL(I2C)

#gyro = adafruit_l3gd20.L3GD20_I2C(I2C)
#mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(I2C)
#mag = adafruit_lsm303dlh_mag.LIS3MSM303DLH_Mag(I2C)
#accel = adafruit_lsm303_accel.LSM303_Accel(I2C)

#accel.range = adafruit_lsm303_accel.Range.RANGE_2G
#accel.mode = adafruit_lsm303_accel.Mode.MODE_HIGH_RESOLUTION

print('got all I2c stuff')

def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle

def vector_2_rad(x, y):
    angle = atan2(y, x)
    return angle

def get_heading_rad(_sensor):
    magnet_x, magnet_y, _ = _sensor.magnetic
    return vector_2_rad(magnet_x, magnet_y)

def get_heading(_sensor):
    magnet_x, magnet_y, _ = _sensor.magnetic
    return vector_2_degrees(magnet_x, magnet_y)


# Create the TFT Gizmo display, global, there's only one
display = tft_gizmo.TFT_Gizmo()

# Make the display context
splash = displayio.Group(max_size=20)
display.show(splash)

#
#  Draw (lines) the bounding box of text area
#
def drawTextBb(textArea, grp, clr):
    dims = textArea.bounding_box  # returns/assigns tuple
    drawRect (dims[0], dims[1], dims[2]+2, dims[3], clr, grp)

#
# Get the accelerometer field, formatted for display
#
def getFormattedAcces(ax):
    s = '%.3f' % ax
    if ax >= 0.0:
        return ' ' + s
    else:
        return s

def getAccelText():
    x, y, z = cp.acceleration
    xstr = getFormattedAcces(x)
    ystr = getFormattedAcces(y)
    zstr = getFormattedAcces(z)

    txt = ' X:' + xstr + '\n Y:' + ystr + '\n Z:' + zstr
    return txt
 
def getLight():
    return 'LightSensor: ' + str(cp.light)

def getMag():
        return("{:.2f}'".format(get_heading(mag)))
        #return "%0.2f\n%0.2f\n%0.2f"%mag.magnetic

#
# Draw a line (unfilled) rectangle.
# There's probably a better way, and this uses up the child space, but hey, it works.
#
def drawRect(x, y, w, h, color, gp):
    l = Line(x,   y, x+w, y,   color)
    gp.append(l)
    l = Line(x+w, y, x+w, y+h, color)
    gp.append(l)
    l = Line(x+w, y+h, x, y+h, color)
    gp.append(l)
    l = Line(x, y+h, x, y, color)
    gp.append(l)

def drawCircle(x, y, r, phil, edge, group):
    #c = Circle(x, y, r, phil, edge, 1)
    circle = Circle(x, y, r, fill=phil, outline=edge)
    group.append(circle)

color_bitmap = displayio.Bitmap(240, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x550000  # outer

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle/sprite 
inner_bitmap = displayio.Bitmap(200, 200, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x333333  # inner
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=20, y=20)
splash.append(inner_sprite)

def makeTextLabel(txt, xL, yL, clr, frameIt = False):
    tlbl = label.Label(terminalio.FONT, text=txt, color=clr)
    tgrp = displayio.Group(max_size=10, scale=2, x=xL, y=yL)
    tgrp.append(tlbl)
    # the order of appends is important here, we assume the label is [0]
    if frameIt:
        drawTextBb(tlbl, tgrp, 0xFFFF00)
    return tgrp

text_group = makeTextLabel('Hello', 30, 35, 0xDDDD00)
splash.append(text_group)

# ACCELEROMETER---------------------------
txt = getAccelText()
x_group = makeTextLabel(txt, 30, 80, 0xFFFF00, frameIt=True)
splash.append(x_group)

# LIGHT---------------------------
txt = getLight()
l_group = makeTextLabel(txt, 30, 200, 0x00DDDD, frameIt=False)
splash.append(l_group)


txt = getMag()
m_group = makeTextLabel(txt, 150, 80, 0x00DDDD, frameIt=False)
splash.append(m_group)


# Red ornaments-------
drawRect(20, 20, 200, 200, 0xFF0000, splash)
drawRect(0, 0, 239, 239, 0xDD0000, splash)    


COMPASS_OUTER = 0x00BB00
COMPASS_CROSS = 0x008800
drawCircle(COMPASS_X, COMPASS_Y, COMPASS_R,  0x005500, COMPASS_OUTER, splash)
drawCircle(COMPASS_X, COMPASS_Y, COMPASS_R+2,  None, COMPASS_OUTER, splash)
drawCircle(COMPASS_X, COMPASS_Y, 2,  None, COMPASS_OUTER, splash)
cl = Line(COMPASS_X - COMPASS_R, COMPASS_Y, COMPASS_X + COMPASS_R, COMPASS_Y, COMPASS_CROSS)
splash.append(cl)
cl = Line(COMPASS_X, COMPASS_Y-COMPASS_R, COMPASS_X, COMPASS_Y+COMPASS_R , COMPASS_CROSS)
splash.append(cl)
# just add a line here so the pop() call elsewhere has something to pop()
X = round(COMPASS_R*cos(0) + COMPASS_X)
Y = round(COMPASS_R*sin(0) + COMPASS_Y)
cl = Line(COMPASS_X, COMPASS_Y, X, Y, 0xFFFFFF)
#print(str(X) + ' ' + str(Y))
splash.append(cl)

def updateCompass(deg):
    X = round(COMPASS_R*cos(deg) + COMPASS_X)
    Y = round(COMPASS_R*sin(deg) + COMPASS_Y)
    #print(str(X) + ' ' + str(Y))
    cl = Line(COMPASS_X, COMPASS_Y, X, Y, 0xFFFF00)
    splash.pop()
    splash.append(cl)


lastTime = time.monotonic()
while True:
    # splash is a Group
    # bg_sprite is a TileGrid
    # text_group is a Group
    # text_area is a Label
    # splash has text_group has text_area
    nowTime = time.monotonic()
    if (nowTime != lastTime):
        #text_group.remove(text_area)
        text =  'CPU: ' +str(microcontroller.cpu.temperature) + 'C'

        #text = str(nowTime)
        text_area = label.Label(terminalio.FONT, text=text, color=0x0000FF)
        text_group[0] = text_area
        
        txt = getAccelText()
        xtext_area = label.Label(terminalio.FONT, text=txt, color=0xFFFF00)   
        x_group[0] = xtext_area

        txt = getLight()
        ltext_area = label.Label(terminalio.FONT, text=txt, color=0x00FFDD)   
        l_group[0] = ltext_area

        txt = getMag()
        ltext_area = label.Label(terminalio.FONT, text=txt, color=0x00FFDD)   
        m_group[0] = ltext_area

        updateCompass(get_heading_rad(mag))

        lastTime = nowTime

        
    time.sleep(0.5)













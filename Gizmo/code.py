
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
import microcontroller

import time

from adafruit_circuitplayground import cp

from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon

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


barBg = 0x000033
barFg = 0x0000DD
barOl = 0xFF0000
barGraph = displayio.Group(max_size=30, x=170, y=40)
rectb = Rect(0, 0, 40, 100, fill=barBg, outline=barOl)
rectf = Rect(0, 0, 40, 50, fill=barFg)
barGraph.append(rectb)
barGraph.append(rectf)
splash.append(barGraph)


# Red ornaments-------
drawRect(20, 20, 200, 200, 0xFF0000, splash)
drawRect(0, 0, 239, 239, 0xDD0000, splash)    

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
        
        lastTime = nowTime

    time.sleep(1.0)













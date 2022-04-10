
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo

import time

from adafruit_circuitplayground import cp

from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon

# Create the TFT Gizmo display
display = tft_gizmo.TFT_Gizmo()

# Make the display context
splash = displayio.Group(max_size=20)
display.show(splash)

def getAccelText():
    x, y, z = cp.acceleration
    txt = ' X:' + str(x) + '\n Y:' + str(y) + '\n Z:' + str(z)
    return txt

def getLight():
    return 'Light: ' + str(cp.light)

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

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(200, 200, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x444444  # inner
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=20, y=20)
splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(max_size=10, scale=2, x=30, y=35)
text = "Steve W\nprogrammed\nthis"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)   
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# ACCELEROMETER---------------------------
x_group = displayio.Group(max_size=10, scale=2, x=30, y=80)
txt = getAccelText()
xtext_area = label.Label(terminalio.FONT, text=txt, color=0xFFFF00)   
x_group.append(xtext_area)  # Subgroup for text scaling

splash.append(x_group)

# LIGHT---------------------------
l_group = displayio.Group(max_size=10, scale=2, x=30, y=200)
txt = getLight()
ltext_area = label.Label(terminalio.FONT, text=txt, color=0xFFFF00)   
l_group.append(ltext_area)  # Subgroup for text scaling
splash.append(l_group)


drawRect(20, 20, 200, 200, 0xFF0000, splash)
drawRect(0, 0, 239, 239, 0xFF0000, splash)    


def bb(ta, g, c):
    dims = ta.bounding_box
    drawRect (dims[0], dims[1], dims[2]+2, dims[3], c, g)

bb(xtext_area, x_group, 0xFFFF00)
    

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
        text = str(nowTime)
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
        #text_group.append(text_area)
        text_group[0] = text_area



        
        txt = getAccelText()
        xtext_area = label.Label(terminalio.FONT, text=txt, color=0xFFFF00)   
        x_group[0] = xtext_area

        txt = getLight()
        ltext_area = label.Label(terminalio.FONT, text=txt, color=0xFFFF00)   
        l_group[0] = ltext_area
        
        lastTime = nowTime

    time.sleep(1.0)

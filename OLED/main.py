import time
import board
import adafruit_ssd1306
import busio as io


# Adafruit M0 Feather
# Initialize I2C and OLED device
i2c = io.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3D)


print('test')

oled.fill(1)
oled.show()

time.sleep(2.0)

oled.fill(0)
oled.show()

oled.pixel(0, 0, 1)
oled.show()

oled.text('Hello', 10, 10, 0)




oled.show()

while True:
    print('x')
    oled.fill(0)
    oled.line(0, 0, 127, 0, 1)
    oled.line(127, 0, 127, 64, 1)
    s = str(time.monotonic())
    oled.text(s, 20, 10, 1)    
    oled.show()

    time.sleep(1.0)

# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import datetime
import os
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)


# Define Input pins:
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP
press_A = False

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP
press_B = False

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP
press_L = False

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP
press_R = False

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP
press_U = False

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP
press_D = False

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP
press_C = False


# Define commands for sub process 
my_env = os.environ.copy()
my_env['AUDIODEV'] = 'hw:X18XR18,0'
record_command = ['rec', '-q', '--buffer', '262144', '-c', '18', '-b', '24']
path_str = '/media/pi/ExternalSSD'
ls_command = ['ls', path_str]
mount_command = ['sudo', '/usr/bin/mount', '/dev/sda1', path_str]
umount_command = ['sudo', '/usr/bin/umount', '/dev/sda1']
record_file = '%s/%s.caf' % \
    (path_str, datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
#record_proc = subprocess.Popen(record_command + [record_file], env = my_env)
#rec_proc.terminate()


# Setup the LCD and drawing environment
# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load the default font for text
font = ImageFont.load_default()
# Get the width and height of the text in pixels
def getfontsize(font, text):
    # Calculate the size of the text in pixels
    left, top, right, bottom = font.getbbox(text)
    return right - left, bottom - top
text = "Hello World!"
(font_width, font_height) = getfontsize(font, text)


# Define the text to be displayed
def getLS(list):
    result = subprocess.run(ls_command, capture_output=True, text=True)
    err_str = result.stdout
    print(result.stderr)
    text = result.stdout
    if len(err_str) > 0:
        result = subprocess.run(umount_command, capture_output=True, text=True)
        print(result.stderr)
        text = None
    if text == '' or text == None or len(text) == 0:
        print("running mount")
        result = subprocess.run(mount_command, capture_output=True, text=True)
        print(result.stderr)
        result = subprocess.run(ls_command, capture_output=True, text=True)
        text = result.stdout
    return text.splitlines()

# Draw 6 lines of text to the screen
def drawText(text, offset, shift):
    pos = 0
    lines = len(text)
    print("%s %s %s" % (text, offset, lines))
    for line in range(6):
        if lines ==0 or (line+offset > lines):
            return
        draw.text((0, pos), text[line+offset][shift:], font=font, fill=255,)
        print(text[line+offset][shift:])
        pos = pos + font_height


redraw = True   # if true blank and redraw the screen
offset = 0      # starting line of output
shift = 0       # number of characters to shift
text = getLS(True)

A = 0
B = A + 3
C = B + 2 # 4
D = C + 2 # 6
E = D + 2 # 8
F = E + 2 # 9
G = F + 3 # 12
X_off = width - G
Y_off = 5
U_pos = [(C+X_off, B+Y_off), (D+X_off, A+Y_off), (E+X_off, B+Y_off)]
D_pos = [(D+X_off, G+Y_off), (E+X_off, F+Y_off), (C+X_off, E+Y_off)]

while True:
    if redraw:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        drawText(text, offset, shift)
        redraw = False

    # x,y left middle right
    if button_U.value:  # button is released
        draw.polygon(U_pos, outline=255, fill=0)  # Up
        if press_U:
            if offset > 0:
                offset -= 1
            redraw = True
            press_U = False
    else:  # button is pressed:
        draw.polygon(U_pos, outline=255, fill=1)  # Up filled
        press_U = True

    # middle, right, left
    if button_D.value:  # button is released
        draw.polygon(D_pos, outline=255, fill=0)  # down
        if press_D:
            if offset < len(text) - 6:
                offset += 1
            redraw = True
            press_D = False
    else:  # button is pressed:
        draw.polygon(D_pos, outline=255, fill=1)  # down filled
        press_D = True

    # middle, top, bottom
    if button_L.value:  # button is released
        draw.polygon([(A+X_off, D+Y_off), (B+X_off, C+Y_off), (B+X_off, E+Y_off)], outline=255, fill=0)  # left
        if press_L:
            if shift > 0:
                shift -= 1
            redraw = True
            press_L = False
    else:  # button is pressed:
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  # left filled
        press_L = True

    # middle, top, bottom
    if button_R.value:  # button is released
        draw.polygon([(G+X_off, D+Y_off), (F+X_off, C+Y_off), (F+X_off, E+Y_off)], outline=255, fill=0)  # right
        if press_R:
            shift += 1
            redraw = True
            press_R = False
    else:  # button is pressed:
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1)  # right filled
        press_R = True

    if button_C.value:  # button is released
        draw.rectangle((C+X_off, C+Y_off, E+X_off, E+Y_off), outline=255, fill=0)  # center
        if press_C:
            shift = 0
            offset = 0
            redraw = True
            press_C = False
            text = getLS(True)
    else:  # button is pressed:
        draw.rectangle((20, 22, 40, 40), outline=255, fill=1)  # center filled
        press_C = True

    # x_min, y_min, x_max, y_max, origin is upper left
    if button_A.value:  # Lower/left button is released
        draw.ellipse((115, 53, 125, 63), outline=255, fill=0)  # A button
    else:  # button is pressed:
        draw.ellipse((115, 53, 125, 63), outline=255, fill=1)  # A button filled

    if button_B.value:  # Upper/right button is released
        draw.ellipse((115, 40, 125, 50), outline=255, fill=0)  # B button
    else:  # button is pressed:
        draw.ellipse((115, 40, 125, 50), outline=255, fill=1)  # B button filled

    if not button_A.value and not button_B.value and not button_C.value:
        catImage = Image.open("happycat_oled_64.ppm").convert("1")
        disp.image(catImage)
    else:
        # Display image.
        disp.image(image)

    disp.show()


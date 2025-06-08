# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import datetime
import time
import os
import board
import time
#import displayio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735
import subprocess

# Set Text Attributes
FONTSIZE = 14
MAX_LINES = 8

# Create the SPI interface.
spi = board.SPI()
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D27)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

disp = st7735.ST7735R(spi, rotation=270, height=128, width=128, x_offset=2, y_offset=3,   # 1.44" ST7735R
    cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE,
)

# Define Input pins:
button_1 = DigitalInOut(board.D21)
button_1.direction = Direction.INPUT
button_1.pull = Pull.UP
press_1 = False

button_2 = DigitalInOut(board.D20)
button_2.direction = Direction.INPUT
button_2.pull = Pull.UP
press_2 = False

button_3 = DigitalInOut(board.D16)
button_3.direction = Direction.INPUT
button_3.pull = Pull.UP
press_3 = False

button_L = DigitalInOut(board.D5)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP
press_L = False

button_R = DigitalInOut(board.D26)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP
press_R = False

button_U = DigitalInOut(board.D6)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP
press_U = False

button_D = DigitalInOut(board.D19)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP
press_D = False

button_C = DigitalInOut(board.D13)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP
press_C = False


# Define commands for sub process 
my_env = os.environ.copy()
my_env['AUDIODEV'] = 'hw:X18XR18,0'
# requires sox, apt install sox libsox-fmt-all
record_command = ['rec', '-q', '-c', '18', '-b', '24', '--buffer', '262144']
path0_str = '/media/pi/ExternalSSD'
path1_str = '/media/pi/ExternalSSD1'
if os.path.exists(path1_str):
    path_str = path1_str
else:
    path_str = path0_str
ls_command = ['ls', path_str]
mount_command = ['sudo', '/usr/bin/mount', '/dev/sda1', path_str]
umount_command = ['sudo', '/usr/bin/umount', '/dev/sda1']
record_proc = None


# Setup the LCD and drawing environment
# Clear display.
disp.fill(0)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load the default font for text
# Load a TTF Font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
# Get the width and height of the text in pixels
def getfontsize(font, text):
    # Calculate the size of the text in pixels
    left, top, right, bottom = font.getbbox(text)
    return right - left, bottom - top
text = "Hello World! 2025"
(font_width, font_height) = getfontsize(font, text)


# Define the text to be displayed
def getLS(list):
    result = subprocess.run(ls_command, capture_output=True, text=True)
    err_str = result.stderr.rstrip()
    text = result.stdout
    if len(err_str) > 0:
        print("umount")
        result = subprocess.run(umount_command, capture_output=True, text=True)
        path_str = path0_str
        print(result.stderr.rstrip())
        text = None
    if text == '' or text == None or len(text) == 0:
        if os.path.exists(path1_str):
            path_str = path1_str
        else:
            path_str = path0_str
        print("running mount")
        result = subprocess.run(mount_command, capture_output=True, text=True)
        print(result.stderr.rstrip())
        result = subprocess.run(ls_command, capture_output=True, text=True)
        text = result.stdout
        print(text.rstrip())
    return text.splitlines()

# Draw 6 lines of text to the screen
def drawText(text, offset, shift):
    pos = 0 #+ 2 * font_height
    lines = len(text)
#    print("%s %s %s" % (text, offset, lines))
    for line in range(MAX_LINES):
        if lines ==0 or (line+offset >= lines):
            break
        # draw the file names green
        draw.text((0, pos), text[line+offset][shift:], font=font, fill=(0,255,0),)
        draw.text((0, pos), text[line+offset][shift:], font=font, fill=(0,255,0),) # make it bold
#        print(text[line+offset][shift:])
        # overlay the size of the file in blue
        du_cmd = '/usr/bin/du', '-sh', '%s/%s' % (path_str, text[line+offset])
        line_size = subprocess.run(du_cmd, capture_output=True, text=True).stdout.rstrip().split()[0]
#        print(line_size)
        size_width = draw.textlength(line_size, font)
        draw.text((width - size_width,pos), line_size, font=font, fill=(0,0,255),)        
        # update to support next version of Pillow
#        pos += font.getsize(text[line+offset])[1]
        pos += font.getbbox(text[line+offset])[3]
    # get the size of the filesystem
    df_cmd = '/usr/bin/df', '-h', path_str
    fs_size_output = subprocess.run(df_cmd, capture_output=True, text=True).stdout.rstrip().split()
    fs_line = '%s %s ' % (fs_size_output[11],fs_size_output[10])
#    print(fs_line)
    size_width = draw.textlength(fs_line, font)
    draw.text((0,pos), fs_line, font=font, fill=(0,0,255),)
    draw.text((0,pos), fs_line, font=font, fill=(0,0,255),)
    height = font.getbbox(fs_line)[3]
    if record_proc == None:
        draw.rectangle((size_width, pos+1, size_width+height/4, pos+height-1), 
                    outline=(0,255,0), fill=(0,255,0))
        draw.rectangle((size_width+height/2, pos+1, size_width+3*height/4, pos+height-1), 
                    outline=(0,255,0), fill=(0,255,0))
    else:
        draw.polygon([(size_width,pos+1),(size_width,pos+height-1),(size_width+2*height/3,pos+height/2)],
                     outline=(255,0,0), fill=(255,0,0))
        size_width += height
        time_cmd = '/usr/bin/ps', 'p', '%s' % record_proc.pid, '-o', 'etime'
        time_output = subprocess.run(time_cmd, capture_output=True, text=True).stdout.rstrip().split()[1]
        print(time_output)
        draw.text((size_width,pos), time_output, font=font, fill=(255,0,0),)

redraw = True   # if true blank and redraw the screen
offset = 0      # starting line of output
shift = 0       # number of characters to shift
text = getLS(True)
redraw_time = 0

while True:
    if time.time() > redraw_time + 1:
        redraw = True
    if redraw:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        drawText(text, offset, shift)
        redraw = False
        redraw_time = int(time.time())

    if button_U.value:  # button is released
        if press_U:
            if offset > 0:
                offset -= 1
            redraw, press_U = True, False
    else:  # button is pressed:
        press_U = True

    if button_D.value:  # button is released
        if press_D:
            if offset < len(text) - MAX_LINES:
                offset += 1
            redraw, press_D = True, False
    else:  # button is pressed:
        press_D = True

    if button_L.value:  # button is released
        if press_L:
            if shift > 0:
                shift -= 1
            redraw, press_L = True, False
    else:  # button is pressed:
        press_L = True

    if button_R.value:  # button is released
        if press_R:
            shift += 1
            redraw, press_R = True, False
    else:  # button is pressed:
        press_R = True

    if button_C.value:  # button is released
        if press_C:
            shift, offset = 0, 0
            redraw, press_C = True, False
            text = getLS(True)
            time.sleep(0.5)
    else:  # button is pressed:
        press_C = True

    # x_min, y_min, x_max, y_max, origin is upper left
    if button_1.value:  # Lower/left button is released
        draw.ellipse((115, 53, 125, 63), outline=(255,0,0), fill=(0,0,0))  # A button
    else:  # button is pressed:
        draw.ellipse((115, 53, 125, 63), outline=(255,0,0), fill=(255,255,255))  # A button filled
        if record_proc == None:
            record_file = '%s/%s.caf' % \
                (path_str, datetime.datetime.now().strftime("%y-%m-%d-%H%M%S"))
            record_proc = subprocess.Popen(record_command + [record_file], env = my_env)
            time.sleep(1)
            print("record started")
            redraw = True
            text = getLS(True)

    if button_2.value:  # Upper/right button is released
        draw.ellipse((115, 40, 125, 50), outline=(0,255,0), fill=(0,0,0))  # B button
    else:  # button is pressed:
        draw.ellipse((115, 40, 125, 50), outline=(0,255,0), fill=(255,255,255))  # B button filled

    if button_3.value:  # Upper/right button is released
        draw.ellipse((115, 27, 125, 37), outline=(0,0,255), fill=(0,0,0))  # B button
    else:  # button is pressed:
        draw.ellipse((115, 27, 125, 37), outline=(0,0,255), fill=(255,255,255))  # B button filled

    if not button_2.value and not button_3.value:
        catImage = Image.open("happycat_oled_64.ppm")
        if record_proc != None:
            record_proc.terminate()
            record_proc = None
            print("Recording stopped")
            redraw = True
        disp.image(catImage)
    else:
        # Display image.
        disp.image(image)

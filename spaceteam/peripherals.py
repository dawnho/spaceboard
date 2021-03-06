#!/usr/bin/env python2.7
"""
Initializes and provides access to board peripherals
"""

import atexit
import smbus
import time

# initialize GPIO
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
atexit.register(GPIO.cleanup)

# all pin numbers are BOARD
RESET_PIN = 36

# handling i2c resets
I2C_ALL_CALL = 0x0 # all call address -- goes to all devices (that support it)
I2C_SOFT_RESET = 0x06 # all devices reset
def all_call_reset(bus):
  bus.write_byte(I2C_ALL_CALL, I2C_SOFT_RESET)

# initialize I2C
BUS_ID = 1
_SMBUS = smbus.SMBus(BUS_ID)

# these pins are not used in the code, just here for reference
SMBUS_SDA_PIN = 03
SMBUS_SCL_PIN = 05

from ads1115 import ADS1115
ANALOG1 = ADS1115(_SMBUS, 0x48)

from mcp23017 import MCP23017
MCP22 = MCP23017(_SMBUS, 0x22)
MCP23 = MCP23017(_SMBUS, 0x23)
MCP24 = MCP23017(_SMBUS, 0x24)
MCP25 = MCP23017(_SMBUS, 0x25)
MCP26 = MCP23017(_SMBUS, 0x26)
MCP27 = MCP23017(_SMBUS, 0x27)

INPUTS = [
    MCP22,
    MCP23,
    MCP24,
    MCP25,
    MCP26,
    MCP27,
    ANALOG1,
    ]

# initialize microcontroller
from microcontroller import Microcontroller
MAPLE = Microcontroller("/dev/serial0")

# these pins are not used in the code, just here for reference
MICROCONTROLLER_TX_PIN = 8
MICROCONTROLLER_RX_PIN = 10

# display pins and setup
DISPLAY_DC_PIN = 29           # harness pin 3 (1 is PWR, 2 is GND)
DISPLAY_SCLK_PIN = 23         # pin 4
DISPLAY_MOSI_PIN = 19         # pin 5  these pins are port 0
DISPLAY_CE_PIN = 24           # harness pin 6; this is CE0, so we get device 0
DISPLAY_RESET_PIN = RESET_PIN # pin 7; we pass NONE to device since we do reset ourselves

from ssd1325 import SSD1325
DISPLAY = SSD1325(gpio = GPIO, gpio_DC = 29, gpio_RST = None)

from progress import Progress
PROGRESS = Progress(MAPLE)

OUTPUTS = [
    PROGRESS,
    MAPLE,
    DISPLAY,
    ]

from sound_player import SoundPlayer
SOUNDS = SoundPlayer()

ALL = INPUTS + OUTPUTS
def read_all():
  for p in ALL:
    p.communicate()

def toggle_reset():
  GPIO.setup(RESET_PIN, GPIO.OUT)
  GPIO.output(RESET_PIN, 0)
  time.sleep(0.1)
  GPIO.output(RESET_PIN, 1)

def reset_all():
  """resets all peripherals"""
  toggle_reset()

  # initialize the display
  DISPLAY.reset()

  # reset the MAPLE
  MAPLE.reset()
  tries = 0
  while tries < 3:
    time.sleep(0.1)
    try:
      MAPLE.get_state()
    except:
      tries += 1
    else:
      break

  # re-initalize any mcp port expanders
  mcps = [p for p in INPUTS if type(p) == MCP23017]
  for mcp in mcps:
    mcp.reset()

  # reset any ADC devices
  adcs = [p for p in INPUTS if type(p) == ADS1115]
  if len(adcs) > 0:
    all_call_reset(_SMBUS)

    # send config to any devices
    for adc in adcs:
      adc.reset()

  DISPLAY.message = 'READY!'
  SOUNDS.set_music('ambient')

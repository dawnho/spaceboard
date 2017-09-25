#!/usr/bin/env python2.7

import spaceteam
from spaceteam import MCP23017
from spaceteam import RPi

import sys
import time

def main(args):
  pi = RPi()
  pi.reset_peripherals()

  mcp1 = MCP23017(0x20)
  mcp1.set_as_output(15)
  mcp1.set_as_output(14)

  mcp1.write(15, 1)
  time.sleep(2)
  mcp1.write(14, 1)
  time.sleep(2)
  mcp1.write(15, 0)
  time.sleep(2)
  mcp1.write(14, 0)
  time.sleep(2)

  print args
  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
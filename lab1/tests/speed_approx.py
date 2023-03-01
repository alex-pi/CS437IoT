import picar_4wd as fc
import time
import sys

MAX_POWER = 5
TURN_POWER = 30
TOTAL_TURN_TIME = 5.8

direction = sys.argv[1]

if direction == 'f':
	print("Move forward")
	fc.forward(MAX_POWER)
	time.sleep(1)
	fc.stop()

if direction == 'b':
	print("Move backward")
	fc.backward(MAX_POWER)
	time.sleep(1)
	fc.stop()
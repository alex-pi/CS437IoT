import picar_4wd as fc
import time

MAX_POWER = 30
TURN_POWER = 20
TOTAL_TURN_TIME = 5.3

#print("Move forward")
#fc.forward(MAX_POWER)
#time.sleep(3)
#fc.stop()
#
#print("Move backward")
#fc.backward(MAX_POWER)
#time.sleep(3)
#fc.stop()

print("Turn left")
fc.turn_left(TURN_POWER)
time.sleep((TOTAL_TURN_TIME / 4) + 0.5)
fc.stop()

time.sleep(1.5)

print("Turn right")
fc.turn_right(TURN_POWER)
time.sleep(TOTAL_TURN_TIME / 4)
fc.stop()

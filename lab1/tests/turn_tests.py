import picar_4wd as fc
import time


TURN_POWER = 30
# Aprox 360 turn
TOTAL_TURN_TIME = 5.8
SMALL_TURN_TIME = TOTAL_TURN_TIME / 20
TURN_MAX_FACTOR = 3

#fc.turn_left(TURN_POWER)
#time.sleep(TOTAL_TURN_TIME)
#fc.stop()

for i in range(0, 7):
	print("----------- ",  i)
	time.sleep(2)
	turn_factor = (i - TURN_MAX_FACTOR) * SMALL_TURN_TIME
	print(turn_factor)

	if turn_factor < 0:
		print("Turning left")
		fc.turn_left(TURN_POWER)
	elif turn_factor > 0:
		print("Turning right")
		fc.turn_right(TURN_POWER)
	else:
		print("Not turning")
	time.sleep(abs(turn_factor))
	fc.stop()
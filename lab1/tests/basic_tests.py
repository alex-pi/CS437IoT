import picar_4wd as fc
import time

MAX_POWER = 20
TURN_POWER = 30
TOTAL_TURN_TIME = 5.8

print("Move forward")
fc.forward(MAX_POWER)
time.sleep(2)
fc.stop()

print("Move backward")
fc.backward(MAX_POWER)
time.sleep(2)
fc.stop()

print("Turn left")
fc.turn_left(TURN_POWER)
time.sleep(TOTAL_TURN_TIME / 4)
fc.stop()

print("Turn right")
fc.turn_right(TURN_POWER)
time.sleep(TOTAL_TURN_TIME / 4)
fc.stop()

print("Test servo and ultrasonic.")
scan_list = []
while not scan_list or len(scan_list) != 10:
	# The parameter represents the min distance to keep from the object.
    scan_list = fc.scan_step(35)

# An array with status is only returned when reached 90 or -90
print(scan_list)
fc.servo.set_angle(0)
time.sleep(1)
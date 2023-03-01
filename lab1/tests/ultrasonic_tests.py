import picar_4wd as fc
import time

fc.servo.set_angle(60)
time.sleep(1)
print(fc.us.get_distance())
fc.servo.set_angle(0)
time.sleep(1)
print(fc.us.get_distance())

scan_list = []
while not scan_list or len(scan_list) != 10:
	# The parameter represents the min distance to keep from the object.
    scan_list = fc.scan_step(35)

# An array with status is only returned when reached 90 or -90
print(scan_list)
fc.servo.set_angle(0)
time.sleep(1)
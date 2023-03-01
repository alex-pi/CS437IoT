import picar_4wd as fc
import time
import sys


def get_distance_at(angle, delay=0.08):
    fc.servo.set_angle(angle)
    time.sleep(delay)
    distance = fc.us.get_distance()
    angle_distance = [angle, distance]
    print(angle_distance)
    return distance

angle = int(sys.argv[1])
#fc.servo.set_angle(angle)
#time.sleep(1)
d1 = get_distance_at(angle, delay=0.1)

print(d1)
import picar_4wd as fc
import time
import sys

ANGLE_RANGE = 180
STEP = 10
us_step = STEP
current_angle = 90
# To the left
MAX_ANGLE = ANGLE_RANGE/2
# To the right
MIN_ANGLE = -ANGLE_RANGE/2

def get_distance_at(angle, delay=0.08):
    fc.servo.set_angle(angle)
    time.sleep(delay)
    distance = fc.us.get_distance()
    angle_distance = (angle, distance)
    #print(angle_distance)
    return angle_distance

def scan_step():
    global current_angle, us_step
    #
    angle_distance = get_distance_at(current_angle)
    if current_angle >= MAX_ANGLE:
        current_angle = MAX_ANGLE
        us_step = -STEP
    elif current_angle <= MIN_ANGLE:
        current_angle = MIN_ANGLE
        us_step = STEP

    current_angle += us_step
    return angle_distance

num_steps = int(sys.argv[1])
#fc.servo.set_angle(angle)
#time.sleep(1)
for step in range(1, num_steps):
    out = scan_step()
    print(out)
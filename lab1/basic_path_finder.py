import picar_4wd as fc
import time
import random
import sys
import tty
import termios

MAX_POWER = 5
TURN_POWER = 30
TOTAL_TURN_TIME = 5.8
SMALL_TURN_TIME = TOTAL_TURN_TIME / 20
TURN_MAX_FACTOR = 3
NUM_READS = fc.ANGLE_RANGE / fc.STEP

def find_best_gap(arr, size=4, min_sum=6):
    best_pos = -1
    best_sum = -1
    iters = len(arr) - size + 1
    if iters <= 0:
        return [-1, []]
    for i in range(0, iters):
        csum = sum(arr[i:i+size])
        if csum < min_sum:
            continue
        if csum > best_sum:
            best_sum = csum
            best_pos = i

    return [best_pos, arr[best_pos:best_pos+size]]


def scan_around(min_dist=35):

    scan_list = []
    # 
    while not scan_list or len(scan_list) != NUM_READS:
        # The parameter represents the min distance to keep from the object.
        scan_list = fc.scan_step(min_dist)

    fc.servo.set_angle(0)
    time.sleep(0.6)
    print(scan_list)
    return scan_list

def backout():
    fc.backward(MAX_POWER)
    time.sleep(0.25)
    fc.stop()    

def stop_find_path():
    fc.stop()
    backout()

    while True:
        scan_result = scan_around()
        gap = find_best_gap(scan_result)
        print(gap)
        if gap[0] != -1:
            turn_factor = (gap[0] - TURN_MAX_FACTOR) * SMALL_TURN_TIME
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
            break

        fc.turn_left(TURN_POWER)
        time.sleep(SMALL_TURN_TIME)
        fc.stop()


def navigate():
    fc.servo.set_angle(90)
    time.sleep(1)

    while True:

        scan_list = fc.scan_step(35)
        if not scan_list:
            continue

        threshold1 = scan_list[3:7]
        #threshold2 = scan_list[2:8]
        print(threshold1)
        if sum(threshold1) <= 6:
            stop_find_path()
            
        else:
            fc.forward(MAX_POWER)


if __name__ == "__main__":
    try: 
        navigate()
    finally: 
        print("stop")
        fc.stop()
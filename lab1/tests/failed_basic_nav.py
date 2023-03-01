import picar_4wd as fc
import time
import random
import sys
import tty
import termios

ULTRAS_REF_POINT = 35
MAX_POWER = 10
TURN_POWER = 30
TOTAL_TURN_TIME = 5.8
SMALL_TURN_TIME = TOTAL_TURN_TIME / 20
TURN_MAX_FACTOR = 3
NUM_READS = fc.ANGLE_RANGE / fc.STEP


def backout():
    fc.backward(MAX_POWER)
    time.sleep(0.20)
    fc.stop()    


def change_direction(randomly=False):
    fc.stop()
    backout()
    turn_funcs = [fc.turn_left, fc.turn_right]

    if randomly:
        turnf = turn_funcs[random.randint(0, 1)]
    else:
        turnf = fc.turn_right

    turn_time = TOTAL_TURN_TIME / 8
    turnf(TURN_POWER)
    time.sleep(turn_time)
    fc.stop()


def navigate():
    fc.servo.set_angle(0)
    time.sleep(1)
    warn_level = 0
    powa = MAX_POWER

    while True:

        scan_list = fc.scan_step(35)
        if not scan_list:
            continue

        threshold1 = scan_list[3:7]
        #threshold2 = scan_list[2:8]
        print('Scan read: {}'.format(threshold1))
        if sum(threshold1) <= 6:
            warn_level += 1
            powa = 5
            print('Warning level increased: {}'.format(warn_level))
        else:
            warn_level = 0
            powa = MAX_POWER
            print('Good read, warning: {}'.format(warn_level))
        #if threshold1 != [2,2,2,2] and threshold1 != [1,2,2,1]:
        if warn_level > 1:
            print('Warning high, turn!: {}'.format(warn_level))
            change_direction(randomly=False)
            warn_level = 0
            powa = MAX_POWER
            
        else:
            fc.forward(powa)


if __name__ == "__main__":
    try: 
        navigate()
    finally: 
        print("stop")
        fc.stop()
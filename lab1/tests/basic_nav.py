import picar_4wd as fc
import time
import random
import sys
import tty
import termios

ULTRAS_REF_POINT = 35
MAX_POWER = 30
TURN_POWER = 30
TOTAL_TURN_TIME = 5.8


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

    while True:

        scan_list = fc.scan_step(ULTRAS_REF_POINT)
        if not scan_list:
            continue

        threshold1 = scan_list[3:7]
        #threshold2 = scan_list[2:8]
        print('Scan read: {}'.format(threshold1))
        if sum(threshold1) <= 7:
            print('Change direction!')
            change_direction(randomly=False)
            
        else:
            print('Keep going!')
            fc.forward(MAX_POWER)


if __name__ == "__main__":
    try: 
        navigate()
    finally: 
        print("stop")
        fc.stop()
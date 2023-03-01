import picar_4wd as fc
import time
import sys
from picar_4wd.speed import Speed

def get_distance_traveled(power=30, move_func=fc.forward):
    speed4 = Speed(25)
    speed4.start()
    move_func(power)
    x = 0
    for i in range(1, 10):
        time.sleep(0.1)
        speed = speed4()
        # speed x time = distance
        x += speed * 0.1
        print("%s mm"%x)
        print("%s mm/s"%speed)

    print("%s mm"%x)
    print("%s cm"%(x/10))
    speed4.deinit()
    fc.stop()

get_distance_traveled(power=int(sys.argv[1]))

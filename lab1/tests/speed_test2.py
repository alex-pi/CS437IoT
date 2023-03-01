import picar_4wd as fc
import time
import sys
from picar_4wd.speed import Speed

speed4 = Speed(25)

def get_distance_traveled(power=30, move_func=fc.forward):
    
    speed4.start()
    start_time = time.time()
    m_time = start_time
    move_func(power)
    x = 0
    speed = 0
    while (time.time() - start_time) <= 1:
        #time.sleep(0.1)
        elapse_time = time.time() - m_time
        if elapse_time > 0.1:
            speed = speed4()
            # speed x time = distance
            x += speed * elapse_time
            m_time = time.time()
            print("%s mm"%x)
            print("%s mm/s"%speed)

    print("%s mm"%x)
    print("%s cm"%(x/10))
    print("%s sec"%(time.time() - start_time))


if __name__ == "__main__":
    try: 
        get_distance_traveled(power=int(sys.argv[1]))
    except KeyboardInterrupt:
        print("stopped by User")
       # ctrl+c
    finally: 
        speed4.deinit()
        fc.stop()



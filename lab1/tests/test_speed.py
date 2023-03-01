import picar_4wd as fc
import time
from picar_4wd.speed import Speed

speed4 = Speed(4)
speed4.start()

# 100 is 51.84mm/s approx
fc.backward(100)
#fc.forward(30)

time.sleep(0.3)
speed = speed4()
time.sleep(3)

print("%smm/s"%speed)

speed4.deinit()
fc.stop()
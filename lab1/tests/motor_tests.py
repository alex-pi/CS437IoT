import picar_4wd as fc
import time

#fc.set_motor_power(1, 20)
print('left_front')
fc.left_front.set_power(20)
time.sleep(4)
fc.stop()

print('right_front')
fc.right_front.set_power(20)
time.sleep(4)
fc.stop()

print('left_rear')
fc.left_rear.set_power(20)
time.sleep(4)
fc.stop()

print('right_rear')
fc.right_rear.set_power(20)
time.sleep(4)
fc.stop()

'''for m in range(1, 5):
	fc.set_motor_power(m, -20)
	time.sleep(4)
	fc.stop()'''
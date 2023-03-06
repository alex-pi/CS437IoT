import picar_4wd as fc
from picar_4wd.utils import power_read
import time
from multiprocessing import Process, Queue
import tempfile
from utils import *


'''
Controls the main loop that decides what the car is doing.
'''
class CarController():

    def __init__(self):
        # Queue to send commands to the CarPro process
        self.cmd_q = Queue()
        # Queue where the CarPro process
        self.stats_q = Queue()
        # Process works much better than Threads in this case.
        self.car_t = Process(target=CarController.car_loop, name="CarPro",
                             args=(self.cmd_q, self.stats_q,), daemon=True)
        self.distance_traveled = 0
        self.total_distance_traveled = 0
        self.listening = False
        self.car_status = 'still'
        self.actions = {
            'forward': fc.forward,
            'backward': fc.backward,
            'stop': fc.stop,
            'left': (fc.turn_left, {'angle': 90, 'adjust_time': 0}),
            'right': (fc.turn_right, {'angle': 90, 'adjust_time': 0})
        }
        self.move_defaults = {'distance': 10, 'power': 20}

        self.metrics = {
            'distance_traveled': 0,
            'car_status': 'still'
        }

        self.TURN_POWER = 20
        # Aprox 360 turn
        self.TOTAL_TURN_TIME = 5.0

    '''
    Method with the main loop to execute commands and get information from the Car.
    TODO move this method out of this class, it does not need to be here.
    '''
    @staticmethod
    def car_loop(queue_in, queue_out):
        move_time = 0.1
        listening = True
        task = None
        while listening:
            if not queue_in.empty():
                task = queue_in.get(False)

            if task:
                # Moving should not block the loop
                if task['car_status'] == 'moving':
                    trace(task)
                    distance_traveled = 0
                    if task['time_to_travel'] <= 0.1:
                        fc.stop()
                        task['car_status'] = 'still'
                        task['distance_traveled'] = distance_traveled
                        speed = 0
                        #info("Distance traveled: %s cm"%self.distance_traveled)
                    else:
                        task['move_func'](task['power'])
                        time.sleep(move_time)
                        speed = AV_SPEED_AT[task['power']]
                        dist = speed * move_time
                        distance_traveled += dist
                        #task.total_distance_traveled += dist
                        #task.distance_to_travel -= dist
                        task['time_to_travel'] -= move_time
                        debug(f"Time to travel {task['time_to_travel']} s")
                        debug(f"Moved {dist} cms in {move_time} s")
                    queue_out.put({
                        'distance_traveled': distance_traveled,
                        'car_status': task['car_status'],
                        'current_speed': f"{speed} cm/s"
                    })
                elif task['car_status'] == 'turning':
                    # Turning blocks the loop, but that should be fine...
                    queue_out.put({
                        'car_status': task['car_status']
                    })
                    task['move_func'](task['power'])
                    time.sleep(task['turning_time'])
                    fc.stop()
                    task['car_status'] = 'still'
                    queue_out.put({
                        'car_status': task['car_status']
                    })
                elif task['car_status'] == 'stopped':
                    fc.stop()
                    task['car_status'] = 'still'
                    queue_out.put({
                        'car_status': task['car_status']
                    })
                elif task['car_status'] == 'not_listening':
                    listening = False

    def get_metrics(self):
        while not self.stats_q.empty():
            e = self.stats_q.get(False)
            self.metrics['distance_traveled'] += e.get('distance_traveled', 0)
            self.metrics['car_status'] = e['car_status']
            self.metrics['current_speed'] = e.get('current_speed', 0)

        self.metrics.update(get_sys_metrics())
        self.metrics['battery_voltage'] = power_read()

        return self.metrics

    def move(self, action='forward', params={}):
        move_params = dict(self.move_defaults)
        move_params.update(params)
        speed = AV_SPEED_AT[move_params['power']]
        time_to_travel = move_params['distance'] / speed
        info("Estimated travel time: %s s"%time_to_travel)

        self.distance_traveled = 0

        # Put a command/task in the process queue.
        self.cmd_q.put({
            'car_status': 'moving',
            'distance_to_travel': move_params['distance'],
            'time_to_travel': time_to_travel,
            'move_func': self.actions.get(action, None),
            'power': move_params['power']
        })

    def turn(self, action='right', params={}):
        turn_func = self.actions[action][0]
        turn_params = dict(self.actions[action][1])
        turn_params.update(params)
        # There should not be mapping happening while turning
        turn_time = self.TOTAL_TURN_TIME / (360 / turn_params['angle'])
        turning_time = turn_time + turn_params['adjust_time']

        # Put a command/task in the process queue.
        self.cmd_q.put({
            'car_status': 'turning',
            'turning_time': turning_time,
            'move_func': turn_func,
            'power': self.TURN_POWER
        })

    def stop(self):
        # Stop command/task to the queue
        self.cmd_q.put({
            'car_status': 'stopped',
        })

    def start(self):
        self.listening = True
        self.car_t.start()

    def finish(self):
        self.listening = False
        self.cmd_q.put({
            'car_status': 'not_listening',
        })
        debug('Car Controller loop finished.')
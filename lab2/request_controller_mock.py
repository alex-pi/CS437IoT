from utils import *
import random

class RequestControllerMock():

    def __init__(self):
        self.distance_traveled = 0

    def handle(self, message):
        cmd = message.get('cmd', None)
        params = message.get('params', {})
        debug(f'Command {cmd} received.')
        debug(f'Parameters {params}')
        response = {}
        if cmd == "forward":
            trace("Moving forward.")
        elif cmd == "backward":
            trace("Moving backward.")
        elif cmd == "left":
            trace("Turning left.")
        elif cmd == "right":
            trace("Turning right.")
        elif cmd == "stop":
            trace("Stopping car.")
        elif cmd == "metrics":
            trace("Getting metrics.")
            response = self.__mock_metrics()
        else:
            info("Command not supported")

        return response

    def __mock_metrics(self):
        self.distance_traveled += 5
        metrics = {
            'distance_traveled': self.distance_traveled,
            'car_status': random.choice(['stopped', 'moving', 'turning']),
            'current_speed': f"{random.uniform(5, 70):.1f} cm/s",
            'cpu_use': f"{random.randint(10, 99)}%",
            'free_memory': f"{random.randint(3000, 8000)} MB",
            'total_memory': "8000 MB"
        }

        return metrics

    def finish(self):
        trace('Ctrl Mock finish.')

if __name__ == '__main__':
    rcm = RequestControllerMock()
    rcm.handle({
        'cmd': 'forward',
        'params': {
            'distance': 40,
            'power': 20
        }
    })
    info(rcm.handle({
        'cmd': 'metrics'
    }))
from utils import *
import random


class RequestControllerMock():

    def __init__(self):
        self.distance_traveled = 0

    def handle(self, message):
        cmd = message.get('cmd', None)
        params = message.get('params', {})
        debug('Command {} received.'.format(cmd))
        debug('Parameters {}'.format(params))
        response = {}
        if cmd == "water":
            trace("Watering.")
        elif cmd == "schedule":
            trace("Schedule installed.")
        else:
            info("Command not supported.")

        return response


if __name__ == '__main__':
    rcm = RequestControllerMock()
    rcm.handle({
        'cmd': 'water',
        'params': {
            'ml': 40,
            'plant': 'Ronaldo'
        }
    })
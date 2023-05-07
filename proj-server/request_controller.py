from utils import *
import random
import RPi.GPIO as GPIO
import time


class RequestController():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.pin_mapping = {
            'Blanquita': [26],
            'Dolly': [6],
            'Ronaldo': [20],
        }
        self.secs_100_millis_factor = 0.035

    def handle(self, message):
        cmd = message.get('cmd', None)
        params = message.get('params', {})
        debug('Command {} received.'.format(cmd))
        debug('Parameters {}'.format(params))
        response = {}
        if cmd == "water":
            trace("Watering.")
            self.water(params)
        elif cmd == "schedule":
            # Not implemented yet.
            trace("Schedule installed.")
        else:
            info("Command not supported.")

        return response

    def water(self, params):
        # GPIO | Relay
        #--------------
        # 26     01
        # 19     02
        # 13     03
        # 06     04
        # 12     05
        # 16     06
        # 20     07
        # 21     08
        pins = self.pin_mapping[params['plant']]
        millis = params['ml']

        GPIO.setmode(GPIO.BCM)

        for p in pins:
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, GPIO.HIGH)

        # Sleep time variables
        sleepTimeShort = 0.1
        sleepTimeLong = self.__get_time(millis, len(pins))

        # MAIN LOOP =====
        # ===============
        try:
            for p in pins:
                GPIO.output(p, GPIO.LOW)
                time.sleep(sleepTimeLong)
                GPIO.output(p, GPIO.HIGH)
                time.sleep(sleepTimeShort)

        # End program cleanly with keyboard
        finally:
            GPIO.cleanup()

    def __get_time(self, millis, num_pumps):
        return self.secs_100_millis_factor * millis / num_pumps


if __name__ == '__main__':
    rcm = RequestController()
    rcm.handle({
        'cmd': 'water',
        'params': {
            'ml': 40,
            'plant': 'Ronaldo'
        }
    })
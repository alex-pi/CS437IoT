from utils import *
from car_controller import CarController


class RequestController:

	def __init__(self):
		self.car_ctl = CarController()
		self.car_ctl.start()

	def handle(self, message):
		cmd = message.get('cmd', None)
		params = message.get('params', {})
		debug(f'Command {cmd} received.')
		debug(f'Parameters {params}')
		response = {}
		if cmd == "forward":
			trace("Moving forward.")
			self.car_ctl.move(cmd, params)
		elif cmd == "backward":
			trace("Moving backward.")
			self.car_ctl.move(cmd, params)
		elif cmd == "left":
			trace("Turning left.")
			self.car_ctl.turn(cmd, params)
		elif cmd == "right":
			trace("Turning right.")
			self.car_ctl.turn(cmd, params)
		elif cmd == "stop":
			trace("Stopping car.")
			self.car_ctl.stop()
		elif cmd == "metrics":
			trace("Getting metrics.")
			response = self.car_ctl.get_metrics()
		else:
			print("Command not supported")

		return response

	def finish(self):
		self.car_ctl.finish()



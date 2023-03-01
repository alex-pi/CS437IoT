import picar_4wd as fc
import time
import sys
import math
import threading
import tempfile
import os
import numpy as np
import matplotlib.pyplot as plt
from picar_4wd.speed import Speed
from astar import AStarPath
from utils import *
from pathlib import Path
#import detection.detect as objdet


# Registered average speeds (cm/s) given a "power".
AV_SPEED_AT = {
    20: 30,
    5: 25
}

'''
Represents a map being used during navigation or map creation (object mapping).
'''
class Map():

    def __init__(self, scale=1, map_name=None):
        # One array location to cm
        self.SCALE = scale
        self.dim = 180
        if map_name:
            self.map = np.load(map_name)
        else: 
            self.map = np.zeros((self.dim, self.dim), dtype=int)
        self.obj_mark = 2
        #self.init_car_position = [self.dim - 1, int(self.dim / 2)]
        #self.car_position = self.init_car_position
        self.car_path = []
        #self.car_direction = [-1, 0]
        self.prev_obj_position = []
        self.prev_obj_idxs = []
        # Astar without costs to interpolate objects
        self.astar_conn = AStarPath(self.map, connect_mode=True)

    def set_initial_position(self, init_pos):
        # Make sure is not a tuple as it will change
        inpt = [init_pos[0], init_pos[1]]
        self.initial_position = inpt
        self.car_position = inpt
        self.car_path.append(inpt)

    def update_direction(self, new_direction):
        # Make sure is not a tuple as it will change
        dirt = [new_direction[0], new_direction[1]]
        self.car_direction = dirt

    def update_position(self, dist_traveled):

        dist_x = abs(dist_traveled * self.car_direction[1])
        dist_y = abs(dist_traveled * self.car_direction[0])
        # Non fractional distance traveled
        eff_dist_x = int((dist_x / self.SCALE)) * self.SCALE
        eff_dist_y = int((dist_y / self.SCALE)) * self.SCALE

        # Residual traveled distance
        res_dist_x = dist_x - eff_dist_x
        res_dist_y = dist_y - eff_dist_y

        # array units here should be integers
        x_units = (eff_dist_x / self.SCALE) * self.car_direction[1]
        y_units = (eff_dist_y / self.SCALE) * self.car_direction[0]

        info("units traveled: x={},y={}"
            .format(x_units, y_units))

        x_idx = self.car_position[1] + int(x_units)
        y_idx = self.car_position[0] + int(y_units)

        # maybe add guards to not assign position
        # out of the map... or the navigator should do it?
        self.car_position[1] = x_idx
        self.car_position[0] = y_idx

        #self.map[y_idx, x_idx] = 8
        self.car_path.append([y_idx, x_idx])
        info("car position {}".format(self.car_position))

        return res_dist_x + res_dist_y


    def map_object(self, obj_position, angle_interpol):
        theta = math.radians(obj_position[0])
        h = obj_position[1]

        # negative is right from car perspective
        dist_adj = math.cos(theta) * h
        dist_opp = math.sin(theta) * h

        if self.car_direction[0] != 0:
            yo = abs(dist_adj) * self.car_direction[0]
            xo = dist_opp * self.car_direction[0]
        elif self.car_direction[1] != 0:
            yo = dist_opp * self.car_direction[1] * -1
            xo = abs(dist_adj) * self.car_direction[1]

        x_units = (xo / self.SCALE) 
        y_units = (yo / self.SCALE) 

        x_idx = self.car_position[1] + int(x_units)
        y_idx = self.car_position[0] + int(y_units)

        # When objects are out of bound we mark the limits of the matrix.
        x_idx = x_idx if (x_idx > 0 and x_idx < self.dim) else min([0, self.dim-1], key=lambda x:abs(x-x_idx))
        y_idx = y_idx if (y_idx > 0 and y_idx < self.dim) else min([0, self.dim-1], key=lambda x:abs(x-y_idx))

        info("object idexes: x={},y={}"
            .format(x_idx, y_idx))
        info("car idexes: x={},y={}"
            .format(self.car_position[1], self.car_position[0]))

        self.map[y_idx, x_idx] = self.obj_mark

        self.improve_obj_mark(obj_position, angle_interpol, (y_idx, x_idx))

        self.prev_obj_idxs = [y_idx, x_idx]
        self.prev_obj_position = obj_position

    def improve_obj_mark(self, obj_position, angle_interpol, curr_idxs):

        obj_path = []
        obj_path.append(curr_idxs)
        if self.prev_obj_position:
            prev_angle = self.prev_obj_position[0]
            prev_dist = self.prev_obj_position[1]
            angle = obj_position[0]
            dist = obj_position[1]
            # angles can be adjacent but it might be that objects are actually
            # far, i.e. one is far in the backgroud while the other closer to sensor.
            if abs(angle - prev_angle) <= angle_interpol and abs(prev_dist - dist) < 5:
                info("Interpolate: {}, {}".format(prev_angle, angle))
                #self.connect([y_idx, x_idx], self.prev_obj_idxs)
                prev_idxs = tuple(self.prev_obj_idxs)
                came_from, _ = self.astar_conn.a_star_search(curr_idxs, \
                    prev_idxs)      
                obj_path = self.astar_conn.build_route(curr_idxs, prev_idxs, \
                    came_from, mark=self.obj_mark)

        for p in obj_path:
            get_clearance(self.map, p, 2, mark=self.obj_mark)


    def reset(self):
        self.prev_obj_position = []
        self.prev_obj_idxs = []

    def show(self, car_mark=1):
        if car_mark:
            for cp in self.car_path:
                self.map[cp[0], cp[1]] = car_mark
        #plt.imshow(self.map, cmap='gray')
        plt.imshow(self.map)
        plt.title("Map View")
        plt.show()


'''
Controls the mapping thread using the ultrasonic sensor.
'''
class ObjectMapper():

    def __init__(self, grid_map, map_mode=False):
        self.gmap = grid_map
        self.ANGLE_RANGE = 180
        self.STEP = 10
        self.us_step = self.STEP
        self.current_angle = 90
        # To the left
        self.MAX_ANGLE = self.ANGLE_RANGE/2
        # To the right
        self.MIN_ANGLE = -self.ANGLE_RANGE/2
        # Map definitions
        self.MAP_MAX_DIST = 70
        self.map_mode = map_mode

        self.scan_flag = True
        self.scan_in_pause = False
        self.scan_t = threading.Thread(target=self.scan_loop, name="ThreadMapper")
        fc.servo.set_angle(self.current_angle)
        time.sleep(0.5)

    def get_distance_at(self, angle, delay=0.08):
        # make sure servo gets in position before reading from ultrasonic
        fc.servo.set_angle(angle)
        time.sleep(delay)
        # distance is in cm
        distance = fc.us.get_distance()
        angle_distance = (angle, distance)
        #info(angle_distance)
        return angle_distance

    def scan_step(self):
        angle_distance = self.get_distance_at(self.current_angle)
        if self.current_angle >= self.MAX_ANGLE:
            self.current_angle = self.MAX_ANGLE
            self.us_step = -self.STEP
        elif self.current_angle <= self.MIN_ANGLE:
            self.current_angle = self.MIN_ANGLE
            self.us_step = self.STEP

        self.current_angle += self.us_step
        # picar lib returns -2 when nothing is detected.
        trace("angle, distance={}".format(angle_distance))
        if self.map_mode:
            if angle_distance[1] >= 0 and angle_distance[1] <= self.MAP_MAX_DIST:
                info("Mapping object...")
                self.gmap.map_object(angle_distance, self.STEP)
                info("Done mapping object...")
            return angle_distance

    def scan_loop(self):
        while self.scan_flag:
            if not self.scan_in_pause:
                self.scan_step()

    def start(self):
        self.scan_t.start()

    def stop(self):
        self.scan_flag = False
        self.scan_t.join()

            self.m.show()

    def pause(self):
        self.scan_in_pause = True

    def resume(self):
        self.scan_in_pause = False

    def get_map(self):
        return self.gmap

'''
Controls the main loop that decides what the car is doing.
'''
class CarController():
    def __init__(self):
        self.car_t = threading.Thread(target=self.car_loop, name="CarThread")
        self.distance_traveled = 0
        self.navigating = True
        self.is_moving = False
        self.obj_detected = False
        self.touch_file = '{}/detected.touch'.format(tempfile.gettempdir())

        # I had object detection as another thread but that did not go well.
        #self.od = objdet.ObjectDetector(['stop sign', 'person'])
        #self.od.start()

    def car_loop(self):
        speed = AV_SPEED_AT[20]
        move_time = 0.1
        while self.navigating:
            #self.obj_detected = self.od.detected
            self.obj_detected = os.path.exists(self.touch_file)
            if self.obj_detected:
                debug("Object detected.")
                fc.stop()
                continue
            if self.is_moving:
                if self.time_to_travel <= 0.1:
                    fc.stop()
                    self.is_moving = False 
                    self.finished_travel = True
                    #info("Distance traveled: %s cm"%self.distance_traveled)
                else:
                    self.move_func(self.power)
                    time.sleep(move_time)
                    dist = speed * move_time
                    self.distance_traveled += dist
                    self.distance_to_travel -= dist
                    self.time_to_travel -= move_time
                    debug("Time to travel {} s".format(self.time_to_travel))
                    debug("Moved {} cms in {} s".format(dist, move_time))


    '''
    We init some parameters when the Navigator class decides we start a new
    segment of a travel, some other events might trigger this. Like a route
    being recalculated.
    '''
    def init(self, time_to_travel, distance, power=20, move_func=fc.forward):
        self.time_to_travel = time_to_travel
        self.distance_to_travel = distance
        self.power = power
        self.move_func = move_func
        self.finished_travel = False
        self.distance_traveled = 0


    def start(self):
        self.car_t.start()

    def stop(self):
        self.navigating = False
        #self.od.stop()
        self.car_t.join()

    def pause(self):
        fc.stop()
        #self.od.pause()
        #info("Distance tracking: {} cm".format(self.distance_traveled))
        #info("Distance yet to travel: {} cm".format(self.distance_to_travel))
        self.is_moving = False

    def resume(self):
        #self.od.resume()
        #time.sleep(3)
        #self.distance_traveled = 0
        self.is_moving = True


class Navigator():

    def __init__(self, obj_mapper, 
        initial_position,
        initial_direction=[-1, 0]):
        self.om = obj_mapper
        self.m = obj_mapper.get_map()
        self.m.update_direction(initial_direction)
        self.m.set_initial_position(initial_position)
        self.car_ctrl = CarController()
        self.TURN_POWER = 20
        # Aprox 360 turn
        self.TOTAL_TURN_TIME = 5.0
        self.SAFE_REF_POINT = 35

        # start car and object mapper loops
        self.car_ctrl.start()
        self.om.start()
        #else:
        #    self.nav_t = threading.Thread(target=self.nav_loop, name="ThreadNavigator")

    def finish(self):
        self.om.stop()
        self.car_ctrl.stop()            

    '''
    Loop to travel a segment of a route while also mapping objects with ultrasonic.
    '''
    def travel_map(self, distance=30, power=20, move_func=fc.forward):
        try:
            # TODO Given the current position, reduce
            # distance if needed to stay on map

            speed = AV_SPEED_AT[power]
            time_to_travel = distance / speed
            move_time = 0.5
            travel_steps = int(time_to_travel / move_time)
            # TODO Add code to deal with residuals

            # Expecting constant distance (speed)
            dist = speed * move_time
            dist_total = 0
            self.om.resume()
            time.sleep(0.2)
            for step in range(1, travel_steps + 1):
                info("************")
                move_func(power)       
                time.sleep(move_time)
                fc.stop()
                dist_total += dist 

                info("Moved %s cm"%dist)
                debug("Stop for scaning...")
                self.m.update_position(dist)
                time.sleep(1)

            info("--- Distance traveled ---")
            info("%s cm"%dist_total)

        finally:
            self.om.pause()
            # Reset map variables for interpolation
            self.m.reset()
            fc.stop()

    '''
    Better version of above function since it uses the CarController.
    '''
    def move(self, distance, power=20, move_func=fc.forward):
        speed = AV_SPEED_AT[power]
        time_to_travel = distance / speed
        info("Estimated travel time: %s s"%time_to_travel)
        start_time = time.time()
        try:
            self.car_ctrl.init(time_to_travel, distance, power, move_func)
            info("--- Car Moving ---")
            while True:
                #self.om.resume()
                if self.car_ctrl.obj_detected:
                    self.car_ctrl.pause()
                else:                
                    self.car_ctrl.resume() 
                time.sleep(0.5)
                if self.car_ctrl.finished_travel:
                    break

            time_elapsed = time.time() - start_time
            info("Real time elapsed: {} ".format(time_elapsed))

            # Update should happen more frequently...
            self.m.update_position(self.car_ctrl.distance_traveled)
            time.sleep(1)

        finally:
            self.car_ctrl.pause()
            #self.om.pause()
            # Reset map variables for interpolation
            #self.m.reset()
            fc.stop()
            info("--- Car Stopped ---")

    '''
    Make the car turn.
    '''
    def turn(self, turn_func, new_direction, angle=90, adjust_time=0):
        try:
            # There should not be mapping happening while turning
            turn_time = self.TOTAL_TURN_TIME / (360 / angle)
            turn_func(self.TURN_POWER)
            time.sleep(turn_time + adjust_time)
            fc.stop()
            time.sleep(6.3)
            self.m.update_direction(new_direction)
            # Turning gains and looses distance travel due to way PiCar turns.
            # it all depends on what is our point of reference.
            # Is it the ultrasonic sensor or the car rotation point?
            # self.m.update_position(10)            
        finally:
            fc.stop()


'''
Make the car move in a predetermined path to scan surroundings.
Objects will be map having the car as reference point.
'''
def mapping_moving(map_name='map.npy'):
    m = Map()
    om = ObjectMapper(m, map_mode=True)
    #nav = Navigator(om, initial_position=[160, 179], 
    #    initial_direction=[0, -1])
    nav = Navigator(om, initial_position=[90, 0], 
        initial_direction=[0, 1],
        map_mode=True)

    nav.travel_map(distance=150)
    nav.turn(fc.turn_right, [1, 0])
    nav.travel_map(distance=60)
    nav.turn(fc.turn_right, [0, -1] , adjust_time=-0.1)
    nav.travel_map(distance=120)
    #nav.turn(fc.turn_left, [1, 0], adjust_time=0.3)
    
    nav.finish()
    with open(map_name, 'wb') as f:
        np.save(f, m.map)


'''
The more reliable way of mapping with the car :), just fix a position.
'''
def fixed_mapping(pos, direc, map_name):
    try:
        m = Map()
        om = ObjectMapper(m, map_mode=True)
    
        m.update_direction(direc)
        m.set_initial_position(pos)
        om.start()
        time.sleep(7)
    finally:
        om.stop()
        with open(map_name, 'wb') as f:
            np.save(f, m.map)

        m.show()


'''
Given a map, find a route from start to end
and navigate it.
'''
def navigate(start, end, init_dir, map_name):
    m = Map(map_name=map_name)
    om = ObjectMapper(m)   
    asp = AStarPath(m.map, cost_ratio=14)
    cf, _ = asp.a_star_search(start, end)
    route = asp.build_route(start, end, cf) 

    dirs, diss, _ = zip_route(route)
    info("Travel plan: {}".format(list(zip(dirs, diss))))

    nav = Navigator(om, initial_position=start, 
        initial_direction=init_dir)

    curr_dir = m.car_direction
    for new_dir, dis in zip(dirs, diss):
        info("Next instruction: {} {}".format(new_dir, dis))
        tf = decode_turn(tuple(m.car_direction), new_dir, fc)
        info(tf)
        if tf:
            nav.turn(tf[0], new_dir, adjust_time=tf[1])
        nav.move(dis)

    nav.finish() 

    path = expand_route(start, dirs, diss)
    for s in path:
        m.map[s[0], s[1]] = 3
    show_map(m.map)


if __name__ == '__main__':
    # Map A
    # fixed_mapping([65, 60], [1, 0])
    # Map B
    # fixed_mapping([120, 105], [-1, 0])

    #navigate((80, 160), (80, 20), (0, -1), "./map_f_A.npy")

    navigate((10, 160), (170, 90), (0, -1), "./map_f_B.npy")


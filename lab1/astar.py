import numpy as np
import heapq

'''
A* algorithm implementation that uses a 2-d numpy arrays as a map.

This class can also be used to connect two points without any penalization
when connect_mode=True. This is used for interpolating/joining objects. 
'''
class AStarPath():

    def __init__(self, np_map, connect_mode=False, cost_ratio=1):
        # By default it is just a star algorithm
        self.all_around = False
        self.filter_obstacles = True
        self.connect_mode = connect_mode
        self.np_map = np_map
        self.cost_ratio = cost_ratio
        if connect_mode:
            # I use this for interpolation
            self.filter_obstacles = False
            self.all_around = True

    def is_inside(self, p):
        (ry, cx) = p
        return 0 <= cx < self.np_map.shape[1] and 0 <= ry < self.np_map.shape[0]

    def is_free(self, p):
        (ry, cx) = p
        return self.np_map[ry, cx] != 2

    def man_distance(self, p1, p2):
        (ry1, cx1) = p1
        (ry2, cx2) = p2
        return abs(cx1 - cx2) + abs(ry1 - ry2)

    '''
    Cost to move from point 1 to 2 factors distance from obstacles.
    A route is penalized if gets to close to an obstacle. Such distance
    is controled by self.cost_ratio.

    When connect_mode=True there is no cost.
    '''
    def get_cost(self, p1, p2):
        if self.connect_mode:
            return 0
        neighbors = self.get_neighbors(p2, filter_obstacles=False, all_around=True
                                       , ratio=self.cost_ratio)
        cost = 0
        for n in neighbors:
            cost += self.np_map[n[0], n[1]]

        # I tried this hack to smooth routes, but it did not work for me.
        # udge = 0
        # ry1, cx1) = p1
        # ry2, cx2) = p2
        # f (ry1 + cx1) % 2 == 0 and ry2 != ry1: nudge = 1
        # f (ry1 + cx1) % 2 == 1 and cx2 != cx1: nudge = 1

        #return cost + (0.001 * nudge)
        return cost

    '''
    It gets the surrounding points of a given point, ratio controls how many
    "layers" of neighbors we want to include.
    '''
    def get_neighbors(self, p, filter_obstacles=True, all_around=False, ratio=1):
        (ry, cx) = p
        #r = ratio

        if self.connect_mode:
            filter_obstacles = False
            all_around = True

        neighbors = []
        for r in range(1, ratio+1):
            if all_around:
                # counter-clockwise start at 6 (down)
                neighbors += [(ry+r, cx), (ry+r, cx+r), (ry, cx+r), (ry-r, cx+r),
                             (ry-r, cx), (ry-r, cx-r), (ry, cx-r), (ry+r, cx-r)]
            else:
                # down, up, left, right
                neighbors += [(ry+r, cx), (ry-r, cx), (ry, cx-r), (ry, cx+r)]
        #if (cx + ry) % 2 == 0:
        #    neighbors.reverse()
        neighbors = filter(self.is_inside, neighbors)
        if filter_obstacles:
            neighbors = filter(self.is_free, neighbors)

        return list(neighbors)


    '''
    A* implementation
    '''
    def a_star_search(self, start, goal):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            current = heapq.heappop(frontier)[1]  # pop item not cost

            if current == goal:
                break

            for neigh in self.get_neighbors(current):
                new_cost = cost_so_far[current] + self.get_cost(current, neigh)
                if neigh not in cost_so_far or new_cost < cost_so_far[neigh]:
                    cost_so_far[neigh] = new_cost
                    priority = new_cost + self.man_distance(neigh, goal)
                    # frontier.put(next, priority)
                    heapq.heappush(frontier, (priority, neigh))
                    came_from[neigh] = current

        return came_from, cost_so_far

    '''
    Given the sequence  of steps by a_star_search, this method traces
    back to form and array with steps to follow.

    When mark is passed it also marks the path with a given number in the 
    np array self.np_map
    '''
    def build_route(self, start, goal, came_from, mark=None):
        current = goal
        path = []
        while current != start:
            if mark:
                self.np_map[current[0], current[1]] = mark
            path.append(current)
            current = came_from[current]

        if mark:
            self.np_map[start[0], start[1]] = mark
        path.append(start)
        path.reverse()

        return path


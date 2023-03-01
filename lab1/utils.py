import matplotlib.pyplot as plt

LOG_LEVELS = {
	'ERROR': 0,
	'INFO': 1,
	'DEBUG': 2,
	'TRACE': 3
}

LOG_LVL = 'INFO'

def trace(message):
    if LOG_LEVELS['TRACE'] <= LOG_LEVELS[LOG_LVL]:
        print(message)

def debug(message):
	if LOG_LEVELS['DEBUG'] <= LOG_LEVELS[LOG_LVL]:
		print(message)

def info(message):
	if LOG_LEVELS['INFO'] <= LOG_LEVELS[LOG_LVL]:
		print(message)

def is_inside(np_map, p):
    (ry, cx) = p
    return 0 <= cx < np_map.shape[1] and 0 <= ry < np_map.shape[0]

'''
Used to add clearance to an object/obstacle marked in the map.
ratio controls how much units of clearance to add.
'''
def get_clearance(np_map, p, ratio, mark):
    (ry, cx) = p
    blc = (ry + ratio, cx - ratio)
    brc = (ry + ratio, cx + ratio)
    urc = (ry - ratio, cx + ratio)
    ulc = (ry - ratio, cx - ratio)

    clear_list = []

    for ccx in range(blc[1], brc[1]+1):
        clear_list.append((blc[0], ccx))
        clear_list.append((ulc[0], ccx))

    for cry in range(ulc[0], blc[0]+1):
        clear_list.append((cry, ulc[1]))
        clear_list.append((cry, urc[1]))

    clear_list = filter(lambda x: is_inside(np_map, x), clear_list)

    if mark:
        for m in clear_list:
            np_map[m[0], m[1]] = mark

    return clear_list

'''
Given a route found by A* algorithm this performs the following steps:
1) splits the route in segments where direction changes, each segment is represented
    by its direction and distance.
2) if segments are too small, those are integrated to subsequent larger segments
   this has the effect of smoothing a path.
3) After step 2 there might be redundancies, i.e. adjacent segments with same direction
   are collapsed into 1 single larger segment.
'''
def zip_route(route):
    segments = []
    distances = []
    directions = []
    curr_seg = [route[0]]
    curr_dir = (route[1][0] - route[0][0],
                route[1][1] - route[0][1])

    for s in range(1, len(route)):
        prev = route[s-1]
        curr = route[s]
        new_dir = (curr[0] - prev[0], curr[1] - prev[1] )

        if curr_dir == new_dir:
            curr_seg.append(curr)
        else:
            segments.append(curr_seg)
            directions.append(curr_dir)
            #dist = max(abs(curr_seg[0][0] - curr_seg[-1][0]),
            #           abs(curr_seg[0][1] - curr_seg[-1][1]))
            dist = len(curr_seg)
            distances.append(dist)
            curr_seg = [curr]
            curr_dir = new_dir
    segments.append(curr_seg)
    directions.append(curr_dir)
    distances.append(len(curr_seg))

    cdistances = []
    cdirections = []
    for i in range(0, len(directions)):
        dir = directions[i]
        dist = distances[i]

        if dist < 15:
            found = False
            for k in range(i-1, -1, -1):
                if directions[k] == dir and distances[k] > 0:
                    distances[k] += dist
                    distances[i] = 0
                    break
            if found:
                continue
            for j in range(i+1, len(directions)):
                if directions[j] == dir and distances[j] > 0:
                    distances[j] += dist
                    distances[i] = 0
                    break
        else:
            cdirections.append(dir)
            cdistances.append(dist)

    debug(cdirections)
    debug(cdistances)

    idxs_redundant = []
    base_dir_idx = 0
    for i in range(1, len(cdirections)):
        currd = cdirections[i]
        if cdirections[base_dir_idx] != currd:
            base_dir_idx = i
            continue

        cdistances[base_dir_idx] += cdistances[i]
        idxs_redundant.append(i)

    fdistances = []
    fdirections = []
    for i in range(0, len(cdirections)):
        if i not in idxs_redundant:
            fdistances.append(cdistances[i])
            fdirections.append(cdirections[i])

    debug(fdirections)
    debug(fdistances)

    return fdirections, fdistances, segments

'''
Given a collections of pairs, distances and directions
this method creates an expanded path with the sequence of coordinates
in grid/map.
'''
def expand_route(start, directions, distances):
    current = start
    path = [current]
    for dir, dis in zip(directions, distances):
        print(dir, dis)
        for d in range(1, dis+1):
            step = (current[0] + dir[0], current[1] + dir[1])
            path.append(step)
            current = step

    return path


'''
Used to translate turning to the appropiate picar lib method
for turning.
'''
def decode_turn(curr_dir, new_dir, fc):
    ladjust = 0.33
    radjust = -0.1
    dic_turns = {
        (1, 0): {
            (0, -1): (fc.turn_right, radjust),
            (0, 1): (fc.turn_left, ladjust)
        },
        (-1, 0): {
            (0, 1): (fc.turn_right, radjust),
            (0, -1): (fc.turn_left, ladjust)
        },
        (0, 1): {
            (1, 0): (fc.turn_right, radjust),
            (-1, 0): (fc.turn_left, ladjust)
        },
        (0, -1): {
            (-1, 0): (fc.turn_right, radjust),
            (1, 0): (fc.turn_left, ladjust)
        },
    }

    return dic_turns[curr_dir].get(new_dir)

'''
Simply shows an numpy 2-d array as a heatmap.
'''
def show_map(data):
    # Function to show the heat map
    plt.imshow(data)

    plt.title("Map View")
    plt.show()
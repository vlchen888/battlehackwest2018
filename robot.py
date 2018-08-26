import random
import math

             

class Util:
    @classmethod
    def sign(cls, x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0


class Queue(object):
    def __init__(self):
        self.queue = []
    def put(self, item):
        self.queue.append(item)
    def get(self):
        # assert(not self.empty()), "trying to get from empty queue"
        val = self.queue[0]
        self.queue = self.queue[1:]
        return val
    def empty(self):
        if len(self.queue) == 0:
            return True
        return False



class MyRobot(BCAbstractRobot):
    
    # Phases: FIND_TEAM, BUILD_NEXUS, etc...
    phase = "FIND_TEAM"

    directions = [
        bc.NORTH,
        bc.NORTHEAST,
        bc.EAST,
        bc.SOUTHEAST,
        bc.SOUTH,
        bc.SOUTHWEST,
        bc.WEST,
        bc.NORTHWEST,
    ]

    num_turns = 0
    dest_x = -1
    dest_y = -1
    arr_map = []
    curr_x = -1
    curr_y = -1

    VIEW_SIZE = 7

    targets = [
        [10, 10],
        [17, 10],
        [17, 17],
        [24, 17],
        [24, 24],
        [31, 24],
        [31, 31]
    ]

    target_index = 0
    

    def relative_pos_to_dir(self, dX, dY):
        if dX == 0 and dY == -1:
            return bc.NORTH
        elif dX == 0 and dY == 1:
            return bc.SOUTH
        elif dX == -1 and dY == 0:
            return bc.WEST
        elif dX == 1 and dY == 0:
            return bc.EAST
        elif dX == -1 and dY == 1:
            return bc.SOUTHWEST
        elif dX == -1 and dY == -1:
            return bc.NORTHWEST
        elif dX == 1 and dY == 1:
            return bc.SOUTHEAST
        elif dX == 1 and dY == -1:
            return bc.NORTHEAST
        else:
            return None
            

    def turn(self):
        # Log some metadata
        self.num_turns += 1 
        self.log(self.num_turns)

        self.curr_x = self.me()["x"]
        self.curr_y = self.me()["y"]

        self.map_arr = self.get_visible_map()

        num_friendlies = self._get_num_friendlies()

        if self.me()["team"] == 1:
            if phase == "FIND_TEAM":
                target_x = 10
                target_y = 10
                return self._get_move_pathfind(target_x, target_y)
            elif phase == "BUILD_NEXUS":
                pass
        else:
            return
        

    # TODO
    def _is_friendly(self, uid):
        return True

    def _get_num_friendlies(self):
        num_friendlies = 0
        for x in range(self.VIEW_SIZE):
            for y in range(self.VIEW_SIZE):
                val = self.map_arr[y][x]
                if (not val == bc.EMPTY and not val == bc.HOLE and self._is_friendly(val)):
                    num_friendlies += 1
        return num_friendlies

    def _get_unit_dir(self, dx, dy):
        mag = math.sqrt(dx*dx + dy*dy)
        if mag == 0:
            return (0, 0)
        return (round(dx/mag), round(dy/mag))


    def _get_best_direction(self, target_x, target_y):
        return self._get_unit_dir(target_x - self.curr_x, target_y - self.curr_y)
    

    def _get_move_pathfind(self, target_x, target_y):
        dX, dY = self._get_best_direction(target_x, target_y)
        if dX == 0 and dY == 0:
            return None
        desired_dir = self.relative_pos_to_dir(dX, dY)
        # Try to avoid the obstacle. Use bugfind
        index = self.directions.index(desired_dir)

        i = 0
        while i < 8:
            nextDir = self.directions[(index + i) % len(self.directions)]
            if self.get_in_direction(nextDir) == bc.EMPTY:
                return self.move(nextDir)
            i += 1

        return None
    

    ############### METHODS FOR NEW ROBOTS ###################
    def _update_target(self):
        """
        If you're a new robot, then check where you are by
        iterating through the nexus list

        If the current target has more eligible nexus, stay

        Else, move onto new target
        """
        me = self.me()
        for i in range(target_index, len(self.targets)):
            if abs(me.x - self.targets[i][0]) < 4 and \
               abs(me.y - self.targets[i][1]) < 4:
                self.target_index = i
                break

        if self._find_new_nexus() == False:
            return self.target_index
        else:
            self.target_index += 1
            return self.target_index 


    def _in_nexus(self):
        cells = [
            [0, 1],
            [0, -1],
            [-1, 0],
            [1, 0]
        ]
        for cell in cells:
            cell_type = self.get_relative_pos(cell[0], cell[1])
            if cell_type in [bc.EMPTY, bc.HOLE] or not _is_friendly(cell_type.id):
                return False
        return True

    def _is_new_robot(self):
        """
        Conditions:
        - health below 50
        - in the centre of 4 robots
        """
        me = self.me()
        if me.health < 50 and self._in_nexus():
            return True
        return False

    ##########################################################


    ############### METHODS FOR BFS ##########################

    def _array_copy(self, arr):
        new_arr = []
        for i in arr:
            new_arr.append(i)
        return new_arr


    def _get_min_path(self, dX, dY):
        # self.log(["finding min path to:", dX, dY])
        assert(abs(dX) <= 3 or abs(dY) <= 3)
        
        visited = []
        for i in range(7):
            row = []
            for j in range(7):
                row.append(False)
            visited.append(row)

        q = Queue()
        q.put(
            (
                (3, 3),
                []
            )
        )
        visited[3][3] = True

        while not q.empty():
            node, path = q.get()
            path.append(node)
            neighbours = [
                (node[0] + 1, node[1] + 1),
                (node[0] - 1, node[1] + 1),
                (node[0] + 1, node[1] - 1),
                (node[0] - 1, node[1] - 1),
                (node[0] - 1, node[1]),
                (node[0] + 1, node[1]),
                (node[0], node[1] + 1),
                (node[0], node[1] - 1)    
            ]
            for neighbour in neighbours:
                if neighbour[0] - 3 == dX and neighbour[1] - 3 == dY:
                    # self.log(["found spot", neighbour, dX, dY, path])
                    return path
                if neighbour[0] < 0 or neighbour[0] > 6 or \
                   neighbour[1] < 0 or neighbour[1] > 6:
                    continue
                if visited[neighbour[0]][neighbour[1]] == False:
                    visited[neighbour[0]][neighbour[1]] = True
                    neighbour_val = self.get_relative_pos(neighbour[0] - 3, neighbour[1] - 3)
                    if neighbour_val == bc.EMPTY:
                        q.put(
                            (
                                neighbour,
                                self._array_copy(path)
                            )
                        )
        return None


    def _get_next_move_to_location(self, dX, dY):
        try:
            path = self._get_min_path(dX, dY)
        except:
            self.log(["got rekt at finding path"])
            path = []
        # self.log(["got path", path])
        if path != None and len(path) > 1:
            # self.log(["valid path"])
            x, y = path[1][0] - 3, path[1][1] - 3
            # self.log(["matching to move", x, y])
            if self.get_relative_pos(x, y) != bc.EMPTY:
                # self.log(["move not empty", self.get_relative_pos(x, y)])
                return None
            return self.relative_pos_to_dir(x, y)
            # self.log([x, y, "didn't match any direction"])
        else:
            return None


    ############### END METHODS FOR BFS ##########################
    ############### OTHER BFS METHODS ############################

    def _get_closest_friendly_robot(self):
        me = self.me()
        closest_robot = None
        smallest_distance = None
        for robot in self.get_visible_robots():
            # self.log(["my stuff and their signal", self.me(), robot.signal])
            if me.id != robot.id and _is_friendly(robot):
                distance = math.sqrt((robot.x - me.x) ** 2 + (robot.y - me.y) ** 2)
                if smallest_distance == None or distance < smallest_distance:
                    closest_robot = robot
                    smallest_distance = distance
        return [closest_robot, smallest_distance]

            
    def _get_relative_coord_of_robot(self, robot):
        me = self.me()
        vis_map = self.get_visible_map()
        for i, row in enumerate(vis_map):
            for j, col in enumerate(row):
                if vis_map[i][j] == robot.id:
                    return (j - 3, i - 3)
        return None


    def _get_move_to_robot(self):
        me = self.me()
        closest_robot = None
        closest_robot, distance = self._get_closest_friendly_robot()
        if closest_robot != None and distance >= 2:
            rel_robot_coord = self._get_relative_coord_of_robot(closest_robot)
            if rel_robot_coord != None:
                try:
                    next_move = self.get_next_move_to_location(rel_robot_coord[0], rel_robot_coord[1])
                    return next_move
                except:
                    self.log(["got rekt at finding move"])
                    return None
        return None


    def _print_list_of_dicts(self, list_of_dicts):
        keys = []
        vals = []
        for d in list_of_dicts:
            for k in list(d.keys()):
                keys.append(k)
            for val in list(d.values()):
                vals.append(val)
        self.log([keys, vals])

    """
    try:
        move_to_robot = self.get_move_to_robot()
    except:
        self.log(["had exception"])
    if move_to_robot != None:
        self.log(["Moving to direction:", move_to_robot])
        return self.move(move_to_robot)
    else:
        closest_robot, smallest_distance = self.get_closest_friendly_robot()
        if closest_robot == None:
            return self.move(random.choice(self.DIRECTIONS))
    """

#########################################################################
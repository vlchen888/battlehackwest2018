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
    
    # Phases: FIND_TEAM, BUILD_NEXUS, FIND_NEW_NEXUS, MOVE_TO_NEW_NEXUS, etc...
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
    curr_x = -1
    curr_y = -1

    new_nexus_target_x = -1
    new_nexus_target_y = -1


    map_arr = []

    VIEW_SIZE = 7

    general_targets = [
        [10, 10],
        [17, 10],
        [17, 17],
        [24, 17],
        [24, 24],
        [31, 24],
        [31, 31]
    ]

    general_target_index = 0
    
    NEXUS_MASK = 8

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

        self.curr_x = self.me()["x"]
        self.curr_y = self.me()["y"]

        self.map_arr = self.get_visible_map()

        num_friendlies = self._get_num_friendlies()

        if self.me()["team"] == 1
            if self.phase == "FIND_TEAM":
                if self._is_new_robot():
                    self._update_target()
                    target_x = self.general_targets[self.general_target_index][0]
                    target_y = self.general_targets[self.general_target_index][1]                    
                    if _in_target_area():
                        self.phase = "FIND_TARGET"
                    else:
                        self.phase = "FIND_NEW_NEXUS"
                elif self.num_turns > 20:
                    self.phase = "FIND_NEW_NEXUS"
                else:
                    target_x = 10
                    target_y = 10
                    return self._get_move_pathfind(target_x, target_y)
            if self.phase == "FIND_TARGET":
                target_x = self.general_targets[self.general_target_index][0]
                target_y = self.general_targets[self.general_target_index][1]
                if self._in_target_area(target_x, target_y):
                    self.phase == "FIND_NEW_NEXUS"
                else:
                    return self._get_move_pathfind(target_x, target_y)
            if self.phase == "FIND_NEW_NEXUS":
                self._find_new_nexus()
            if self.phase == "MOVE_TO_NEW_NEXUS":
                return self._get_move_find_new_nexus()
        else:
            return self._get_move_pathfind(0, 0)
        

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
    
    ############### METHODS FOR NEXUS FINDING ##########################
    def _examine_spot(self, abs_x, abs_y):
        arr_x, arr_y = self._get_arr_coord_from_abs(abs_x, abs_y)
        return self.map_arr[arr_y][arr_x]


    def _is_empty(self, abs_x, abs_y):
        return self._examine_spot(abs_x, abs_y) == bc.EMPTY


    def _is_hole(self, abs_x, abs_y):
        return self._examine_spot(abs_x, abs_y) == bc.HOLE


    def _is_robot(self, abs_x, abs_y):
        return not self._is_empty(abs_x, abs_y) and not self._is_hole(abs_x, abs_y)


    def _get_arr_coord_from_abs(self, abs_x, abs_y):
        arr_x = abs_x - self.curr_x + 3
        arr_y = abs_y - self.curr_y + 3
        return (arr_x, arr_y)


    def _is_valid_nexus_center(self, abs_x, abs_y):
        """Returns True when abs_x, abs_y is a valid nexus center."""
        # Only could be a nexus if there are no holes
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if self._is_hole(abs_x + dx, abs_y + dy):
                    return False
        return True


    def _is_master_present(self, top_position_x, top_position_y):
        if self._is_robot(top_position_x, top_position_y):
            robot_id = self._examine_spot(top_position_x, top_position_y)
            if self._is_friendly(robot_id):
                sig = self.get_robot(robot_id).signal
                if sig & self.NEXUS_MASK > 0:
                    return True
        return False

    def _find_new_nexus(self):
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                next_x = self.curr_x + dx
                next_y = self.curr_y + dy
                if next_x >= 0 and next_y >= 0 and self._is_valid_nexus_center(next_x, next_y):
                    top_position_x = next_x
                    top_position_y = next_y - 1
                    if not self._is_master_present(top_position_x, top_position_y):
                        # Safe to go here
                        self.new_nexus_target_x = top_position_x
                        self.new_nexus_target_y = top_position_y
                        self.phase = "MOVE_TO_NEW_NEXUS"
                        return True

        return False

    def _is_visible(self, abs_x, abs_y):
        arr_x = abs_x - self.curr_x + 3
        arr_y = abs_y - self.curr_y + 3
        return arr_x >= 0 and arr_x < self.VIEW_SIZE and arr_y >= 0 and arr_y < self.VIEW_SIZE


    def _get_move_find_new_nexus(self):
        if self._is_visible(self.new_nexus_target_x, self.new_nexus_target_y):
            if self._is_master_present(self.new_nexus_target_x, self.new_nexus_target_y):
                self.phase = "FIND_NEW_NEXUS"
                return None
        return self._get_move_pathfind(self.new_nexus_target_x, self.new_nexus_target_y)

    ############### END METHODS FOR NEXUS FINDING ##########################
    ############### METHODS FOR FINDING EXISTING NEXUS ##########################
    def _compute_moves(self, curr_x, curr_y, target_x, target_y):
        '''
            This is a good approx. to get minimal number of moves.
            '''
        if self.get_relative_pos(target_x - curr_x, target_y - curr_y) == bc.EMPTY:
            return max(abs(curr_x - target_x)**2 + abs(curr_y - target_y)**2)
        return 999999
    
    def _compute_min_nexus_dist(self, master_x, master_y):
        one = compute_moves(self.me().x, self.me().y, master_x, master_y+2)
        two = compute_moves(self.me().x, self.me().y, master_x-1, master_y+1)
        three = compute_moves(self.me().x, self.me().y, master_x+1, master_y+1)
        # This means that the target is
        if one & two & three == 999999:
            return (-1, -1)
        if one <= two and one <= three:
            return (master_x, master_y+2)
        elif two <= three and two <= one:
            return (master_x-1, master_y+1)
        elif two <= three and two <= one:
            return (master_x+1, master_y+1)

    def _find_existing_nexus(self):
        '''
            Looking for the nearby robots to see if there is an existing
            master. If one is found, find the position that is closest to it and
            goes towards it.
            Returns true if an existing nexus is found.
        '''
        currentMap = self.get_visible_map()
        currentRobos = self.get_visible_robots()
        
        for i in currentRobos:
            if self._is_friendly(i.id):
                signal = i.signal
                if self.NEXUS_MASK&signal == self.NEXUS_MASK:
                    return self.compute_min_nexus_dist(i.x, i.y)
        return (-1, -1)

    ############### METHODS FOR NEW ROBOTS ###################
    def _in_target_area(self, target_x, target_y):
        """
        Are you close to a target area
        """
        if abs(me.x - target_x) < 3 and \
           abs(me.y - target_y) < 3:
            return True
        else:
            return False

    def _update_target(self):
        """
        If you're a new robot, then check where you are by
        iterating through the nexus list

        If the current target has more eligible nexus, stay

        Else, move onto new target
        """
        me = self.me()
        for i in range(self.general_target_index, len(self.general_targets)):
            if abs(me.x - self.general_targets[i][0]) < 3 and \
               abs(me.y - self.general_targets[i][1]) < 3:
                self.general_target_index = i
                break

        if self._find_new_nexus() == True:
            return self.general_target_index
        else:
            self.general_target_index += 1
            return self.general_target_index 


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
        - turn counter is below 3
        - health below 50
        - in the centre of 4 robots
        """
        me = self.me()
        if me.health < 50 and self._in_nexus() and self.num_turns < 3:
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

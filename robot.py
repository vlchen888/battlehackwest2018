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
    destin_loc = [(10,10), (5,5), (5,15), (15,15), (5, 15)]


    map_arr = []

    VIEW_SIZE = 7
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
        self.NEXUS_MASK = 8
        self.curr_x = self.me()["x"]
        self.curr_y = self.me()["y"]
        
        self.map_arr = self.get_visible_map()
        
        num_friendlies = self._get_num_friendlies()
        if self.num_turns <= 1:
            self.destin_loc = [(10,10), (5,5), (5,15), (15,15), (5, 15)]
        if self.me()["team"] == 1:
            #if self.phase != "IN NEXUS" and self.num_turns%25 == self.num_turns/25:
            #    self.phase == "FIND_TEAM"
            
            
            # Every 25 turns, we head to a new loc...
            if self.phase == "FIND_TEAM":
                if self.num_turns > 20:
                    self.phase = "FIND_EXISTING_NEXUS"
                #(target_x, target_y) = self.destin_loc[self.num_turns%25]
                (target_x, target_y) = (10, 10)
                return self._get_move_pathfind(target_x, target_y)
        
            # Can choose to not try and find existing nexus every time while
            # in phase, but since several can be heading there, might
            # want to check it...
            self.log("Printing out data....")
            self.log(self.phase)
            self.log(self.me())
            if self.phase == "IN NEXUS":
                return
            if self.phase == "FIND_EXISTING_NEXUS":
                (target_x, target_y) = self._find_existing_nexus()
                if target_y != -1:
                    if target_x != curr_x and target_y != curr_y:
                        self.log("Heading to..."+target_x+", "+target_y)
                        self.log("Currently at ..."+self.curr_x+", "+self.curr_y)
                        return self._get_move_pathfind(target_x, target_y)
                    else:
                        self.phase = "IN NEXUS"
                        return
            self.phase = "FIND_NEW_NEXUS"
            if self.phase == "FIND_NEW_NEXUS":
                res = self._find_new_nexus()
                if res == False:
                    #self.phase == "FIND_EXISTING_NEXUS"
                    return self.move(random.choice([
                                                    bc.NORTH,
                                                    bc.NORTHEAST,
                                                    bc.EAST,
                                                    bc.SOUTHEAST,
                                                    bc.SOUTH,
                                                    bc.SOUTHWEST,
                                                    bc.WEST,
                                                    bc.NORTHWEST,
                                                    ]))
            if self.phase == "MOVE_TO_NEW_NEXUS":
                res = self._get_move_find_new_nexus()
                if res != None:
                    return res
                self.log("Returning to do nothing...")
                return self._get_move_pathfind(0, 0)
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
        self.log("path finding...")
        dX, dY = self._get_best_direction(target_x, target_y)
        if dX == 0 and dY == 0:
            self.log("We are at the spot!!")
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
        self.log("hmmmm")
        return None
    
    ############### METHODS FOR ATTACKING ##########################
    def attack_logic(self):
        # Want to check if the spot is already occupied.
        # If it is, we want to find another one
        if self.phase == "MOVING TO ATTACK":
            if self.get_relative_pos(self.dest_x - self.curr_x, self.dest_y - self.curr_y) != bc.EMPTY:
                res = self._check_friendly_near_enemy(mapp, e.x, e.y)
                if res != None:
                    return res
                else:
                    self.phase = "TODO: CHANGE TO NEXUS!!!!"
        else
            res = self._fight_or_flight()
            if res != None:
                return res
            else:
                self.phase = "TODO: CHANGE TO NEXUS!!!!"

    def _fight_or_flight(self):
        '''
        We will almost always be trying to kill...
        But if there is a large enough enemy swarm... nah dude.
        Also, determine if we want to chase...
        '''
        currentMap = self.get_visible_map()
        currentRobos = self.get_visible_robots()
        
        # First, want to check for enemies immediate to you.
        for i in range(-1,2):
            for j in range(-1,2):
                state = self.get_in_direction(self.relative_pos_to_dir(i,j))
                if state != bc.HOLE and state != bc.EMPTY:
                if self._is_friendly(state) == False:
                    self.phase = "ATTACKING"
                    return self.attack(self.relative_pos_to_dir(i,j))
        
        # Secondly, we check if we should be chasing.
        for i in currentRobos:
            if self._is_friendly(i.id) == false:
                return self._check_friendly_near_enemy(currentMap, i.x, i.y)

    def _check_friendly_near_enemy(mapp, e.x, e.y):
        '''
        Returns None if there are no enemies with adjacent friendlies.
        Otherwise changes the phase and sets the destination coords.
        '''
        lf_spot = (-1,-1)
        for i in range(-1,2):
            for j in range(-1,2):
                state = self.get_relative_pos(e.x - self.curr_x+i, e.y - self.curr_y+j)
                
                # still trying to find a friendly near the enemy....
                if lf_spot == False and state != bc.HOLE and state != bc.EMPTY:
                    if self._is_friendly(state):
                        self.phase = "MOVING TO ATTACK"
                
                # found a friendly... determining where to go....
                elif lf_spot and state == bc.EMPTY:
                    self.dest_x = e.x - self.curr_x+i
                    self.dest_y = e.y - self.curr_y+j
                        return self._get_move_pathfind(self.dest_x, self.dest_y)
        return None

    ############### END METHODS FOR ATTACKING ##########################

                                                                                                
                                                                                                
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


    # What if an enemy is at/moved to that position???
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
        if self.new_nexus_target_x == self.curr_x and self.new_nexus_target_y == self.curr_y:
            self.log("changing signal...We are at NEXUS")
            self.phase = "IN NEXUS"
            newSig = self.NEXUS_MASK|self.signal
            self.signal(newSig)
            return None
        self.log("Heading to..."+self.new_nexus_target_x+", "+self.new_nexus_target_y)
        self.log("Currently at ..."+self.curr_x+", "+self.curr_y)
        currentRobos = self.get_visible_robots()
    
        for i in currentRobos:
            if self._is_friendly(i.id):
                signal = i.signal
                if self.NEXUS_MASK&signal == self.NEXUS_MASK:
                    self.phase = "FIND_EXISTING_NEXUS"
                    self.log("master at... "+i.x+", "+i.y)
                    self.log("Changed phase...FIND EXISTING NEXUS")
                    return None
        #if self._is_visible(self.new_nexus_target_x, self.new_nexus_target_y):
        #      if self._is_master_present(self.new_nexus_target_x, self.new_nexus_target_y):
        #        self.phase = "FIND_EXISTING_NEXUS"
        #        return None
        
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
        self.log(master_x,master_y)
        one = self._compute_moves(self.me().x, self.me().y, master_x, master_y+2)
        two = self._compute_moves(self.me().x, self.me().y, master_x-1, master_y+1)
        three = self._compute_moves(self.me().x, self.me().y, master_x+1, master_y+1)
        # This means that the target is
        self.log("finished computing... now deciding...")
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
                    return self._compute_min_nexus_dist(i.x, i.y)
        return (-1, -1)


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

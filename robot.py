import random
import math

             
"""
Branch from master, f190a4c951ba36d89fa1d8cea6f029ef58e8820a by vlchen888
Ident testing notes:

1) Each robot cycles through ident list successfully
2) Incorrectly identifies enemies (but possibly due to both teams having same ident list)
"""


class Util:
    @classmethod
    def sign(cls, x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0



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
    
    friend_ids = set([])
    enemy_ids = set([])
    
    # List of identifying signals every robot cycles through
    # If there is a mismatch, the offender is an enemy
    # List of identifying signals every robot cycles through
    # If there is a mismatch, the offender is an enemy
    IDENT_SIG_LEN = 8
    ident_sig = [6, 4, 2, 5, 3, 7, 1, 0]
    ident_sig_num = None


    num_turns = 0
    dest_x = -1
    dest_y = -1
    arr_map = []
    curr_x = -1
    curr_y = -1

    VIEW_SIZE = 7
    

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
        if self.ident_sig_num == None:
            self.ident_sig_num = self._init_ident_num()          # Current # identifier being broadcast
        
        if self.me()["team"] == 0:
            self.ident_sig = [0, 2, 4, 5, 7, 1, 6]
            
        # Log some metadata
        self.num_turns += 1 
        self._identify()
        
        # ##############################
        self.log(self.me()["signal"])
        self.log(self.friend_ids)
        self.log(self.enemy_ids)
        # ##############################
        
        self.curr_x = self.me()["x"]
        self.curr_y = self.me()["y"]

        self.map_arr = self.get_visible_map()

        num_friendlies = self._get_num_friendlies()

        if self.me()["team"] == 1:
            if self.phase == "FIND_TEAM":
                target_x = 10
                target_y = 10
                return self._get_move_pathfind(target_x, target_y)
            elif self.phase == "BUILD_NEXUS":
                pass
        else:
            return
        
    # Identifies the robot by broadcasting ident and checking neighbors
    #   Call on every turn
    def _identify(self):
        # Broadcast new signal first, then classify
        self._broadcast_sig()
        self._classify_visible_robots()
           
    # Broadcasts current ID message.
    def _broadcast_sig(self):
        #if self.ident_sig_num == None:
        #    self.ident_sig_num = 0
        self.signal(self.ident_sig[self.ident_sig_num])
        #self.log(ident_sig[ident_sig_num])
        #self.log(ident_sig_num)
        #self.log(self.me()["signal"])
        self.ident_sig_num += 1
        if self.ident_sig_num >= self.IDENT_SIG_LEN:
            self.ident_sig_num = 0
   
    # Classifies each visible robot.
    def _classify_visible_robots(self):
        robots = self.get_visible_robots()
        #self.log(ident_sig_num)
        for robot in robots:
            robot_id = robot.id
            robot_signal = robot.signal
            #self.log(robot_signal)
           
            # Classify based on signal
            # During the current robot's turn, all robots have either broadcasted the new ident_sig
            # or not
            old_ident_sig_num = self.ident_sig_num - 1
            if old_ident_sig_num < 0:
                old_ident_sig_num = self.IDENT_SIG_LEN - 1
           
            if (robot_id == self.me()["id"]):
                self.friend_ids.add(robot_id)
            elif (self.ident_sig[self.ident_sig_num] == robot_signal) or \
               (self.ident_sig[old_ident_sig_num] == robot_signal):
                self.friend_ids.add(robot_id)
            else:
                self.enemy_ids.add(robot_id)
               
            # Check for intersections and remove them from friends
            self.friend_ids = self.friend_ids.difference(self.friend_ids.intersection(self.enemy_ids))
           
    # Returns the index of the ident that a new robot should be initialized to
    def _init_ident_num(self):
        # Check for parents - 4 robots immediately adjoining the new robot. 1 of 3 cases
        #   - Starting robot, no neighbor   - return 0
        #   - Starting robot, neighbors     - return 0
        #   - Newly spawned robot           - return ident index of a neighbor
        parents = self._get_parents()
        # No parents - we are on turn 0
        if len(parents) == 0:
            # index is 0 on startup
            return 0
        else:
            # Get current signal of a parent
            new_sig = parents[0].signal
           
            # Find index of new signal and return it
            return self.ident_sig.index(new_sig)
       
       
    # Returns a list of the 4 robots that spawned a new robot, if they exist
    #   Used to initialize the signaling for a new robot to match that of the parent
    #   If erroneously called because two original robots are next to each other,
    #   doesn't matter, since all starting robots are initialized with same ident index
    def _get_parents(self):
        parents = []
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                thing_around = self.get_relative_pos(dx, dy)
                if (type(thing_around) == type(self)):
                    parents.append(thing_around)
        return parents
        

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
    

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
        self.log(self.num_turns)

        self.curr_x = self.me()["x"]
        self.curr_y = self.me()["y"]

        self.map_arr = self.get_visible_map()

        num_friendlies = self._get_num_friendlies()

        if self.me()["team"] == 1:
            if False:
                target_x = 10
                target_y = 10
                return self._get_move_pathfind(target_x, target_y)
            else:
                (target_x, target_y) = self._find_existing_nexus()
                if target_y != -1:
                    return self._get_move_pathfind(target_x, target_y)
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


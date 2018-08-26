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
    
    # Phases: FIND_TEAM, BUILD_NEXUS, FIND_NEW_NEXUS, MOVE_TO_NEW_NEXUS, etc...
    phase = "FIND_TEAM"
    NEXUS_MASK = 1 # remove me
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

        if self.me()["team"] == 1:
            if self.phase == "FIND_TEAM":
                if self.num_turns > 20:
                    self.phase = "FIND_NEW_NEXUS"
                target_x = 10
                target_y = 10
                return self._get_move_pathfind(target_x, target_y)
            elif self.phase == "FIND_NEW_NEXUS":
                self._find_new_nexus()
            elif self.phase == "MOVE_TO_NEW_NEXUS":
                return self._get_move_find_new_nexus()
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


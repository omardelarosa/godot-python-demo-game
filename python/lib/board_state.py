from typing import List, Tuple
from astar import AStar
import numpy as np


class BoardState(AStar):
    ALLOW_INVALID_MOVES = True

    Y_WEIGHT = 2.0
    Y_WEIGHT_EUCLID = 0.0
    EMPTY_TILE = -1
    FILLED_TILE = 1
    MOVABLE_TILE = 0
    FRIENDLY_TILE = 1
    ENEMY_TILE = 2
    NEIGHBOR_TILE = 3

    DEFAULT_DISTANCE_BUDGET = 3
    DEFAULT_GROUND_LEVEL_Y = 0
    MASK_DEFAULT_PIVOT_VALUE = -1

    NEIGHBORING_DIRECTIONS_MASK = [
        # forward,backward,left,right - own level
        (1, 0, 0),
        (0, 0, 1),
        (-1, 0, 0),
        (0, 0, -1),
        # forward,backward,left,right - above one level
        (1, 1, 0),
        (0, 1, 1),
        (-1, 1, 0),
        (0, 1, -1),
        # forward,backward,left,right - below one level
        (1, -1, 0),
        (0, -1, 1),
        (-1, -1, 0),
        (0, -1, -1),
    ]

    @staticmethod
    def create_grid_map_from_elevation_array(array_2d_elevation, shape_tup):
        """Create a rectangular GridMap from a 2D-elevation array"""
        x, y = shape_tup

        grid = {}
        for x in range(0, x):
            for y in range(0, y):
                elevation = array_2d_elevation[y][x]
                # skip empty tiles
                if elevation != None:
                    tile = BoardState.FILLED_TILE
                    pos = (x, elevation, y)
                    grid[pos] = tile
        return grid

    @staticmethod
    def create_2d_position_list_from_2d_mask(
        array_2d_mask, mask_shape_tup, grid_pivot_pos=(0, 0)
    ):
        """Create a rectangular GridMap from a 2D-elevation array"""
        sx, sy = mask_shape_tup

        mask_pivots = []
        for x in range(0, sx):
            for y in range(0, sy):
                mask_val = array_2d_mask[y][x]
                # skip empty tiles and pivot tiles
                if mask_val == BoardState.MASK_DEFAULT_PIVOT_VALUE:
                    mask_pivots.append((x, y))

        pivot_position_in_mask = (0, 0)
        if len(mask_pivots) == 0:
            print(
                f"warning: no pivot position found in mask. using default pivot of {pivot_position_in_mask}"
            )
        elif len(mask_pivots) >= 1:
            pivot_position_in_mask = mask_pivots[0]
            if len(mask_pivots) > 1:
                print(
                    f"warning: multiple pivot positions found in mask.  using first one: {pivot_position_in_mask}"
                )

        grid_map = {}
        for x in range(0, sx):
            for y in range(0, sy):
                mask_val = array_2d_mask[y][x]
                if mask_val != None and mask_val != BoardState.MASK_DEFAULT_PIVOT_VALUE:
                    px, py = pivot_position_in_mask
                    # offset mask so pivot is 0,0
                    gx, gy = grid_pivot_pos
                    out_pos = (x - px + gx, y - py + gy)
                    grid_map[out_pos] = mask_val
        return grid_map

    def __init__(self, _grid_map):
        self.grid_map = _grid_map
        self.terrain_grid = {}
        self.terrain_grid_2d = {}
        self.meta_grid = {}

        # initialize the immutable terrain grid
        self._set_terrain_grid(self.grid_map)

    # Astar methods

    def dist(self, n1, n2):
        return self.manhattan_dist(n1, n2)

    def euclidean_distance(self, n1, n2):
        (x1, y1, z1) = n1
        (x2, y2, z2) = n2
        return np.sqrt(
            ((x2 - x1) ** 2)
            + (((y2 - y1) ** 2) * BoardState.Y_WEIGHT_EUCLID)
            + ((z2 - z1) ** 2)
        )

    def get_neighbors_by_2d_mask(
        self, pivot_position, mask_2d
    ) -> List[Tuple[int, int, int]]:
        x, _, z = pivot_position
        grid_pivot_pos_2d = (x, z)
        positions_2d_mask = BoardState.create_2d_position_list_from_2d_mask(
            mask_2d["mask"], mask_2d["shape"], grid_pivot_pos=grid_pivot_pos_2d
        )
        positions_3d = []
        for pos_2d in positions_2d_mask:
            pos_3d = self.get_grid_pos_2d(pos_2d)
            if pos_3d:
                positions_3d.append(pos_3d)
        return positions_3d

    def get_nearest_node_from_position(self, position):
        all_positions = list(self.terrain_grid.keys())
        return self.get_nearest_node_from_nodes(position, all_positions)

    def get_nearest_node_from_nodes(self, position, nodes_list):
        # TODO: make this configurable in which distance function it uses
        min_distance = float("INF")
        min_distance_pos = None
        for neighbor_position in nodes_list:
            n_dist = self.euclidean_distance(position, neighbor_position)
            if n_dist <= min_distance:
                min_distance = n_dist
                min_distance_pos = neighbor_position
        return min_distance_pos, min_distance

    def manhattan_dist(self, n1, n2):
        (x1, y1, z1) = n1
        (x2, y2, z2) = n2
        return abs(x2 - x1) + (abs((y2 - y1)) * BoardState.Y_WEIGHT) + abs(z2 - z1)

    def heuristic_cost_estimate(self, n1, n2):
        """computes the 'manhattan' distance between two (x,y,z) tuples"""
        return self.dist(n1, n2)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return self.dist(n1, n2)

    def neighbors(self, node):
        """for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
        nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        node_np = np.array(node)
        neighbors = []
        for direction in BoardState.NEIGHBORING_DIRECTIONS_MASK:
            dir_np = np.array(direction)
            dir_tup = tuple(dir_np + node_np)
            if not self.is_empty_tile(dir_tup):
                neighbors.append(dir_tup)
        return neighbors

    def movable_area(self, root, distance_budget=DEFAULT_DISTANCE_BUDGET):
        """BFS algo for creating a movable area"""
        q = [root]
        discovered = set([root])
        # set.add(root)
        while len(q):
            v = q.pop(0)
            if self.distance_between(v, root) >= distance_budget:
                return list(discovered)
            for neighbor in self.neighbors(v):
                if neighbor not in discovered:
                    discovered.add(neighbor)
                    q.append(neighbor)
        return list(discovered)

    def setup(self):
        pass

    def _set_terrain_grid(self, grid_map_position_list):
        print("creating terrain grid")

        self.terrain_grid = {}
        self.terrain_grid_2d = {}
        for p in grid_map_position_list:
            self.set_grid_pos(self.terrain_grid, p, BoardState.FILLED_TILE)
            x, y, z = p
            pos_2d = (x, z)
            if pos_2d not in self.terrain_grid_2d:
                self.terrain_grid_2d[pos_2d] = []
            # adds a 2D-representation of the board for certain 2-d only operations
            self.terrain_grid_2d[pos_2d].append(p)

    def is_empty_tile(self, pos):
        grid_value = self.get_grid_pos(self.terrain_grid, pos)
        if grid_value == BoardState.EMPTY_TILE:
            return True
        return False

    def is_valid_move(self, to_position):
        if BoardState.ALLOW_INVALID_MOVES:
            return True
        grid_value = self.get_grid_pos(self.terrain_grid, to_position)
        if grid_value == BoardState.EMPTY_TILE:
            return False
        return True

    def get_grid_pos_2d(self, position: Tuple[int, int]) -> Tuple[int, int, int]:
        if position in self.terrain_grid_2d:
            # return the max y (i.e. hieghest position in vertical stack)
            max_y_pos = max(self.terrain_grid_2d[position], key=lambda x: x[1])
            if max_y_pos in self.terrain_grid:
                return max_y_pos
        else:
            return None

    def get_grid_pos(self, grid, position):
        if position in grid:
            return grid[position]
        else:
            return BoardState.EMPTY_TILE

    def set_grid_pos(self, grid, position, value):
        try:
            grid[position] = value
        except:
            print("update to grid failed for ", position, value)

    def update_meta_grid(
        self,
        movable_tiles=[],
        attackable_tiles=[],
        friendly_tiles=[],
        enemy_tiles=[],
        self_tiles=[],
    ):

        # Clear meta grid
        self.meta_grid = {}

        for t in movable_tiles:
            self.set_grid_pos(self.meta_grid, t, BoardState.MOVABLE_TILE)

        # TODO: update this to support "long-range" attacks
        for t in attackable_tiles:
            self.set_grid_pos(self.meta_grid, t, BoardState.NEIGHBOR_TILE)

        for t in friendly_tiles:
            self.set_grid_pos(self.meta_grid, t, BoardState.FRIENDLY_TILE)

        for t in enemy_tiles:
            self.set_grid_pos(self.meta_grid, t, BoardState.ENEMY_TILE)

        # TODO: come up with a tile color for self tiles
        # for t in self_tiles:
        #     self.set_grid_pos(self.meta_grid, t, BoardState.EMPTY_TILE)
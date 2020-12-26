from python.test.test_game_state import DEFAULT_ELEVATION_MAP
from python.lib.board_state import BoardState
from .constants import (
    DEFAULT_ELEVATION_MAP_SHAPE,
    DEFAULT_ELEVATION_MAP,
    DEFAULT_EXPECTED_OUTPUT_GRID_MAP,
)


def test_BoardState_create_grid_map_from_elevation_array():

    elevation_map_2d = DEFAULT_ELEVATION_MAP

    shape = DEFAULT_ELEVATION_MAP_SHAPE

    grid_map = BoardState.create_grid_map_from_elevation_array(elevation_map_2d, shape)

    expected_grid_map = DEFAULT_EXPECTED_OUTPUT_GRID_MAP

    for k, v in grid_map.items():
        # print(f"{k}: {v} -> {expected_grid_map[k]}")
        assert k in expected_grid_map
        assert v == expected_grid_map[k]

    assert grid_map == expected_grid_map


def test_BoardState_create_position_list_from_2d_mask():

    # a cross mask in a 3x4 neighborhood
    mask_2d = [
        [None, BoardState.FILLED_TILE, None],
        [
            BoardState.FILLED_TILE,
            BoardState.MASK_DEFAULT_PIVOT_VALUE,
            BoardState.FILLED_TILE,
        ],
        [None, BoardState.FILLED_TILE, None],
        [None, BoardState.FILLED_TILE, None],
    ]

    shape = (3, 4)

    # without a grid pivot
    grid_map = BoardState.create_2d_position_list_from_2d_mask(mask_2d, shape)

    expected_grid_map = {
        (-1, 0): BoardState.FILLED_TILE,
        (0, -1): BoardState.FILLED_TILE,
        (0, 1): BoardState.FILLED_TILE,
        (1, 0): BoardState.FILLED_TILE,
        (0, 2): BoardState.FILLED_TILE,
    }

    assert grid_map == expected_grid_map

    # with a grid pivot provided

    grid_pivot_pos = (1, 1)

    grid_map_rel = BoardState.create_2d_position_list_from_2d_mask(
        mask_2d, shape, grid_pivot_pos
    )

    expected_grid_map_relative = {
        (0, 1): BoardState.FILLED_TILE,
        (1, 0): BoardState.FILLED_TILE,
        (2, 1): BoardState.FILLED_TILE,
        (1, 2): BoardState.FILLED_TILE,
        (1, 3): BoardState.FILLED_TILE,
    }

    assert grid_map_rel == expected_grid_map_relative


def test_board_state():
    span = 8  # the board's square radius

    grid = []

    for x in range(-(span - 1), span):
        for y in range(-1, 2):
            for z in range(-(span - 1), span):
                grid.append((x, y, z))

    board = BoardState(grid)

    board.setup()

    # Check center tile neighbors
    expected_neighbors = BoardState.NEIGHBORING_DIRECTIONS_MASK
    CENTER_TILE_POS = (0, 0, 0)
    actual_neighbors = board.neighbors(CENTER_TILE_POS)
    assert expected_neighbors == actual_neighbors

    # Check corner cases
    corners = [(-1, 0, -1), (1, 0, 1), (1, 0, -1), (-1, 0, 1)]
    corner_positions = [((span - 1) * x, y, (span - 1) * z) for x, y, z in corners]
    idx = 0
    for corner_pos in corner_positions:
        x, y, z = corners[idx]
        s = span - 1
        corner_neighbors = board.neighbors(corner_pos)
        print(
            "corner: ",
            corners[idx],
            corner_pos,
            " corner_neighbors: ",
            corner_neighbors,
        )
        assert len(corner_neighbors) == 6
        invalid_tiles = [
            ((s * x) + x, y, s * z),
            ((s * x), y, (s * z) + z),
            ((s * x) + x, y + 1, s * z),
            ((s * x), y + 1, (s * z) + z),
            ((s * x) + x, y - 1, s * z),
            ((s * x), y - 1, (s * z) + z),
        ]

        for invalid_tile in invalid_tiles:
            assert invalid_tile not in corner_neighbors

        idx += 1

    # Check pathfinding
    diagonal_path = board.astar(corner_positions[0], corner_positions[1])

    diagonal_path_list = list(diagonal_path)

    expected_diagonal_path = [
        (-7, 0, -7),
        (-6, 0, -7),
        (-5, 0, -7),
        (-4, 0, -7),
        (-3, 0, -7),
        (-2, 0, -7),
        (-1, 0, -7),
        (0, 0, -7),
        (1, 0, -7),
        (2, 0, -7),
        (3, 0, -7),
        (3, 0, -6),
        (3, 0, -5),
        (3, 0, -4),
        (4, 0, -4),
        (5, 0, -4),
        (6, 0, -4),
        (6, 0, -3),
        (6, 0, -2),
        (6, 0, -1),
        (6, 0, 0),
        (6, 0, 1),
        (6, 0, 2),
        (6, 0, 3),
        (7, 0, 3),
        (7, 0, 4),
        (7, 0, 5),
        (7, 0, 6),
        (7, 0, 7),
    ]

    assert diagonal_path_list == expected_diagonal_path

    lateral_path = board.astar(corner_positions[0], corner_positions[2])

    lateral_path_list = list(lateral_path)

    expected_lateral_path = [
        (-7, 0, -7),
        (-6, 0, -7),
        (-5, 0, -7),
        (-4, 0, -7),
        (-3, 0, -7),
        (-2, 0, -7),
        (-1, 0, -7),
        (0, 0, -7),
        (1, 0, -7),
        (2, 0, -7),
        (3, 0, -7),
        (4, 0, -7),
        (5, 0, -7),
        (6, 0, -7),
        (7, 0, -7),
    ]

    assert lateral_path_list == expected_lateral_path

    # Test movable area checking
    movable_area_from_center = board.movable_area(CENTER_TILE_POS, distance_budget=2)

    print("[")
    for pos in movable_area_from_center:
        print(f"{pos},")
    print("]")

    expected_movable_area = [
        (0, -1, -1),
        (0, -1, -2),
        (-1, 1, -1),
        (0, -1, 1),
        (0, 1, 0),
        (-1, 1, 1),
        (2, 1, 0),
        (1, -1, 1),
        (1, -1, -1),
        (0, 0, -1),
        (0, 0, -2),
        (0, 0, 1),
        (1, 0, 1),
        (1, 1, 0),
        (1, 0, -1),
        (-1, -1, -1),
        (0, -1, 0),
        (-1, -1, 1),
        (-1, 1, 0),
        (-2, 1, 0),
        (0, 1, 2),
        (1, -1, 0),
        (2, -1, 0),
        (-1, 0, 1),
        (-1, 0, -1),
        (0, 0, 0),
        (1, 0, 0),
        (2, 0, 0),
        (-1, -1, 0),
        (0, 1, -1),
        (-2, -1, 0),
        (0, -1, 2),
        (0, 1, 1),
        (0, 1, -2),
        (-1, 0, 0),
        (-2, 0, 0),
        (0, 0, 2),
        (1, 1, -1),
        (1, 1, 1),
    ]

    assert movable_area_from_center == expected_movable_area
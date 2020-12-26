from python.lib.events import Events
from python.lib.board_state import BoardState
from python.lib.game_state import GameState
from unittest.mock import MagicMock
from collections import Counter

from .constants import (
    DEFAULT_EXPECTED_OUTPUT_GRID_MAP,
    DEFAULT_ELEVATION_MAP,
    DEFAULT_ELEVATION_MAP_SHAPE,
)

DEFAULT_RANDOM_SEED = 20201224

DEFAULT_INITIAL_GAME_STATE = {
    "grid": BoardState.create_grid_map_from_elevation_array(
        DEFAULT_ELEVATION_MAP, DEFAULT_ELEVATION_MAP_SHAPE
    ),
    "characters": [
        {
            "id": "i1",
            "position": (1, 0, 1),
            "name": "c1",
            "hit_points": 1,
            "last_position": (1, 0, 1),
            "team_id": "t2",
        },
        {
            "id": "i2",
            "position": (5, 2, 0),
            "name": "c2",
            "hit_points": 1,
            "last_position": (5, 2, 0),
            "team_id": "t1",
        },
        {
            "id": "i3",
            "position": (6, 0, 1),
            "name": "c3",
            "hit_points": 1,
            "last_position": (6, 0, 1),
            "team_id": "t1",
        },
        {
            "id": "i4",
            "position": (4, 0, 2),
            "name": "c4",
            "hit_points": 1,
            "last_position": (4, 0, 2),
            "team_id": "t2",
        },
        {
            "id": "i5",
            "position": (7, -1, 5),
            "name": "c5",
            "hit_points": 1,
            "last_position": (7, -1, 5),
            "team_id": "t1",
        },
        {
            "id": "i6",
            "position": (7, 0, 9),
            "name": "c6",
            "hit_points": 1,
            "last_position": (7, 0, 9),
            "team_id": "t2",
        },
    ],
    "teams": [
        {"id": "t1", "name": "t1"},
        {"id": "t2", "name": "t2"},
    ],
    "num_characters_per_team": 3,
    "num_teams": 2,
}


def test_GameState_setup():

    gs = GameState(
        events=Events,
        initial_state=DEFAULT_INITIAL_GAME_STATE,
        rng_seed=DEFAULT_RANDOM_SEED,
    )

    gs.broadcast = MagicMock(name="broadcast")

    gs.setup(skip_character_team_assignment=True, skip_character_repositioning=True)

    gs.broadcast.assert_called_with(
        Events.EVENT_PLAYER_MOVE_SUCCESS,
        gs.selected_character.position,
        gs.selected_character.position,
    )

    output_terrain_grid = DEFAULT_EXPECTED_OUTPUT_GRID_MAP

    output_meta_grid = {
        (2, 1, 1): BoardState.NEIGHBOR_TILE,
        (1, 0, 1): BoardState.MOVABLE_TILE,
        (2, 1, 0): BoardState.MOVABLE_TILE,
        (0, 0, 0): BoardState.MOVABLE_TILE,
        (1, 0, 0): BoardState.NEIGHBOR_TILE,
        (2, 1, 2): BoardState.MOVABLE_TILE,
        (1, 0, 3): BoardState.MOVABLE_TILE,
        (0, 0, 2): BoardState.MOVABLE_TILE,
        (1, 0, 2): BoardState.NEIGHBOR_TILE,
        (0, 0, 1): BoardState.NEIGHBOR_TILE,
    }

    for k, v in output_meta_grid.items():
        print(f"{k}: {v},")

    expected_output_state = {
        "selected_character": DEFAULT_INITIAL_GAME_STATE["characters"][0],
        "grid": output_terrain_grid,
        "meta_grid": output_meta_grid,
        "characters": DEFAULT_INITIAL_GAME_STATE["characters"],
        "teams": DEFAULT_INITIAL_GAME_STATE["teams"],
    }

    actual_output_state = gs.state()

    for k, v in actual_output_state.items():
        # DEBUG:
        print(f"[{k}]: actual: {v}, expected: {expected_output_state[k]}")
        assert actual_output_state[k] == expected_output_state[k]


def test_GameState_setup_with_auto_assigned_positions_and_teams():

    initial_state = {**DEFAULT_INITIAL_GAME_STATE, "characters": [], "teams": []}

    gs = GameState(
        events=Events,
        initial_state=initial_state,
        rng_seed=DEFAULT_RANDOM_SEED,
    )

    gs.broadcast = MagicMock(name="broadcast")

    gs.setup()

    gs.broadcast.assert_called_with(
        Events.EVENT_PLAYER_MOVE_SUCCESS,
        gs.selected_character.position,
        gs.selected_character.position,
    )

    expected_num_characters = int(
        initial_state["num_characters_per_team"] * initial_state["num_teams"]
    )

    assert len(gs.characters) == expected_num_characters
    assert len(gs.teams) == initial_state["num_teams"]


def test_GameState_on_request_player_move():
    gs = GameState(
        events=Events,
        initial_state=DEFAULT_INITIAL_GAME_STATE,
        rng_seed=DEFAULT_RANDOM_SEED,
    )

    gs.broadcast = MagicMock(name="broadcast")

    # Use fixed positions
    gs.setup(skip_character_team_assignment=True, skip_character_repositioning=True)

    # Check initial position
    # print("selected character: ", gs.state()["selected_character"])
    assert (
        gs.state()["selected_character"]["position"]
        == DEFAULT_INITIAL_GAME_STATE["characters"][0]["position"]
    )

    # Valid move
    gs.on_request_player_move((0, 0, 1))

    from_pos = (1, 0, 1)  # aka character start position
    to_pos = (1, 0, 2)
    gs.broadcast.assert_called_with(
        Events.EVENT_PLAYER_MOVE_SUCCESS,
        from_pos,
        to_pos,
    )

    assert gs.state()["selected_character"]["position"] == to_pos

    # Invalid move
    gs.on_request_player_move((0, 0, 10))

    assert gs.state()["selected_character"]["position"] == to_pos

    # No movement change
    gs.broadcast.assert_called_with(
        Events.EVENT_PLAYER_MOVE_FAILED,
        to_pos,
        to_pos,
    )


def test_GameState_create_characters():
    gs = GameState(
        events=Events,
        initial_state={
            "grid": DEFAULT_INITIAL_GAME_STATE["grid"],
            "num_characters_per_team": 3,
            "num_teams": 2,
        },
    )

    gs.setup()

    # Each character is assigned a random position on the grid
    positions = [c.position for c in gs.characters]
    ids = [c.id for c in gs.characters]
    character_team_ids = [c.team_id for c in gs.characters]
    team_ids = [t.id for t in gs.teams]
    assert len(gs.characters) > 0

    # ensure each character has a unique id
    assert len(ids) == gs.get_total_num_characters()
    assert len(ids) == len(set(ids))

    # ensure the number of unique positions matches the total num of characters
    assert len(positions) == gs.get_total_num_characters()
    assert len(positions) == len(set(positions))

    # ensure the number of unique positions matches the total num of characters
    assert len(set(character_team_ids)) == gs.num_teams

    # ensure there is an even number of teams
    actual_counts = Counter(character_team_ids)
    expected_counts = Counter(
        {
            (team_ids[0]): 3,
            (team_ids[1]): 3,
        }
    )
    assert actual_counts == expected_counts

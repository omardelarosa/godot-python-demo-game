from python.lib.masks import CROSS_MASK, SPEAR_MASK, SWORD_MASK, X_MASK
import numpy as np

import random

from numpy.lib.shape_base import tile

from .conversions import Conversions
from .board_state import BoardState
from .character import Character
from .team import Team


class GameState:

    DEFAULT_PLAYER_START_POS = (0, 0, 0)
    DEFAULT_MOVE_DISTANCE_BUDGET = 3
    MINIMUM_MOVE_DISTANCE = 0.1
    MAXIMUM_MOVE_DISTANCE = 0.5
    NULL_GRID = []
    DEFAULT_NUM_CHARACTERS_PER_TEAM = 2
    DEFAULT_NUM_TEAMS = 2
    NULL_CHARACTER = Character({"id": Character.NULL_ID})
    NULL_TEAM = Team({"id": Team.NULL_ID})
    AVAILABLE_ATTACK_MASKS = [CROSS_MASK, SPEAR_MASK, SWORD_MASK, X_MASK]

    def __init__(self, events, game_manager=None, initial_state={}, rng_seed=None):

        random.seed(rng_seed)

        self._initial_state = initial_state
        self.events = events
        self.selected_character = (
            GameState.NULL_CHARACTER
        )  # Prevent selected character from ever being None to make code less complex
        self.game_manager = game_manager
        if "grid" in self._initial_state:
            self.board_state = BoardState(self._initial_state["grid"])
        else:
            self.board_state = BoardState(GameState.NULL_GRID)

        self.cursor_position = GameState.DEFAULT_PLAYER_START_POS
        self.movable_tiles = []
        self.attackable_tiles = []
        self.selected_character_attack_mask = SPEAR_MASK

        # If using preloaded teams
        initial_character_list = (
            initial_state["characters"] if "characters" in self._initial_state else []
        )
        initial_team_list = (
            initial_state["teams"] if "teams" in self._initial_state else []
        )
        if initial_team_list and initial_character_list:
            self.num_characters_per_team = int(
                len(initial_character_list) / len(initial_team_list)
            )
            self.num_teams = len(initial_team_list)
        else:
            # Generated teams
            self.num_characters_per_team = int(
                initial_state["num_characters_per_team"]
                if "num_characters_per_team" in initial_state
                else GameState.DEFAULT_NUM_CHARACTERS_PER_TEAM
            )

            self.num_teams = int(
                initial_state["num_teams"]
                if "num_teams" in initial_state
                else GameState.DEFAULT_NUM_TEAMS
            )

        self.create_teams(teams=initial_team_list)
        self.create_characters(characters=initial_character_list)

    def state(self):
        """
        Returns a serialized Dictionary of the game state for use in Godot environment
        """
        return {
            "grid": self.board_state.terrain_grid,
            "meta_grid": self.board_state.meta_grid,
            "selected_character": dict(self.selected_character),
            "characters": [dict(c) for c in self.characters],  # serialize characters
            "teams": [dict(t) for t in self.teams],
        }

    def setup(
        self, skip_character_repositioning=False, skip_character_team_assignment=False
    ):
        self.board_state.setup()

        if not skip_character_repositioning:
            self.assign_character_positions()

        if not skip_character_team_assignment:
            self.assign_character_teams()

        # set first character in list as selected character. TODO: make this less random.
        self.selected_character = self.characters[0]

        print("selected_character: ", self.selected_character)

        self.movable_tiles = self.get_movable_tiles_from_player_pos(
            self.selected_character.position
        )

        self.board_state.update_meta_grid(
            movable_tiles=self.movable_tiles,
            # new neighbors
            attackable_tiles=self.board_state.neighbors(
                self.selected_character.position
            ),
            friendly_tiles=[],
            enemy_tiles=[],
            self_tiles=[],
        )

    def create_teams(self, teams=[]):
        if teams:
            self.teams = [Team(t) for t in teams]
        else:
            self.teams = [Team() for _ in range(0, self.num_teams)]

    def create_characters(self, characters=[]):
        if characters:
            self.characters = [Character(c) for c in characters]
        else:
            num_characters = self.get_total_num_characters()
            self.characters = [Character() for _ in range(0, num_characters)]

    def assign_character_positions(self):
        tile_positions = list(self.board_state.terrain_grid.keys())
        num_characters_total = self.get_total_num_characters()
        available_positions = random.sample(tile_positions, num_characters_total)
        for c in self.characters:
            c.position = available_positions.pop()
            c.last_position = c.position  # this is initially the same

    def assign_character_teams(self):
        num_characters_total = self.get_total_num_characters()
        sampled_characters = random.sample(self.characters, num_characters_total)
        print("sampled_characters: ", len(sampled_characters), num_characters_total)
        for t in self.teams:
            for _ in range(0, self.num_characters_per_team):
                character = sampled_characters.pop()
                character.team_id = t.id
                # print("character: ", character, " team: ", t)

    def move_character(self, character, move_directional_tup):
        next_position = np.array(move_directional_tup) + np.array(character.position)

        (
            nearest_grid_node_from_position,
            _,
        ) = self.board_state.get_nearest_node_from_position(next_position)
        neighbors_of_player_position = self.board_state.neighbors(character.position)

        (
            player_neighbor_closest_to_desired_position,
            distance,
        ) = self.board_state.get_nearest_node_from_nodes(
            nearest_grid_node_from_position,
            neighbors_of_player_position,
        )

        if self.is_valid_move(
            character.position, player_neighbor_closest_to_desired_position, distance
        ):
            prev_position = character.position
            character.position = tuple(player_neighbor_closest_to_desired_position)

            self.attackable_tiles = self.get_attackable_tiles_from_player_pos(
                self.selected_character.position
            )

            # TODO: remove other players from attackable tiles

            self.board_state.update_meta_grid(
                movable_tiles=self.movable_tiles,
                # new neighbors
                attackable_tiles=self.attackable_tiles,
                friendly_tiles=[],
                enemy_tiles=[],
                self_tiles=[],
            )
            self.broadcast(
                self.events.EVENT_CHARACTER_MOVE_SUCCESS,
                dict(character),
                prev_position,
                character.position,
            )
            return True, prev_position, character.position
        else:
            self.broadcast(
                self.events.EVENT_CHARACTER_MOVE_FAILED,
                dict(character),
                character.position,
                character.position,
            )
            return False, character.position, character.position

    def is_valid_cursor_move(self, current_pos, next_pos, distance):
        return True

    def move_cursor(self, cursor_current_pos, move_directional_tup):
        next_position = np.array(move_directional_tup) + np.array(cursor_current_pos)

        (
            nearest_grid_node_from_position,
            distance,
        ) = self.board_state.get_nearest_node_from_position(next_position)
        if self.is_valid_cursor_move(
            cursor_current_pos, nearest_grid_node_from_position, distance
        ):
            prev_position = self.cursor_position
            self.cursor_position = nearest_grid_node_from_position

            self.board_state.update_meta_grid(
                movable_tiles=self.movable_tiles,
                attackable_tiles=self.attackable_tiles,
                friendly_tiles=[],
                enemy_tiles=[],
                self_tiles=[],
                cursor_position=self.cursor_position,
            )
            self.broadcast(
                self.events.EVENT_CURSOR_MOVE_FAILED,
                prev_position,
                self.cursor_position,
            )
            return True, cursor_current_pos, self.cursor_position
        else:
            self.broadcast(
                self.events.EVENT_CURSOR_MOVE_FAILED,
                self.cursor_position,
                self.cursor_position,
            )
            return False, cursor_current_pos, cursor_current_pos

    def on_request_player_move(self, move_directional_vec):
        if self.selected_character:
            # TODO: move player on board
            move_delta_tup = Conversions.serialize_gd_to_py(move_directional_vec)

            did_move, prev_pos, curr_pos = self.move_character(
                self.selected_character, move_delta_tup
            )

            if did_move:
                self.broadcast(
                    self.events.EVENT_PLAYER_MOVE_SUCCESS,
                    prev_pos,
                    curr_pos,
                )
            else:
                self.broadcast(
                    self.events.EVENT_PLAYER_MOVE_FAILED,
                    prev_pos,
                    curr_pos,
                )

    def on_request_cursor_move(self, move_directional_vec):
        if self.cursor_position:
            self.move_cursor(self.cursor_position, move_directional_vec)

    def get_total_num_characters(self):
        return int(self.num_characters_per_team * self.num_teams)

    def is_valid_move(self, player_pos, desired_position, distance):
        if distance >= GameState.MAXIMUM_MOVE_DISTANCE:
            return False
        if desired_position not in self.movable_tiles:
            return False
        if desired_position == player_pos:
            return False

        # TODO: this needs to validate against other player positions etc

        return True

    def on_end_turn(self, *args):
        self.selected_character.last_position = self.selected_character.position

        # swap characters
        curr_char_idx = self.characters.index(self.selected_character)

        self.selected_character = self.characters[
            (curr_char_idx + 1) % len(self.characters)
        ]

        self.movable_tiles = self.get_movable_tiles_from_player_pos(
            self.selected_character.position
        )

        self.attackable_tiles = self.get_attackable_tiles_from_player_pos(
            self.selected_character.position
        )

        # TODO: make this non-random
        # random.shuffle(GameState.AVAILABLE_ATTACK_MASKS)
        self.selected_character_attack_mask = random.sample(
            GameState.AVAILABLE_ATTACK_MASKS, 1
        )[0]

        # # TODO: update friendly tiles, enemy tiles, self tiles, etc.
        self.board_state.update_meta_grid(
            movable_tiles=self.movable_tiles,
            # new neighbors
            attackable_tiles=self.attackable_tiles,
            friendly_tiles=[],
            enemy_tiles=[],
            self_tiles=[],
        )

        self.broadcast(
            self.events.EVENT_PLAYER_MOVE_SUCCESS,
            self.selected_character.position,
            self.selected_character.position,
        )

        # TODO: change players/teams etc.

        # TODO: check for combat

        # TODO: resolve all combat

        # TODO: add combat turn to queue if necessary

    def get_movable_tiles_from_player_pos(self, player_pos):
        return self.board_state.movable_area(
            player_pos, distance_budget=GameState.DEFAULT_MOVE_DISTANCE_BUDGET
        )

    def get_attackable_tiles_from_player_pos(self, player_pos):
        # Get tiles from mask
        attackable_tiles = self.board_state.get_neighbors_by_2d_mask(
            player_pos, self.selected_character_attack_mask
        )

        return attackable_tiles

    def broadcast(self, event_name, *args):
        if self.game_manager != None:
            self.game_manager.broadcast(event_name, *args)
        else:
            print(
                "warning: no game_manager bound to game_state.  event bubbling disabled"
            )

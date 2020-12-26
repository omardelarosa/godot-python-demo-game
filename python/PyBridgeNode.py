from python.lib.events import Events
from python.lib.conversions import Conversions
from godot import exposed, Node, signal, ResourceLoader

from .lib.game_state import GameState
from .lib.subscribable import Subscribable

from math import floor
import numpy as np

from enum import Enum

# Shared constants
CONSTANTS = ResourceLoader.load("res://Config/Constants.gd")


class GDEvents(Enum):
    # Register constants
    # Turn management
    EVENT_REQUEST_END_TURN = CONSTANTS.get(Events.EVENT_REQUEST_END_TURN.value)

    # Character/player movement events
    EVENT_REQUEST_PLAYER_MOVE = CONSTANTS.get(Events.EVENT_REQUEST_PLAYER_MOVE.value)
    EVENT_PLAYER_MOVE_SUCCESS = CONSTANTS.get(Events.EVENT_PLAYER_MOVE_SUCCESS.value)
    EVENT_PLAYER_MOVE_FAILED = CONSTANTS.get(Events.EVENT_PLAYER_MOVE_FAILED.value)
    EVENT_CHARACTER_MOVE_SUCCESS = CONSTANTS.get(
        Events.EVENT_CHARACTER_MOVE_SUCCESS.value
    )
    EVENT_CHARACTER_MOVE_FAILED = CONSTANTS.get(
        Events.EVENT_CHARACTER_MOVE_FAILED.value
    )

    # Cursor movement events
    EVENT_REQUEST_CURSOR_MOVE = CONSTANTS.get(Events.EVENT_REQUEST_CURSOR_MOVE.value)
    EVENT_CURSOR_MOVE_SUCCESS = CONSTANTS.get(Events.EVENT_CURSOR_MOVE_SUCCESS.value)
    EVENT_CURSOR_MOVE_FAILED = CONSTANTS.get(Events.EVENT_CURSOR_MOVE_FAILED.value)
    EVENT_CURSOR_SELECT = CONSTANTS.get(Events.EVENT_CURSOR_SELECT.value)
    EVENT_GAME_STATE_READY = CONSTANTS.get(Events.EVENT_GAME_STATE_READY.value)


@exposed
class PyBridgeNode(Node):

    # Signals
    game_state_ready = signal(Events.EVENT_GAME_STATE_READY.value)

    player_move_success = signal(Events.EVENT_PLAYER_MOVE_SUCCESS.value)
    player_move_failed = signal(Events.EVENT_PLAYER_MOVE_FAILED.value)

    cursor_move_success = signal(Events.EVENT_CURSOR_MOVE_SUCCESS.value)
    cursor_move_failed = signal(Events.EVENT_CURSOR_MOVE_FAILED.value)

    def _ready(self):
        print("PyBridgeNode ready for setup()")

    def setup(self, gd_dict_of_gd_game_stat):
        # print('setup!')
        serialized_game_state_obj = Conversions.serialize_gd_to_py(
            gd_dict_of_gd_game_stat
        )

        self.subscribable = Subscribable()

        self.game_state = GameState(
            events=GDEvents, game_manager=self, initial_state=serialized_game_state_obj
        )

        self.game_state.setup()

        # Register signal callbacks
        self.callbacks = {
            (GDEvents.EVENT_REQUEST_PLAYER_MOVE.value): [
                self.game_state.on_request_player_move
            ],
            (GDEvents.EVENT_REQUEST_END_TURN.value): [self.game_state.on_end_turn],
            (GDEvents.EVENT_REQUEST_CURSOR_MOVE): [
                self.game_state.on_request_cursor_move
            ],
        }

        self.subscribable.subscribe(self.callbacks)

        self.broadcast(GDEvents.EVENT_GAME_STATE_READY)

    def destroy(self):
        self.unsubscribe(self.callbacks)

    def state(self):
        """
        Returns a serialized Dictionary of the game state
        """
        return Conversions.serialize_py_to_gd(self.game_state.state())

    def notify(self, signal_name, *args):
        """Receive GDScript signals"""
        print("receiving signal: ", signal_name)
        serialized_args = Conversions.serialize_gd_to_py(args)
        self.subscribable.send(signal_name, *serialized_args)

    def broadcast(self, signal_name, *args):
        """Emit signals to GDScript environment"""
        if args:
            serialized_args = [Conversions.serialize_py_to_gd(arg) for arg in args]
        else:
            serialized_args = []
        print("emitting signal: ", signal_name)
        # NOTE: signal_name.value must be called to ensure matching datatypes across GD and Python
        self.call("emit_signal", signal_name.value, *serialized_args)

# Fake Vector 3


from typing import Iterator, Any


class Comparable:
    def __eq__(self, other):
        if self.d == other.d:
            return True
        else:
            return False

    def __str__(self):
        if isinstance(self.d, tuple):
            return str(self.d)
        elif isinstance(self.d, list):
            return str([str(item) for item in self.d])
        elif isinstance(self.d, dict):
            return str({k: str(v) for k, v in self.d.items()})


class Vector3(Comparable):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        # for testing input data
        self.d = (x, y, z)

    def __iter__(self) -> Iterator[Any]:
        return self.d.__iter__()


class Array(Comparable, list):
    def __init__(self, arr):
        self.d = arr

    def __iter__(self) -> Iterator[Any]:
        return self.d.__iter__()


class Dictionary(Comparable, dict):
    def __init__(self, d):
        self.d = d

    def items(self):
        return self.d.items()


class PyBridgeNode:
    EVENT_PLAYER_MOVE_SUCCESS = "player_move_success"

    def __init__(self):
        pass

    def receive(self, action_name, *args):
        pass

    def broadcast(self, signal_name, *args):
        pass
from python.lib.board_state import BoardState


CROSS_MASK = {
    "mask": [
        [None, BoardState.FILLED_TILE, None],
        [
            BoardState.FILLED_TILE,
            BoardState.MASK_DEFAULT_PIVOT_VALUE,
            BoardState.FILLED_TILE,
        ],
        [None, BoardState.FILLED_TILE, None],
        [None, BoardState.FILLED_TILE, None],
    ],
    "shape": (3, 4),
}

SWORD_MASK = {
    "mask": [
        [None, BoardState.FILLED_TILE, None],
        [
            BoardState.FILLED_TILE,
            BoardState.MASK_DEFAULT_PIVOT_VALUE,
            BoardState.FILLED_TILE,
        ],
        [None, BoardState.FILLED_TILE, None],
    ],
    "shape": (3, 3),
}

SPEAR_MASK = {
    "mask": [
        [None, None, BoardState.FILLED_TILE, None, None],
        [None, None, BoardState.FILLED_TILE, None, None],
        [
            BoardState.FILLED_TILE,
            BoardState.FILLED_TILE,
            BoardState.MASK_DEFAULT_PIVOT_VALUE,
            BoardState.FILLED_TILE,
            BoardState.FILLED_TILE,
        ],
        [None, None, BoardState.FILLED_TILE, None, None],
        [None, None, BoardState.FILLED_TILE, None, None],
    ],
    "shape": (5, 5),
}

X_MASK = {
    "mask": [
        [BoardState.FILLED_TILE, None, None, None, BoardState.FILLED_TILE],
        [None, BoardState.FILLED_TILE, None, BoardState.FILLED_TILE, None],
        [
            None,
            None,
            BoardState.MASK_DEFAULT_PIVOT_VALUE,
            None,
            None,
        ],
        [None, BoardState.FILLED_TILE, None, BoardState.FILLED_TILE, None],
        [BoardState.FILLED_TILE, None, None, None, BoardState.FILLED_TILE],
    ],
    "shape": (5, 5),
}
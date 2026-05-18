from dataclasses import dataclass
from typing import Tuple

from constants import PLAYER_O, PLAYER_X


PlacedMove = Tuple[int, int, str]


@dataclass(frozen=True)
class SampleBoard:
    key: str
    name: str
    goal: str
    board_size: int
    ai_player: str
    moves: Tuple[PlacedMove, ...]


SAMPLE_BOARDS = (
    SampleBoard(
        key="opening",
        name="S1 Opening",
        goal="Early position: compare stable opening choices.",
        board_size=9,
        ai_player=PLAYER_O,
        moves=(
            (4, 4, PLAYER_X),
            (4, 5, PLAYER_O),
            (3, 4, PLAYER_X),
        ),
    ),
    SampleBoard(
        key="midgame",
        name="S2 Midgame",
        goal="Balanced midgame: compare attack and defense decisions.",
        board_size=9,
        ai_player=PLAYER_O,
        moves=(
            (4, 4, PLAYER_X),
            (5, 4, PLAYER_O),
            (4, 5, PLAYER_X),
            (5, 5, PLAYER_O),
            (2, 3, PLAYER_X),
            (3, 5, PLAYER_O),
            (6, 6, PLAYER_X),
        ),
    ),
    SampleBoard(
        key="ai_win_now",
        name="S3 AI Win",
        goal="AI has an immediate winning move at (4,2) or (4,6).",
        board_size=9,
        ai_player=PLAYER_O,
        moves=(
            (3, 3, PLAYER_X),
            (4, 3, PLAYER_O),
            (3, 4, PLAYER_X),
            (4, 4, PLAYER_O),
            (5, 5, PLAYER_X),
            (4, 5, PLAYER_O),
            (2, 2, PLAYER_X),
        ),
    ),
    SampleBoard(
        key="must_block",
        name="S4 Block",
        goal="Human threatens a win; depth 2+ should block at (4,6).",
        board_size=9,
        ai_player=PLAYER_O,
        moves=(
            (4, 3, PLAYER_X),
            (4, 2, PLAYER_O),
            (4, 4, PLAYER_X),
            (3, 3, PLAYER_O),
            (4, 5, PLAYER_X),
        ),
    ),
    SampleBoard(
        key="many_branches",
        name="S5 Branches",
        goal="Scattered pieces create many legal nearby moves.",
        board_size=9,
        ai_player=PLAYER_O,
        moves=(
            (1, 1, PLAYER_X),
            (1, 3, PLAYER_O),
            (2, 5, PLAYER_X),
            (3, 2, PLAYER_O),
            (4, 6, PLAYER_X),
            (5, 4, PLAYER_O),
            (6, 2, PLAYER_X),
            (7, 6, PLAYER_O),
            (7, 1, PLAYER_X),
        ),
    ),
)

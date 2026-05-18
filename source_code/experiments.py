import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from ai import AI
from board import Board
from constants import PLAYER_O, PLAYER_X


Move = Tuple[int, int]
PlacedMove = Tuple[int, int, str]


@dataclass(frozen=True)
class TestState:
    key: str
    name: str
    description: str
    board_size: int
    ai_player: str
    moves: Tuple[PlacedMove, ...]
    target_moves: Tuple[Move, ...] = ()


@dataclass
class AlgorithmResult:
    algorithm: str
    move: Optional[Move]
    score: int
    states: int
    time_ms: float
    target_hit: bool


@dataclass
class ComparisonResult:
    state: TestState
    depth: int
    legal_moves: int
    minimax: AlgorithmResult
    alpha_beta: AlgorithmResult
    same_move: bool
    states_saved: int
    states_saved_percent: float
    time_saved_ms: float
    time_saved_percent: float


DEFAULT_DEPTHS = (1, 2, 3)


TEST_STATES = (
    TestState(
        key="opening",
        name="Trang thai dau van",
        description="Ban co moi co vai nuoc quanh tam, chua co the thang ro rang.",
        board_size=7,
        ai_player=PLAYER_O,
        moves=(
            (3, 3, PLAYER_X),
            (3, 4, PLAYER_O),
            (2, 3, PLAYER_X),
        ),
    ),
    TestState(
        key="midgame",
        name="Trang thai giua van",
        description="Hai ben da co cum quan gan nhau, AI can can bang tan cong va phong thu.",
        board_size=7,
        ai_player=PLAYER_O,
        moves=(
            (3, 3, PLAYER_X),
            (4, 3, PLAYER_O),
            (3, 4, PLAYER_X),
            (4, 4, PLAYER_O),
            (1, 2, PLAYER_X),
            (2, 4, PLAYER_O),
            (5, 5, PLAYER_X),
        ),
    ),
    TestState(
        key="ai_win_now",
        name="May co the thang ngay",
        description="AI dang co 3 quan lien tiep va chi can di them mot o de ket thuc.",
        board_size=7,
        ai_player=PLAYER_O,
        moves=(
            (2, 2, PLAYER_X),
            (3, 2, PLAYER_O),
            (2, 3, PLAYER_X),
            (3, 3, PLAYER_O),
            (4, 4, PLAYER_X),
            (3, 4, PLAYER_O),
            (1, 1, PLAYER_X),
        ),
        target_moves=((3, 1), (3, 5)),
    ),
    TestState(
        key="must_block",
        name="Nguoi choi sap thang",
        description="Nguoi choi co 3 quan lien tiep, AI can chan dau mo.",
        board_size=7,
        ai_player=PLAYER_O,
        moves=(
            (3, 2, PLAYER_X),
            (3, 1, PLAYER_O),
            (3, 3, PLAYER_X),
            (2, 2, PLAYER_O),
            (3, 4, PLAYER_X),
        ),
        target_moves=((3, 5),),
    ),
    TestState(
        key="both_attack",
        name="Hai ben cung co co hoi tan cong",
        description="Ca hai ben deu co mau hinh nguy hiem, AI phai uu tien nuoc tot nhat.",
        board_size=7,
        ai_player=PLAYER_O,
        moves=(
            (3, 2, PLAYER_X),
            (5, 1, PLAYER_O),
            (3, 3, PLAYER_X),
            (5, 2, PLAYER_O),
            (1, 1, PLAYER_X),
            (5, 3, PLAYER_O),
            (4, 4, PLAYER_X),
        ),
        target_moves=((5, 0), (5, 4)),
    ),
    TestState(
        key="many_branches",
        name="Nhieu nuoc di hop le",
        description="Quan co nam rai rac, tao nhieu nhanh can xet trong vung lan can.",
        board_size=7,
        ai_player=PLAYER_O,
        moves=(
            (1, 1, PLAYER_X),
            (1, 3, PLAYER_O),
            (2, 5, PLAYER_X),
            (3, 2, PLAYER_O),
            (4, 6, PLAYER_X),
            (5, 4, PLAYER_O),
            (6, 2, PLAYER_X),
            (0, 5, PLAYER_O),
            (5, 0, PLAYER_X),
        ),
    ),
)


def build_board(state: TestState) -> Board:
    board = Board(state.board_size)
    for row, col, player in state.moves:
        if not board.make_move(row, col, player):
            raise ValueError(
                "Invalid move in test state {0}: ({1}, {2}, {3})".format(
                    state.key, row, col, player
                )
            )
    return board


def parse_depths(raw_depths: str) -> Tuple[int, ...]:
    depths = []
    for item in raw_depths.split(","):
        item = item.strip()
        if not item:
            continue
        depth = int(item)
        if depth < 1:
            raise ValueError("Depth must be >= 1")
        depths.append(depth)
    if not depths:
        raise ValueError("At least one depth is required")
    return tuple(depths)


def run_algorithm(state: TestState, depth: int, algorithm: str) -> AlgorithmResult:
    board = build_board(state)
    ai = AI(player=state.ai_player, depth=depth, algorithm=algorithm)
    move = ai.get_move(board)
    return AlgorithmResult(
        algorithm=algorithm,
        move=move,
        score=ai.last_eval,
        states=ai.last_states,
        time_ms=ai.last_time,
        target_hit=bool(state.target_moves and move in state.target_moves),
    )


def compare_state(state: TestState, depth: int) -> ComparisonResult:
    board = build_board(state)
    legal_moves = len(board.get_nearby_moves(radius=2))

    minimax = run_algorithm(state, depth, "minimax")
    alpha_beta = run_algorithm(state, depth, "alpha_beta")

    states_saved = minimax.states - alpha_beta.states
    states_saved_percent = percent(states_saved, minimax.states)
    time_saved_ms = minimax.time_ms - alpha_beta.time_ms
    time_saved_percent = percent(time_saved_ms, minimax.time_ms)

    return ComparisonResult(
        state=state,
        depth=depth,
        legal_moves=legal_moves,
        minimax=minimax,
        alpha_beta=alpha_beta,
        same_move=minimax.move == alpha_beta.move,
        states_saved=states_saved,
        states_saved_percent=states_saved_percent,
        time_saved_ms=time_saved_ms,
        time_saved_percent=time_saved_percent,
    )


def run_experiments(
    depths: Sequence[int] = DEFAULT_DEPTHS,
    states: Sequence[TestState] = TEST_STATES,
) -> List[ComparisonResult]:
    results = []
    for state in states:
        for depth in depths:
            results.append(compare_state(state, depth))
    return results


def save_results(results: Sequence[ComparisonResult], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "level3_results.csv"
    report_path = output_dir / "level3_report.md"

    write_csv(results, csv_path)
    write_report(results, report_path)
    return csv_path, report_path


def write_csv(results: Sequence[ComparisonResult], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns())
        writer.writeheader()
        for row in results:
            writer.writerow(flatten_result(row))


def csv_columns() -> List[str]:
    return [
        "state_key",
        "state_name",
        "depth",
        "legal_moves",
        "minimax_move",
        "alpha_beta_move",
        "same_move",
        "minimax_eval",
        "alpha_beta_eval",
        "minimax_states",
        "alpha_beta_states",
        "states_saved",
        "states_saved_percent",
        "minimax_time_ms",
        "alpha_beta_time_ms",
        "time_saved_ms",
        "time_saved_percent",
        "target_moves",
        "minimax_target_hit",
        "alpha_beta_target_hit",
    ]


def flatten_result(result: ComparisonResult) -> Dict[str, object]:
    return {
        "state_key": result.state.key,
        "state_name": result.state.name,
        "depth": result.depth,
        "legal_moves": result.legal_moves,
        "minimax_move": format_move(result.minimax.move),
        "alpha_beta_move": format_move(result.alpha_beta.move),
        "same_move": result.same_move,
        "minimax_eval": result.minimax.score,
        "alpha_beta_eval": result.alpha_beta.score,
        "minimax_states": result.minimax.states,
        "alpha_beta_states": result.alpha_beta.states,
        "states_saved": result.states_saved,
        "states_saved_percent": round(result.states_saved_percent, 2),
        "minimax_time_ms": round(result.minimax.time_ms, 3),
        "alpha_beta_time_ms": round(result.alpha_beta.time_ms, 3),
        "time_saved_ms": round(result.time_saved_ms, 3),
        "time_saved_percent": round(result.time_saved_percent, 2),
        "target_moves": " ".join(format_move(move) for move in result.state.target_moves),
        "minimax_target_hit": result.minimax.target_hit,
        "alpha_beta_target_hit": result.alpha_beta.target_hit,
    }


def write_report(results: Sequence[ComparisonResult], path: Path) -> None:
    by_depth = group_by_depth(results)
    by_state = group_by_state(results)

    lines = [
        "# Level 3 - Phan tich Minimax va Alpha-Beta",
        "",
        "Bao cao nay duoc tao tu `source_code/experiments.py`. Tat ca lan chay dung cung tap trang thai, cung do sau va cung ham danh gia `evaluate`.",
        "",
        "## Tap trang thai kiem thu",
        "",
    ]

    for state_key, state_results in by_state.items():
        state = state_results[0].state
        board = build_board(state)
        lines.extend(
            [
                "### {0} - {1}".format(state.key, state.name),
                "",
                state.description,
                "",
                "- AI: `{0}`".format(state.ai_player),
                "- So nuoc gan quan co can xet: `{0}`".format(
                    state_results[0].legal_moves
                ),
                "- Nuoc muc tieu: `{0}`".format(
                    " ".join(format_move(move) for move in state.target_moves)
                    if state.target_moves
                    else "Khong co"
                ),
                "",
                "```text",
            ]
        )
        lines.extend(board_to_lines(board))
        lines.extend(["```", ""])

    lines.extend(
        [
            "## Bang ket qua chi tiet",
            "",
            "| Trang thai | Depth | Minimax move | Alpha-Beta move | Cung nuoc? | Minimax states | Alpha-Beta states | Giam states | Giam % | Minimax ms | Alpha-Beta ms |",
            "|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for result in results:
        lines.append(
            "| {state} | {depth} | {mm_move} | {ab_move} | {same} | {mm_states} | {ab_states} | {saved} | {saved_pct:.2f}% | {mm_time:.3f} | {ab_time:.3f} |".format(
                state=result.state.key,
                depth=result.depth,
                mm_move=format_move(result.minimax.move),
                ab_move=format_move(result.alpha_beta.move),
                same="Co" if result.same_move else "Khong",
                mm_states=result.minimax.states,
                ab_states=result.alpha_beta.states,
                saved=result.states_saved,
                saved_pct=result.states_saved_percent,
                mm_time=result.minimax.time_ms,
                ab_time=result.alpha_beta.time_ms,
            )
        )

    lines.extend(["", "## Tong hop theo do sau", ""])
    lines.extend(depth_summary_table(by_depth))
    lines.extend(["", "## Nhan xet goi y", ""])
    lines.extend(build_analysis(results))
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def board_to_lines(board: Board) -> List[str]:
    lines = ["    " + " ".join(str(col) for col in range(board.size))]
    for row in range(board.size):
        cells = " ".join(board.grid[row][col] for col in range(board.size))
        lines.append("{0:>2}  {1}".format(row, cells))
    return lines


def depth_summary_table(by_depth: Dict[int, List[ComparisonResult]]) -> List[str]:
    lines = [
        "| Depth | Minimax states TB | Alpha-Beta states TB | Giam states TB | Giam % TB | Minimax ms TB | Alpha-Beta ms TB |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for depth in sorted(by_depth):
        rows = by_depth[depth]
        avg_mm_states = average(row.minimax.states for row in rows)
        avg_ab_states = average(row.alpha_beta.states for row in rows)
        avg_saved = average(row.states_saved for row in rows)
        avg_saved_percent = average(row.states_saved_percent for row in rows)
        avg_mm_time = average(row.minimax.time_ms for row in rows)
        avg_ab_time = average(row.alpha_beta.time_ms for row in rows)
        lines.append(
            "| {0} | {1:.1f} | {2:.1f} | {3:.1f} | {4:.2f}% | {5:.3f} | {6:.3f} |".format(
                depth,
                avg_mm_states,
                avg_ab_states,
                avg_saved,
                avg_saved_percent,
                avg_mm_time,
                avg_ab_time,
            )
        )
    return lines


def build_analysis(results: Sequence[ComparisonResult]) -> List[str]:
    same_count = sum(1 for row in results if row.same_move)
    total = len(results)
    avg_saved_percent = average(row.states_saved_percent for row in results)
    best_prune = max(results, key=lambda row: row.states_saved_percent)

    lines = [
        "- Alpha-Beta chon cung nuoc voi Minimax trong {0}/{1} lan chay.".format(
            same_count, total
        ),
        "- Trung binh Alpha-Beta giam {0:.2f}% so trang thai so voi Minimax.".format(
            avg_saved_percent
        ),
        "- Truong hop cat tia tot nhat la `{0}` o depth {1}, giam {2:.2f}% trang thai.".format(
            best_prune.state.key,
            best_prune.depth,
            best_prune.states_saved_percent,
        ),
    ]

    lines.extend(depth_growth_notes(results))
    lines.extend(depth_move_notes(results))
    lines.extend(move_quality_notes(results))
    lines.extend(evaluation_notes())
    return lines


def depth_growth_notes(results: Sequence[ComparisonResult]) -> List[str]:
    by_depth = group_by_depth(results)
    notes = []
    depths = sorted(by_depth)
    if len(depths) >= 2:
        first = depths[0]
        last = depths[-1]
        first_mm = average(row.minimax.states for row in by_depth[first])
        last_mm = average(row.minimax.states for row in by_depth[last])
        first_ab = average(row.alpha_beta.states for row in by_depth[first])
        last_ab = average(row.alpha_beta.states for row in by_depth[last])
        notes.append(
            "- Khi tang depth tu {0} len {1}, so trang thai Minimax TB tang tu {2:.1f} len {3:.1f}; Alpha-Beta tang tu {4:.1f} len {5:.1f}.".format(
                first, last, first_mm, last_mm, first_ab, last_ab
            )
        )
    return notes


def move_quality_notes(results: Sequence[ComparisonResult]) -> List[str]:
    target_rows = [row for row in results if row.state.target_moves]
    if not target_rows:
        return []

    minimax_hits = sum(1 for row in target_rows if row.minimax.target_hit)
    alpha_hits = sum(1 for row in target_rows if row.alpha_beta.target_hit)
    total = len(target_rows)
    good_cases = sorted(
        {
            row.state.key
            for row in target_rows
            if row.minimax.target_hit and row.alpha_beta.target_hit
        }
    )
    weak_cases = sorted(
        {
            "{0}/depth{1}".format(row.state.key, row.depth)
            for row in target_rows
            if not row.minimax.target_hit or not row.alpha_beta.target_hit
        }
    )

    notes = [
        "- Voi cac trang thai co nuoc muc tieu ro rang, Minimax dat {0}/{2}, Alpha-Beta dat {1}/{2}.".format(
            minimax_hits, alpha_hits, total
        ),
        "- AI choi tot o cac nhom co loi chien thuat ro rang: {0}.".format(
            ", ".join(good_cases) if good_cases else "chua co"
        ),
    ]
    if weak_cases:
        notes.append(
            "- AI chon chua hop ly tai: {0}. Day la cac ca nen dua vao phan han che khi viet bao cao.".format(
                ", ".join(weak_cases)
            )
        )
    return notes


def depth_move_notes(results: Sequence[ComparisonResult]) -> List[str]:
    notes = []
    for state_key, rows in group_by_state(results).items():
        rows = sorted(rows, key=lambda row: row.depth)
        if len(rows) < 2:
            continue
        minimax_moves = [row.minimax.move for row in rows]
        alpha_moves = [row.alpha_beta.move for row in rows]
        if len(set(minimax_moves)) > 1 or len(set(alpha_moves)) > 1:
            notes.append(
                "- Do sau lam thay doi lua chon o `{0}`: Minimax {1}, Alpha-Beta {2}.".format(
                    state_key,
                    " -> ".join(format_move(move) for move in minimax_moves),
                    " -> ".join(format_move(move) for move in alpha_moves),
                )
            )
    if not notes:
        notes.append("- Trong bo test nay, tang depth khong lam thay doi nuoc di duoc chon.")
    return notes


def evaluation_notes() -> List[str]:
    return [
        "- Ham danh gia hien tai uu tien chuoi quan lien tiep va so dau mo, nen phu hop de nhan dien nuoc thang ngay, chan doi thu va mo rong the tan cong.",
        "- Han che: ham danh gia chua phan tich cac mau hinh bi tach khe, nuoc bay phuc tap va thu tu nuoc di chua duoc sap theo do manh, nen o depth thap AI van co the chon nuoc phong thu hoac tan cong chua toi uu.",
        "- Neu cai tien tiep, nen them move ordering theo diem danh gia tam thoi, bo nho transposition table va bo mau danh gia cho cac the co bi chan mot dau, hai dau, tach mot o.",
    ]


def group_by_depth(results: Sequence[ComparisonResult]) -> Dict[int, List[ComparisonResult]]:
    grouped = {}
    for result in results:
        grouped.setdefault(result.depth, []).append(result)
    return grouped


def group_by_state(results: Sequence[ComparisonResult]) -> Dict[str, List[ComparisonResult]]:
    grouped = {}
    for result in results:
        grouped.setdefault(result.state.key, []).append(result)
    return grouped


def percent(value: float, total: float) -> float:
    if total == 0:
        return 0.0
    return value * 100.0 / total


def average(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def format_move(move: Optional[Move]) -> str:
    if move is None:
        return "-"
    return "({0},{1})".format(move[0], move[1])


def default_output_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "reports"


def run_level3_experiments(
    depths: Sequence[int] = DEFAULT_DEPTHS,
    output_dir: Optional[Path] = None,
) -> Tuple[List[ComparisonResult], Path, Path]:
    if output_dir is None:
        output_dir = default_output_dir()
    results = run_experiments(depths=depths)
    csv_path, report_path = save_results(results, output_dir)
    return results, csv_path, report_path

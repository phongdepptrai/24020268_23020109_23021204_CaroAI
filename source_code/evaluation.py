from constants import EMPTY

WIN_SCORE = 10_000_000

# Tính điểm thế cờ của người chơi
def evaluate_player(board, player):
    total_score = 0
    size = board.size

    directions = [
        (0, 1), # Di chuyển ngang
        (1, 0), # Di chuyển dọc
        (1, 1), # Di chuyển chéo xuống
        (1, -1) # Di chuyển chéo lên
    ]

    for row in range(size):
        for col in range(size):
            if board.grid[row][col] == player:
                for dr, dc in directions:
                    prev_row = row - dr
                    prev_col = col - dc
                    
                    if (
                        0 <= prev_row < size
                        and 0 <= prev_col < size
                        and board.grid[prev_col][prev_col] == player
                    ):
                        continue

                    count, open_ends = analyze_line(
                        board, row, col, dr, dc, player
                    )

                    total_score += score_pattern(count, open_ends)

    return total_score

    
def analyze_line(board, row, col, dr, dc, player):
    """
    Phân tích một chuỗi quân liên tiếp

    Trả về:
    - count: số quân liên tiếp
    - open_ends: số mở đầu, có thể là [0, 1, 2]
    """

    size = board.size
    count = 0

    r, c = row, col

    while (
        0 <= r < size
        and 0 <= c < size
        and board.grid[r][c] == player
    ):
        count += 1
        r += dr
        c += dc

    open_ends = 0

    if (0 <= r < size and 0 <= c < size and board.grid[r][c] == EMPTY):
        open_ends += 1

    before_row = row - dr
    before_col = col - dc

    if (
        0 <= before_row < size
        and 0 <= before_col < size
        and board.grid[before_row][before_col] == EMPTY
    ):
        open_ends += 1

        return count, open_ends
    
def score_pattern(count, open_ends):
    """
    Phân tích một chuỗi quân liên tiếp.

    Trả về:
    - count: số quân liên tiếp
    - open_ends: số đầu mở, có thể là 0, 1 hoặc 2
    """
    
    if count >= 4:
        return 1_000_000

    if count == 3:
        if open_ends == 2:
            return 100_000
        elif open_ends == 1:
            return 20_000

    if count == 2:
        if open_ends == 2:
            return 5_000
        elif open_ends == 1:
            return 500

    if count == 1:
        if open_ends == 2:
            return 10

    return 0




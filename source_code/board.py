import copy
from constants import EMPTY, PLAYER_X, PLAYER_O, WIN_LENGTH


class Board:
    def __init__(self, size=15):
        self.size = size
        self.grid = [[EMPTY] * size for _ in range(size)]
        self.move_history = []
        self.move_count = 0

    def make_move(self, row, col, player):
        if not self.is_valid_move(row, col):
            return False
        self.grid[row][col] = player
        self.move_history.append((row, col, player))
        self.move_count += 1
        return True

    def undo_move(self, row, col):
        if self.grid[row][col] == EMPTY:
            return False
        self.grid[row][col] = EMPTY
        if self.move_history and self.move_history[-1][:2] == (row, col):
            self.move_history.pop()
        self.move_count -= 1
        return True

    def is_valid_move(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] == EMPTY

    def check_winner(self, row, col):
        player = self.grid[row][col]
        if player == EMPTY:
            return None

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            count = 1
            win_cells = [(row, col)]

            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == player:
                count += 1
                win_cells.append((r, c))
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == player:
                count += 1
                win_cells.append((r, c))
                r -= dr
                c -= dc

            if count >= WIN_LENGTH:
                return player, win_cells

        return None

    def is_full(self):
        for row in self.grid:
            for cell in row:
                if cell == EMPTY:
                    return False
        return True

    def get_valid_moves(self):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == EMPTY:
                    moves.append((r, c))
        return moves

    def get_nearby_moves(self, radius=2):
        if self.move_count == 0:
            center = self.size // 2
            return [(center, center)]

        occupied = set()
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != EMPTY:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr][nc] == EMPTY:
                                occupied.add((nr, nc))

        return list(occupied) if occupied else self.get_valid_moves()

    def copy(self):
        new_board = Board(self.size)
        new_board.grid = [row[:] for row in self.grid]
        new_board.move_history = self.move_history[:]
        new_board.move_count = self.move_count
        return new_board

    def set_state(self, state):
        self.size = len(state)
        self.grid = [row[:] for row in state]
        self.move_count = sum(1 for r in state for c in r if c != EMPTY)
        self.move_history = []

    def get_state(self):
        return [row[:] for row in self.grid]

    def get_last_move(self):
        if self.move_history:
            return self.move_history[-1][:2]
        return None

    def display(self):
        header = "   " + "  ".join(f"{c:2}" for c in range(self.size))
        print(header)
        for r in range(self.size):
            row_str = f"{r:2} " + "  ".join(f" {self.grid[r][c]}" for c in range(self.size))
            print(row_str)
        print()

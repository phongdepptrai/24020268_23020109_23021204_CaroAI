import random
import time
from constants import PLAYER_X, PLAYER_O, EMPTY
from evaluation import evaluate, evaluate_player

class AI:
    def __init__(self, player=PLAYER_O, depth=3, algorithm='alpha_beta'):
        self.player = player
        self.opponent = PLAYER_X if player == PLAYER_O else PLAYER_O
        self.depth = depth
        self.algorithm = algorithm
        self.last_move = None
        self.last_eval = 0
        self.last_states = 0
        self.last_time = 0

    def get_move(self, board):
        start_time = time.time()
        self.last_states = 0

        if board.move_count == 0:
            center = board.size // 2
            self.last_move = (center, center)
            self.last_eval = 0
            self.last_time = (time.time() - start_time) * 1000
            return self.last_move

        moves = board.get_nearby_moves(radius=2)
        if not moves:
            moves = board.get_valid_moves()

        # PLACEHOLDER: Random move
        # TODO: Thay thế bằng Minimax hoặc Alpha-Beta dựa trên self.algorithm
        # if self.algorithm == 'minimax':
        #     best_move = self._minimax_root(board)
        # elif self.algorithm == 'alpha_beta':
        #     best_move = self._alpha_beta_root(board)
        best_move = random.choice(moves)

        self.last_move = best_move
        self.last_eval = evaluate(board, self.player, self.opponent)
        self.last_states = 0
        self.last_time = (time.time() - start_time) * 1000
        return best_move

    # PLACEHOLDER: Các thuật toán sẽ được thêm sau
    # -------------------------------------------------------
    # def _minimax_root(self, board):
    #     """Minimax - Tìm nước đi tốt nhất"""
    #     pass
    #
    # def _minimax(self, board, depth, maximizing):
    #     """Minimax đệ quy"""
    #     pass
    #
    # def _alpha_beta_root(self, board):
    #     """Alpha-Beta - Tìm nước đi tốt nhất với cắt nhánh"""
    #     pass
    #
    # def _alpha_beta(self, board, depth, alpha, beta, maximizing):
    #     """Alpha-Beta đệ quy"""
    #     pass
    #
    # def evaluate(self, board):
    #     """Hàm đánh giá heuristic"""
    #     pass
    # -------------------------------------------------------

    def print_evaluation(self, board):
        ai_score = evaluate_player(board, self.player)
        player_score = evaluate_player(board, self.opponent)

        print("===== EVALUATION =====")
        print(f"AI ({self.player}) score: {ai_score}")
        print(f"Player ({self.opponent}) score: {player_score}")
        print("======================")

    
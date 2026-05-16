import random
import time
from constants import PLAYER_X, PLAYER_O, EMPTY
from evaluation import evaluate, evaluate_player


class AI:
    def __init__(self, player=PLAYER_O, depth=3, algorithm='minimax'):
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

        if self.algorithm == 'minimax':
            best_move = self._minimax_root(board)
        elif self.algorithm == 'alpha_beta':
            best_move = self._alpha_beta_root(board)
        else:
            moves = board.get_nearby_moves(radius=2)
            if not moves:
                moves = board.get_valid_moves()
            best_move = random.choice(moves)

        self.last_move = best_move
        self.last_time = (time.time() - start_time) * 1000
        return best_move

    def _minimax_root(self, board):
        best_score = float('-inf')
        best_move = None
        moves = board.get_nearby_moves(radius=2)
        if not moves:
            moves = board.get_valid_moves()

        for r, c in moves:
            board.make_move(r, c, self.player)
            score = self._minimax(board, self.depth - 1, False)
            board.undo_move(r, c)

            if score > best_score:
                best_score = score
                best_move = (r, c)

        self.last_eval = best_score
        return best_move if best_move else random.choice(moves)

    def _minimax(self, board, depth, maximizing):
        self.last_states += 1

        last = board.move_history[-1] if board.move_history else None
        if last:
            result = board.check_winner(last[0], last[1])
            if result:
                winner = result[0]
                if winner == self.player:
                    return 10000000
                else:
                    return -10000000

        if board.is_full():
            return 0

        if depth == 0:
            return evaluate(board, self.player, self.opponent)

        moves = board.get_nearby_moves(radius=2)
        if not moves:
            moves = board.get_valid_moves()

        if maximizing:
            max_eval = float('-inf')
            for r, c in moves:
                board.make_move(r, c, self.player)
                eval_score = self._minimax(board, depth - 1, False)
                board.undo_move(r, c)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in moves:
                board.make_move(r, c, self.opponent)
                eval_score = self._minimax(board, depth - 1, True)
                board.undo_move(r, c)
                min_eval = min(min_eval, eval_score)
            return min_eval

    def _alpha_beta_root(self, board):
        # PLACEHOLDER: Alpha-Beta se them sau
        return self._minimax_root(board)

    def print_evaluation(self, board):
        ai_score = evaluate_player(board, self.player)
        player_score = evaluate_player(board, self.opponent)

        print("===== EVALUATION =====")
        print(f"AI ({self.player}) score: {ai_score}")
        print(f"Player ({self.opponent}) score: {player_score}")
        print("======================")

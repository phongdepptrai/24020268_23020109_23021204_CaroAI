import pygame
from constants import PLAYER_X, PLAYER_O, DEFAULT_DEPTH
from board import Board
from ai import AI
from gui import GUI
from evaluation import evaluate
from sample_boards import SAMPLE_BOARDS

class Game:
    def __init__(self):
        self.gui = GUI()
        self.state = 'menu'
        self.board_size = 15
        self.mode = None
        self.first_player = 'human'
        self.human_player = PLAYER_X
        self.ai_player = PLAYER_O
        self.ai_algorithm = 'alpha_beta'
        self.ai_depth = DEFAULT_DEPTH
        self.board = None
        self.ai = None
        self.current_player = PLAYER_X
        self.game_over = False
        self.winner = None
        self.win_cells = []
        self.waiting_ai = False
        self.loaded_sample_index = None

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            if self.state == 'menu':
                running = self._run_menu()
            elif self.state == 'playing':
                running = self._run_game()

            clock.tick(60)

        self.gui.quit()

    def _run_menu(self):
        buttons, depth_buttons, btn_pvp, btn_pve, btn_human_first, btn_ai_first = self.gui.draw_menu(
            self.first_player,
            self.ai_depth,
            self.board_size
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.gui.toggle_fullscreen()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self.gui.handle_menu_click(
                    event.pos, buttons, depth_buttons, btn_pvp, btn_pve,
                    btn_human_first, btn_ai_first
                )
                if result:
                    action, value = result
                    if action == 'size':
                        self.board_size = value
                    elif action == 'depth':
                        self.ai_depth = value
                    elif action == 'first_player':
                        self.first_player = value
                    elif action == 'mode':
                        self.mode = value
                        self._start_game()
                        self.state = 'playing'

        return True

    def _start_game(self):
        self.board = Board(self.board_size)
        self.current_player = PLAYER_X
        self.human_player = PLAYER_X
        self.ai_player = PLAYER_O
        self.game_over = False
        self.winner = None
        self.win_cells = []
        self.waiting_ai = False

        if self.mode == 'pve':
            if self.first_player == 'ai':
                self.ai_player = PLAYER_X
                self.human_player = PLAYER_O
            self.current_player = PLAYER_X
            self.ai = AI(player=self.ai_player, depth=self.ai_depth, algorithm=self.ai_algorithm)
        else:
            self.ai = None

        self.gui.update_board_size(self.board_size)
        self.gui.set_depth(self.ai_depth)
        self.gui.set_algorithm(self.ai_algorithm)
        self.gui.clear_ai_log()
        self.gui.set_win_cells([])
        self.gui.set_last_move(None)
        self.gui.set_loaded_sample(None, "")
        self.loaded_sample_index = None

    def _run_game(self):
        mouse_pos = pygame.mouse.get_pos()
        self.gui.update_button_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.gui.toggle_fullscreen()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

        if (
            not self.game_over
            and self.mode == 'pve'
            and self.current_player == self.ai_player
            and not self.waiting_ai
        ):
            self.waiting_ai = True
            self._ai_move()
            self.waiting_ai = False

        self.gui.draw_board(self.board, self.current_player,
                            self.ai.player if self.ai else None)

        return True

    def _handle_click(self, pos):
        btn_result = self.gui.check_button_click(pos)
        if btn_result:
            action, value = btn_result
            if action == 'depth':
                self.ai_depth = max(1, min(5, self.ai_depth + value))
                self.gui.set_depth(self.ai_depth)
                if self.ai:
                    self.ai.depth = self.ai_depth
                return
            if action == 'set_depth':
                self.ai_depth = value
                self.gui.set_depth(self.ai_depth)
                if self.ai:
                    self.ai.depth = self.ai_depth
                return
            elif action == 'switch_ai':
                self.ai_algorithm = 'minimax' if self.ai_algorithm == 'alpha_beta' else 'alpha_beta'
                self.gui.set_algorithm(self.ai_algorithm)
                if self.ai:
                    self.ai.algorithm = self.ai_algorithm
                return
            elif action == 'restart':
                self._start_game()
                return
            elif action == 'menu':
                self.state = 'menu'
                return
            elif action == 'ai_move':
                self._manual_ai_move()
                return
            elif action == 'sample':
                self._load_sample_board(value)
                return

        if self.game_over:
            return

        if self.mode == 'pve' and self.current_player == self.ai_player:
            return

        grid_pos = self.gui._pixel_to_grid(*pos)
        if grid_pos is None:
            return

        row, col = grid_pos
        if not self.board.is_valid_move(row, col):
            return

        self.board.make_move(row, col, self.current_player)
        self.gui.set_last_move((row, col))

        result = self.board.check_winner(row, col)
        if result:
            self.winner, self.win_cells = result
            self.game_over = True
            self.gui.set_win_cells(self.win_cells)
            self.gui.show_message(f"{self.winner} wins!")
            return

        if self.board.is_full():
            self.game_over = True
            self.gui.show_message("Draw!")
            return

        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

    def _ai_move(self):
        move = self.ai.get_move(self.board)
        if move is None:
            return

        row, col = move
        self.board.make_move(row, col, self.ai_player)
        self.gui.set_last_move((row, col))
        self.ai.print_evaluation(self.board)

        log = f"Move:({row},{col}) Eval:{self.ai.last_eval} States:{self.ai.last_states} Time:{self.ai.last_time:.1f}ms"
        self.gui.add_ai_log(log)

        result = self.board.check_winner(row, col)
        if result:
            self.winner, self.win_cells = result
            self.game_over = True
            self.gui.set_win_cells(self.win_cells)
            self.gui.show_message(f"{self.winner} wins!")
            return

        if self.board.is_full():
            self.game_over = True
            self.gui.show_message("Draw!")
            return

        self.current_player = self.human_player

    def _manual_ai_move(self):
        if self.mode != 'pve' or self.ai is None or self.game_over:
            return
        if self.current_player != self.ai_player:
            return

        self.waiting_ai = False
        self._ai_move()

    def _load_sample_board(self, index):
        if not 0 <= index < len(SAMPLE_BOARDS):
            return

        sample = SAMPLE_BOARDS[index]
        self.mode = 'pve'
        self.board_size = sample.board_size
        self.board = Board(sample.board_size)

        for row, col, player in sample.moves:
            if not self.board.make_move(row, col, player):
                raise ValueError(
                    f"Invalid sample move: {sample.key} ({row}, {col}, {player})"
                )

        self.ai_player = sample.ai_player
        self.human_player = PLAYER_X if self.ai_player == PLAYER_O else PLAYER_O
        self.current_player = self.ai_player
        self.game_over = False
        self.winner = None
        self.win_cells = []
        self.loaded_sample_index = index

        self.ai = AI(
            player=self.ai_player,
            depth=self.ai_depth,
            algorithm=self.ai_algorithm,
        )

        self.gui.update_board_size(self.board_size)
        self.gui.set_depth(self.ai_depth)
        self.gui.set_algorithm(self.ai_algorithm)
        self.gui.set_win_cells([])
        self.gui.set_last_move(None)
        self.gui.set_loaded_sample(index, sample.name)
        self.gui.clear_ai_log()
        self.gui.add_ai_log(f"Loaded {sample.name}")
        self.gui.add_ai_log(sample.goal)
        self.gui.add_ai_log("Choose depth/AI, then click AI Move.")

        self.waiting_ai = True

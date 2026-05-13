import pygame
from constants import (
    CELL_SIZE, BOARD_MARGIN, SIDEBAR_WIDTH,
    BG_COLOR, GRID_COLOR, CELL_BG, X_COLOR, O_COLOR,
    TEXT_COLOR, HIGHLIGHT_COLOR, BUTTON_COLOR, BUTTON_HOVER,
    BUTTON_TEXT, WIN_LINE_COLOR, LAST_MOVE_COLOR, EMPTY,
    PLAYER_X, PLAYER_O, BOARD_SIZES
)


class Button:
    def __init__(self, x, y, w, h, text, font_size=20, selected=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font_size = font_size
        self.selected = selected
        self.hovered = False

    def draw(self, surface, font):
        color = HIGHLIGHT_COLOR if self.selected else BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, GRID_COLOR, self.rect, 2, border_radius=6)
        text_color = BG_COLOR if self.selected else BUTTON_TEXT
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class GUI:
    def __init__(self, board_size=15):
        pygame.init()
        self.board_size = board_size
        self.cell_size = CELL_SIZE
        self.margin = BOARD_MARGIN
        self.sidebar_w = SIDEBAR_WIDTH
        self.fullscreen = False

        board_px = self.margin * 2 + self.cell_size * board_size
        self.win_w = board_px + self.sidebar_w
        self.win_h = board_px

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        pygame.display.set_caption("Caro AI")

        self.font_sm = pygame.font.SysFont("consolas", 16)
        self.font_md = pygame.font.SysFont("consolas", 20)
        self.font_lg = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_xl = pygame.font.SysFont("consolas", 40, bold=True)

        self._create_buttons()
        self.win_cells = []
        self.last_move = None
        self.message = ""
        self.ai_log = []

    def _create_buttons(self):
        bx = self.margin + self.cell_size * self.board_size + 20
        bw = SIDEBAR_WIDTH - 40
        y = 200

        self.btn_depth_minus = Button(bx, y, 40, 35, "-")
        self.btn_depth_plus = Button(bx + 50, y, 40, 35, "+")
        y += 50
        self.btn_switch_ai = Button(bx, y, bw, 35, "AI: Alpha-Beta")
        y += 50
        self.btn_restart = Button(bx, y, bw, 35, "Restart")
        y += 50
        self.btn_menu = Button(bx, y, bw, 35, "Menu")

    def update_board_size(self, size):
        self.board_size = size
        board_px = self.margin * 2 + self.cell_size * size
        self.win_w = board_px + self.sidebar_w
        self.win_h = board_px
        if not self.fullscreen:
            self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        self._create_buttons()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        self._recalc_layout()

    def _grid_to_pixel(self, row, col):
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        return x, y

    def _pixel_to_grid(self, mx, my):
        col = (mx - self.margin) // self.cell_size
        row = (my - self.margin) // self.cell_size
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return row, col
        return None

    def _recalc_layout(self):
        screen_w, screen_h = self.screen.get_size()
        board_area_w = screen_w - self.sidebar_w - self.margin * 2
        board_area_h = screen_h - self.margin * 2
        max_cell = min(board_area_w // self.board_size, board_area_h // self.board_size)
        self.cell_size = max(20, min(60, max_cell))
        self._create_buttons()

    def draw_board(self, board, current_player, ai_player=None):
        self.screen.fill(BG_COLOR)
        self._draw_grid()
        self._draw_pieces(board)
        self._draw_last_move()
        self._draw_win_line()
        self._draw_sidebar(current_player, ai_player, board)
        pygame.display.flip()

    def _draw_grid(self):
        for i in range(self.board_size + 1):
            x = self.margin + i * self.cell_size
            y = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, GRID_COLOR,
                             (x, self.margin),
                             (x, self.margin + self.board_size * self.cell_size), 1)
            pygame.draw.line(self.screen, GRID_COLOR,
                             (self.margin, y),
                             (self.margin + self.board_size * self.cell_size, y), 1)

    def _draw_pieces(self, board):
        for r in range(board.size):
            for c in range(board.size):
                if board.grid[r][c] != EMPTY:
                    cx, cy = self._grid_to_pixel(r, c)
                    cx += self.cell_size // 2
                    cy += self.cell_size // 2
                    radius = self.cell_size // 2 - 6

                    if board.grid[r][c] == PLAYER_X:
                        offset = radius - 2
                        pygame.draw.line(self.screen, X_COLOR,
                                         (cx - offset, cy - offset),
                                         (cx + offset, cy + offset), 3)
                        pygame.draw.line(self.screen, X_COLOR,
                                         (cx - offset, cy + offset),
                                         (cx + offset, cy - offset), 3)
                    else:
                        pygame.draw.circle(self.screen, O_COLOR, (cx, cy), radius, 3)

    def _draw_last_move(self):
        if self.last_move:
            r, c = self.last_move
            cx, cy = self._grid_to_pixel(r, c)
            cx += self.cell_size // 2
            cy += self.cell_size // 2
            pygame.draw.circle(self.screen, LAST_MOVE_COLOR, (cx, cy), 4)

    def _draw_win_line(self):
        if self.win_cells and len(self.win_cells) >= 2:
            r1, c1 = self.win_cells[0]
            r2, c2 = self.win_cells[-1]
            x1, y1 = self._grid_to_pixel(r1, c1)
            x2, y2 = self._grid_to_pixel(r2, c2)
            x1 += self.cell_size // 2
            y1 += self.cell_size // 2
            x2 += self.cell_size // 2
            y2 += self.cell_size // 2
            pygame.draw.line(self.screen, WIN_LINE_COLOR, (x1, y1), (x2, y2), 4)

    def _draw_sidebar(self, current_player, ai_player, board):
        bx = self.margin + self.cell_size * self.board_size + 20
        bw = SIDEBAR_WIDTH - 40

        title = self.font_lg.render("CARO AI", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (bx, 20))

        mode_text = "PvP" if ai_player is None else "PvE"
        mode_surf = self.font_md.render(f"Mode: {mode_text}", True, TEXT_COLOR)
        self.screen.blit(mode_surf, (bx, 60))

        turn_color = X_COLOR if current_player == PLAYER_X else O_COLOR
        turn_text = f"Turn: {current_player}"
        turn_surf = self.font_md.render(turn_text, True, turn_color)
        self.screen.blit(turn_surf, (bx, 90))

        size_surf = self.font_md.render(f"Board: {board.size}x{board.size}", True, TEXT_COLOR)
        self.screen.blit(size_surf, (bx, 120))

        if ai_player is not None:
            human_player = PLAYER_X if ai_player == PLAYER_O else PLAYER_O
            roles_surf = self.font_sm.render(
                f"You: {human_player}   AI: {ai_player}", True, TEXT_COLOR
            )
            self.screen.blit(roles_surf, (bx, 145))

        ai_algo = getattr(self, '_ai_algorithm', 'alpha_beta')
        algo_label = self.font_sm.render(f"AI: {ai_algo}", True, TEXT_COLOR)
        self.screen.blit(algo_label, (bx, 170))

        y = 200
        depth = getattr(self, '_current_depth', 3)
        depth_label = self.font_md.render(f"Depth: {depth}", True, TEXT_COLOR)
        self.screen.blit(depth_label, (bx + 100, y + 5))
        self.btn_depth_minus.draw(self.screen, self.font_md)
        self.btn_depth_plus.draw(self.screen, self.font_md)

        self.btn_switch_ai.draw(self.screen, self.font_md)
        self.btn_restart.draw(self.screen, self.font_md)
        self.btn_menu.draw(self.screen, self.font_md)

        self._draw_ai_log(bx, 350, bw)

    def _draw_ai_log(self, x, y, w):
        header = self.font_sm.render("AI Log:", True, HIGHLIGHT_COLOR)
        self.screen.blit(header, (x, y))
        y += 25

        for i, log in enumerate(self.ai_log[-8:]):
            surf = self.font_sm.render(log, True, TEXT_COLOR)
            self.screen.blit(surf, (x, y + i * 20))

    def show_message(self, msg, duration_ms=2000):
        self.message = msg

    def draw_menu(self, first_player='human'):
        self.screen.fill(BG_COLOR)

        title = self.font_xl.render("CARO AI", True, HIGHLIGHT_COLOR)
        title_rect = title.get_rect(center=(self.win_w // 2, 60))
        self.screen.blit(title, title_rect)

        subtitle = self.font_md.render("Choose board size:", True, TEXT_COLOR)
        sub_rect = subtitle.get_rect(center=(self.win_w // 2, 130))
        self.screen.blit(subtitle, sub_rect)

        buttons = []
        for i, size in enumerate(BOARD_SIZES):
            btn = Button(self.win_w // 2 - 80, 170 + i * 60, 160, 40, f"{size}x{size}")
            btn.draw(self.screen, self.font_md)
            buttons.append(btn)

        first_label = self.font_md.render("First Move (PvE):", True, TEXT_COLOR)
        first_rect = first_label.get_rect(center=(self.win_w // 2, 360))
        self.screen.blit(first_label, first_rect)

        btn_human_first = Button(
            self.win_w // 2 - 170, 395, 150, 40, "Human First",
            selected=first_player == 'human'
        )
        btn_ai_first = Button(
            self.win_w // 2 + 20, 395, 150, 40, "AI First",
            selected=first_player == 'ai'
        )
        btn_human_first.draw(self.screen, self.font_md)
        btn_ai_first.draw(self.screen, self.font_md)

        mode_label = self.font_md.render("Game Mode:", True, TEXT_COLOR)
        mode_rect = mode_label.get_rect(center=(self.win_w // 2, 465))
        self.screen.blit(mode_label, mode_rect)

        btn_pvp = Button(self.win_w // 2 - 170, 500, 150, 40, "PvP (2 Players)")
        btn_pve = Button(self.win_w // 2 + 20, 500, 150, 40, "PvE (vs AI)")
        btn_pvp.draw(self.screen, self.font_md)
        btn_pve.draw(self.screen, self.font_md)

        hint = self.font_sm.render("F11: Toggle Fullscreen", True, GRID_COLOR)
        hint_rect = hint.get_rect(center=(self.win_w // 2, self.win_h - 30))
        self.screen.blit(hint, hint_rect)

        pygame.display.flip()
        return buttons, btn_pvp, btn_pve, btn_human_first, btn_ai_first

    def handle_menu_click(self, pos, buttons, btn_pvp, btn_pve, btn_human_first, btn_ai_first):
        for i, btn in enumerate(buttons):
            if btn.is_clicked(pos):
                return ('size', BOARD_SIZES[i])
        if btn_human_first.is_clicked(pos):
            return ('first_player', 'human')
        if btn_ai_first.is_clicked(pos):
            return ('first_player', 'ai')
        if btn_pvp.is_clicked(pos):
            return ('mode', 'pvp')
        if btn_pve.is_clicked(pos):
            return ('mode', 'pve')
        return None

    def update_button_hover(self, mouse_pos):
        self.btn_depth_minus.update(mouse_pos)
        self.btn_depth_plus.update(mouse_pos)
        self.btn_switch_ai.update(mouse_pos)
        self.btn_restart.update(mouse_pos)
        self.btn_menu.update(mouse_pos)

    def check_button_click(self, pos):
        if self.btn_depth_minus.is_clicked(pos):
            return ('depth', -1)
        if self.btn_depth_plus.is_clicked(pos):
            return ('depth', 1)
        if self.btn_switch_ai.is_clicked(pos):
            return ('switch_ai', None)
        if self.btn_restart.is_clicked(pos):
            return ('restart', None)
        if self.btn_menu.is_clicked(pos):
            return ('menu', None)
        return None

    def set_win_cells(self, cells):
        self.win_cells = cells if cells else []

    def set_last_move(self, move):
        self.last_move = move

    def set_depth(self, depth):
        self._current_depth = depth

    def set_algorithm(self, algorithm):
        self._ai_algorithm = algorithm

    def add_ai_log(self, log_str):
        self.ai_log.append(log_str)
        if len(self.ai_log) > 50:
            self.ai_log = self.ai_log[-50:]

    def clear_ai_log(self):
        self.ai_log = []

    def quit(self):
        pygame.quit()

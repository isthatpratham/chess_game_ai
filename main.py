import pygame
import sys
from chess_engine import ChessGame
from ai import ChessAI
from constants import *

class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game = ChessGame()
        self.selected = None
        self.valid_moves = []
        self.running = True
        self.promotion_active = False
        
        # UI elements
        self.board_rect = pygame.Rect(20, 20, BOARD_SIZE, BOARD_SIZE)  # Fixed position
        self.side_panel_rect = pygame.Rect(BOARD_SIZE + 40, 20, WIDTH - BOARD_SIZE - 60, BOARD_SIZE)
        
        # Game mode selection
        self.game_mode = "human_vs_human"
        self.ai_difficulty = "medium"
        self.show_menu = True
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.show_menu:
                self.handle_menu_events(event)
            elif self.promotion_active:
                self.handle_promotion_events(event)
            else:
                self.handle_game_events(event)
    
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def draw_ui(self):
        # Side panel background
        pygame.draw.rect(self.screen, (240, 240, 240), self.side_panel_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.side_panel_rect, 2)
        
        # Game status
        status_text = FONT_MEDIUM.render(self.game.game_status, True, TEXT_COLOR)
        self.screen.blit(status_text, (
            self.side_panel_rect.left + 10,
            self.side_panel_rect.top + 20
        ))
        
        # Player times
        white_time = self.game.format_time(self.game.white_time)
        black_time = self.game.format_time(self.game.black_time)
        
        white_text = FONT_MEDIUM.render(f"White: {white_time}", True, TEXT_COLOR)
        black_text = FONT_MEDIUM.render(f"Black: {black_time}", True, TEXT_COLOR)
        
        self.screen.blit(white_text, (
            self.side_panel_rect.left + 10,
            self.side_panel_rect.top + 60
        ))
        self.screen.blit(black_text, (
            self.side_panel_rect.left + 10,
            self.side_panel_rect.top + 100
        ))
        
        # Move history
        history_title = FONT_SMALL.render("Move History:", True, TEXT_COLOR)
        self.screen.blit(history_title, (
            self.side_panel_rect.left + 10,
            self.side_panel_rect.top + 150
        ))
        
        for i, move in enumerate(self.game.move_history[-10:]):  # Show last 10 moves
            move_text = FONT_SMALL.render(move, True, TEXT_COLOR)
            self.screen.blit(move_text, (
                self.side_panel_rect.left + 10,
                self.side_panel_rect.top + 180 + i * 25
            ))
        
        # Controls hint
        controls = FONT_SMALL.render("ESC: Menu", True, TEXT_COLOR)
        self.screen.blit(controls, (
            self.side_panel_rect.left + 10,
            self.side_panel_rect.bottom - 40
        ))
        
        controls = FONT_SMALL.render("Ctrl+Z: Undo", True, TEXT_COLOR)
        self.screen.blit(controls, (
            self.side_panel_rect.left + 10,
            self.side_panel_rect.bottom - 20
        ))

    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check game mode buttons
            mode_button_height = 50
            for i, mode in enumerate(GAME_MODES.keys()):
                button_rect = pygame.Rect(
                    WIDTH//2 - 150, 
                    200 + i * (mode_button_height + 10), 
                    300, 
                    mode_button_height
                )
                if button_rect.collidepoint(mouse_pos):
                    self.game_mode = mode
            
            # Check difficulty buttons (only for AI modes)
            if self.game_mode != "human_vs_human":
                diff_button_height = 40
                for i, diff in enumerate(AI_DIFFICULTIES.keys()):
                    button_rect = pygame.Rect(
                        WIDTH//2 - 120, 
                        350 + i * (diff_button_height + 5), 
                        240, 
                        diff_button_height
                    )
                    if button_rect.collidepoint(mouse_pos):
                        self.ai_difficulty = diff
            
            # Start game button
            start_button = pygame.Rect(WIDTH//2 - 100, 500, 200, 50)
            if start_button.collidepoint(mouse_pos):
                self.game = ChessGame(self.game_mode, self.ai_difficulty)
                self.show_menu = False
    
    def handle_promotion_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            promotion_pieces = ['q', 'r', 'b', 'n']
            
            # Calculate promotion menu position
            col = self.game.promotion_choice[1][1]
            promotion_x = self.board_rect.left + col * SQUARE_SIZE
            promotion_y = self.board_rect.top if self.game.white_to_move else self.board_rect.top + 3 * SQUARE_SIZE
            
            for i, piece in enumerate(promotion_pieces):
                piece_rect = pygame.Rect(
                    promotion_x,
                    promotion_y + i * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                )
                
                if piece_rect.collidepoint(mouse_pos):
                    self.game.move_piece(
                        self.game.promotion_choice[0],
                        self.game.promotion_choice[1],
                        piece
                    )
                    self.promotion_active = False
                    self.selected = None
                    self.valid_moves = []
                    
                    # AI move if needed
                    if ((self.game_mode == "human_vs_ai" and not self.game.white_to_move) or 
                        (self.game_mode == "ai_vs_ai")):
                        self.game.make_ai_move()
    
    def handle_game_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.board_rect.collidepoint(event.pos):
                board_pos = (
                    (event.pos[1] - self.board_rect.top) // SQUARE_SIZE,
                    (event.pos[0] - self.board_rect.left) // SQUARE_SIZE
                )
                
                # If a piece is already selected
                if self.selected:
                    # Check if clicking on same piece (deselect)
                    if board_pos == self.selected:
                        self.selected = None
                        self.valid_moves = []
                    # Check if clicking on valid move
                    elif board_pos in [move[:2] for move in self.valid_moves]:
                        move_result = self.game.move_piece(self.selected, board_pos)
                        if move_result == "promotion":
                            self.promotion_active = True
                        else:
                            self.selected = None
                            self.valid_moves = []
                            
                            # AI move if needed
                            if ((self.game_mode == "human_vs_ai" and not self.game.white_to_move) or 
                                (self.game_mode == "ai_vs_ai")):
                                self.game.make_ai_move()
                    # Select a new piece
                    else:
                        piece = self.game.board[board_pos[0]][board_pos[1]]
                        if piece != "--" and piece[0] == ('w' if self.game.white_to_move else 'b'):
                            self.selected = board_pos
                            self.valid_moves = self.game.get_valid_moves(board_pos)
                # Select a piece
                else:
                    piece = self.game.board[board_pos[0]][board_pos[1]]
                    if piece != "--" and piece[0] == ('w' if self.game.white_to_move else 'b'):
                        self.selected = board_pos
                        self.valid_moves = self.game.get_valid_moves(board_pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.game.undo_move()
                self.selected = None
                self.valid_moves = []
            elif event.key == pygame.K_ESCAPE:
                self.show_menu = True
    
    def update(self):
        if not self.show_menu and not self.promotion_active:
            # Handle AI moves
            if ((self.game_mode == "human_vs_ai" and not self.game.white_to_move) or 
                (self.game_mode == "ai_vs_ai" and not self.game.promotion_choice)):
                self.game.make_ai_move()
            
            # Update animation
            self.game.update_animation()
            
            # Update game timers
            if not self.game.checkmate and not self.game.stalemate:
                self.game.update_timers()
    
    def draw(self):
        self.screen.fill(UI_BG)
        
        if self.show_menu:
            self.draw_menu()
        else:
            self.draw_board()
            self.draw_pieces()
            self.draw_highlights()
            self.draw_ui()
            
            if self.promotion_active:
                self.draw_promotion_menu()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Title
        title = FONT_LARGE.render("Chess Game", True, TEXT_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Game mode selection
        mode_title = FONT_MEDIUM.render("Select Game Mode:", True, TEXT_COLOR)
        self.screen.blit(mode_title, (WIDTH//2 - mode_title.get_width()//2, 160))
        
        mode_button_height = 50
        for i, (mode, name) in enumerate(GAME_MODES.items()):
            color = (200, 200, 255) if mode == self.game_mode else (230, 230, 230)
            button_rect = pygame.Rect(
                WIDTH//2 - 150, 
                200 + i * (mode_button_height + 10), 
                300, 
                mode_button_height
            )
            pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (150, 150, 150), button_rect, 2, border_radius=5)
            
            text = FONT_MEDIUM.render(name, True, TEXT_COLOR)
            self.screen.blit(text, (
                button_rect.centerx - text.get_width()//2,
                button_rect.centery - text.get_height()//2
            ))
        
        # Difficulty selection (only for AI modes)
        if self.game_mode != "human_vs_human":
            diff_title = FONT_MEDIUM.render("Select AI Difficulty:", True, TEXT_COLOR)
            self.screen.blit(diff_title, (WIDTH//2 - diff_title.get_width()//2, 310))
            
            diff_button_height = 40
            for i, (diff, info) in enumerate(AI_DIFFICULTIES.items()):
                color = (200, 200, 255) if diff == self.ai_difficulty else (230, 230, 230)
                button_rect = pygame.Rect(
                    WIDTH//2 - 120, 
                    350 + i * (diff_button_height + 5), 
                    240, 
                    diff_button_height
                )
                pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
                pygame.draw.rect(self.screen, (150, 150, 150), button_rect, 2, border_radius=5)
                
                text = FONT_SMALL.render(info["name"], True, TEXT_COLOR)
                self.screen.blit(text, (
                    button_rect.centerx - text.get_width()//2,
                    button_rect.centery - text.get_height()//2
                ))
        
        # Start game button
        start_button = pygame.Rect(WIDTH//2 - 100, 500, 200, 50)
        pygame.draw.rect(self.screen, (150, 255, 150), start_button, border_radius=5)
        pygame.draw.rect(self.screen, (0, 100, 0), start_button, 2, border_radius=5)
        
        start_text = FONT_MEDIUM.render("Start Game", True, TEXT_COLOR)
        self.screen.blit(start_text, (
            start_button.centerx - start_text.get_width()//2,
            start_button.centery - start_text.get_height()//2
        ))
    
    def draw_board(self):
        # Draw board squares
        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    pygame.Rect(
                        self.board_rect.left + col * SQUARE_SIZE,
                        self.board_rect.top + row * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE
                    )
                )
        
        # Draw coordinates
        font = pygame.font.SysFont('Arial', 14)
        for i in range(8):
            # Column letters (a-h)
            letter = chr(ord('a') + i)
            text = font.render(letter, True, TEXT_COLOR)
            self.screen.blit(text, (
                self.board_rect.left + i * SQUARE_SIZE + SQUARE_SIZE - 15,
                self.board_rect.bottom - 15
            ))
            
            # Row numbers (1-8)
            number = str(8 - i)
            text = font.render(number, True, TEXT_COLOR)
            self.screen.blit(text, (
                self.board_rect.left + 5,
                self.board_rect.top + i * SQUARE_SIZE + 5
            ))
    
    def draw_pieces(self):
        # Draw pieces
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece != "--":
                    # Don't draw the piece being animated
                    if self.game.animation and (row, col) == self.game.animation["start"]:
                        continue
                    
                    self.screen.blit(
                        PIECE_IMAGES[piece],
                        pygame.Rect(
                            self.board_rect.left + col * SQUARE_SIZE,
                            self.board_rect.top + row * SQUARE_SIZE,
                            SQUARE_SIZE,
                            SQUARE_SIZE
                        )
                    )
        
        # Draw animated piece
        if self.game.animation:
            progress = self.game.animation["progress"] / 100
            sr, sc = self.game.animation["start"]
            er, ec = self.game.animation["end"]
            
            x = self.board_rect.left + sc * SQUARE_SIZE + (ec - sc) * SQUARE_SIZE * progress
            y = self.board_rect.top + sr * SQUARE_SIZE + (er - sr) * SQUARE_SIZE * progress
            
            self.screen.blit(PIECE_IMAGES[self.game.animation["piece"]], (x, y))
    
    def draw_highlights(self):
        # Highlight selected piece
        if self.selected:
            row, col = self.selected
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill(HIGHLIGHT_COLOR)
            self.screen.blit(
                highlight,
                (self.board_rect.left + col * SQUARE_SIZE, 
                 self.board_rect.top + row * SQUARE_SIZE)
            )
        
        # Highlight valid moves
        for move in self.valid_moves:
            row, col = move[:2]
            move_highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            move_highlight.fill(MOVE_COLOR)
            self.screen.blit(
                move_highlight,
                (self.board_rect.left + col * SQUARE_SIZE, 
                 self.board_rect.top + row * SQUARE_SIZE)
            )
        
        # Highlight king in check
        king_pos = self.game.white_king_pos if self.game.white_to_move else self.game.black_king_pos
        if self.game.is_in_check():
            check_highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            check_highlight.fill(CHECK_COLOR)
            self.screen.blit(
                check_highlight,
                (self.board_rect.left + king_pos[1] * SQUARE_SIZE,
                 self.board_rect.top + king_pos[0] * SQUARE_SIZE)
            )
    
    def draw_promotion_menu(self):
        promotion_pieces = ['q', 'r', 'b', 'n']
        color = 'w' if self.game.white_to_move else 'b'
        
        # Calculate promotion menu position
        col = self.game.promotion_choice[1][1]
        promotion_x = self.board_rect.left + col * SQUARE_SIZE
        promotion_y = self.board_rect.top if self.game.white_to_move else self.board_rect.top + 3 * SQUARE_SIZE
        
        # Draw menu background
        menu_height = 4 * SQUARE_SIZE if self.game.white_to_move else SQUARE_SIZE
        menu_rect = pygame.Rect(
            promotion_x,
            promotion_y,
            SQUARE_SIZE,
            menu_height
        )
        pygame.draw.rect(self.screen, (240, 240, 240), menu_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), menu_rect, 2)
        
        # Draw promotion pieces
        pieces_to_show = promotion_pieces if self.game.white_to_move else reversed(promotion_pieces)
        for i, piece in enumerate(pieces_to_show):
            piece_rect = pygame.Rect(
                promotion_x,
                promotion_y + i * SQUARE_SIZE,
                SQUARE_SIZE,
                SQUARE_SIZE
            )
            pygame.draw.rect(self.screen, (220, 220, 220), piece_rect)
            pygame.draw.rect(self.screen, (150, 150, 150), piece_rect, 1)
            
            self.screen.blit(
                PIECE_IMAGES[f"{color}{piece}"],
                piece_rect
            )

if __name__ == "__main__":
    gui = ChessGUI()
    gui.run()
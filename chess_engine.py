import pygame
import copy
from constants import *

class CastleRights:
    def __init__(self, wk=True, wq=True, bk=True, bq=True):
        self.wk = wk  # White kingside
        self.wq = wq  # White queenside
        self.bk = bk  # Black kingside
        self.bq = bq  # Black queenside

class ChessGame:
    def __init__(self, game_mode="human_vs_human", ai_difficulty="medium"):
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["wp"] * 8,
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
        ]
        self.white_to_move = True
        self.move_log = []
        self.move_history = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.white_time = GAME_TIME
        self.black_time = GAME_TIME
        self.last_move_time = None
        self.game_status = "White's turn"
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty
        self.animation = None
        self.en_passant_possible = None
        self.white_castle = CastleRights(True, True)
        self.black_castle = CastleRights(True, True)
        self.castle_rights_log = [CastleRights(True, True, True, True)]
        self.promotion_choice = None

    def is_in_bounds(self, r, c):
        """Check if coordinates are within the board bounds"""
        return 0 <= r < 8 and 0 <= c < 8

    def make_ai_move(self):
        if ((self.game_mode == "human_vs_ai" and not self.white_to_move) or 
            (self.game_mode == "ai_vs_ai")):
            from ai import ChessAI
            ai = ChessAI(self.ai_difficulty)
            best_move = ai.find_best_move(self)
            if best_move:
                return self.move_piece(best_move[0], best_move[1])
        return False

    def move_piece(self, start, end, promotion_choice=None):
        if self.checkmate or self.stalemate:
            return False
            
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        
        if piece == "--":
            return False
        if (piece[0] == 'w' and not self.white_to_move) or (piece[0] == 'b' and self.white_to_move):
            return False

        move_info = self.get_move_info(start, end)
        if not move_info["valid"]:
            return False

        # Handle special moves
        captured = "--"
        if move_info["special"] == "enpassant":
            captured_pos = (sr, ec)
            captured = self.board[sr][ec]
            self.board[sr][ec] = "--"
        elif move_info["special"] == "castle":
            self.handle_castling(end)
        elif move_info["special"] == "promotion":
            if promotion_choice:
                piece = piece[0] + promotion_choice
            else:
                self.promotion_choice = (start, end)
                return "promotion"
        else:
            captured = self.board[er][ec]

        # Make the move
        self.board[er][ec] = piece
        self.board[sr][sc] = "--"
        
        # Update king position
        if piece == "wk":
            self.white_king_pos = (er, ec)
        elif piece == "bk":
            self.black_king_pos = (er, ec)
            
        # Update castling rights
        self.update_castling_rights(piece, start)
        
        # Set en passant if pawn moved two squares
        if piece[1] == 'p' and abs(sr - er) == 2:
            self.en_passant_possible = ((sr + er) // 2, sc)
        else:
            self.en_passant_possible = None
            
        # Log the move
        self.move_log.append({
            "start": start,
            "end": end,
            "piece": piece,
            "captured": captured,
            "special": move_info["special"],
            "castle_rights": copy.deepcopy(self.get_castle_rights())
        })
        
        self.add_move_to_history(start, end, piece, captured, move_info["special"])
        self.update_timers()
        
        # Update turn and status
        self.white_to_move = not self.white_to_move
        self.update_game_status()
        
        # Set animation
        self.animation = {
            "start": start,
            "end": end,
            "piece": piece,
            "progress": 0
        }
        
        # Save current castle rights
        self.castle_rights_log.append(self.get_castle_rights())
        
        return True

    def get_castle_rights(self):
        return CastleRights(self.white_castle.wk, 
                          self.white_castle.wq,
                          self.black_castle.bk,
                          self.black_castle.bq)

    def handle_castling(self, end):
        r, c = end
        if c == 6:  # Kingside
            self.board[r][5] = self.board[r][7]
            self.board[r][7] = "--"
        elif c == 2:  # Queenside
            self.board[r][3] = self.board[r][0]
            self.board[r][0] = "--"

    def update_castling_rights(self, piece, start):
        sr, sc = start
        if piece == "wk":
            self.white_castle.wk = False
            self.white_castle.wq = False
        elif piece == "bk":
            self.black_castle.bk = False
            self.black_castle.bq = False
        elif piece == "wr":
            if sr == 7:  # White rook
                if sc == 0:  # Queenside
                    self.white_castle.wq = False
                elif sc == 7:  # Kingside
                    self.white_castle.wk = False
        elif piece == "br":
            if sr == 0:  # Black rook
                if sc == 0:  # Queenside
                    self.black_castle.bq = False
                elif sc == 7:  # Kingside
                    self.black_castle.bk = False

    def get_move_info(self, start, end):
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        move_info = {
            "valid": False,
            "special": None,
            "captured": None
        }

        if piece == "--":
            return move_info

        valid_moves = self.get_valid_moves(start)
        for move in valid_moves:
            if move[:2] == end:
                move_info["valid"] = True
                if len(move) > 2:  # Special move
                    move_info["special"] = move[2]
                break

        return move_info

    def get_valid_moves(self, start):
        r, c = start
        piece = self.board[r][c]
        if piece == "--":
            return []
            
        color = piece[0]
        possible_moves = []
        
        if piece[1] == 'p':
            possible_moves = self.get_pawn_moves(r, c, color)
        elif piece[1] == 'n':
            possible_moves = self.get_knight_moves(r, c, color)
        elif piece[1] == 'b':
            possible_moves = self.get_bishop_moves(r, c, color)
        elif piece[1] == 'r':
            possible_moves = self.get_rook_moves(r, c, color)
        elif piece[1] == 'q':
            possible_moves = self.get_queen_moves(r, c, color)
        elif piece[1] == 'k':
            possible_moves = self.get_king_moves(r, c, color)
            
        # Filter moves that would leave king in check
        valid_moves = []
        for move in possible_moves:
            if not self.would_be_in_check((r, c), move, color):
                valid_moves.append(move)
                
        return valid_moves

    def would_be_in_check(self, start, move, color):
        # Handle both regular and special moves
        if len(move) > 2:  # Special move with extra info
            end_pos = move[:2]
            special = move[2]
        else:
            end_pos = move
            special = None
            
        sr, sc = start
        er, ec = end_pos
        piece = self.board[sr][sc]
        original_piece = self.board[er][ec]
        
        # Handle special moves
        if special == "enpassant":
            captured_pos = (sr, ec)
            captured = self.board[sr][ec]
            self.board[sr][ec] = "--"
        elif special == "castle":
            self.handle_castling(end_pos)
        
        # Make the move
        self.board[er][ec] = piece
        self.board[sr][sc] = "--"
        
        # Update king position if needed
        old_king_pos = None
        if piece == "wk":
            old_king_pos = self.white_king_pos
            self.white_king_pos = (er, ec)
        elif piece == "bk":
            old_king_pos = self.black_king_pos
            self.black_king_pos = (er, ec)
        
        # Check if in check
        king_pos = self.white_king_pos if color == 'w' else self.black_king_pos
        in_check = self.square_under_attack(king_pos[0], king_pos[1], 'b' if color == 'w' else 'w')
        
        # Undo the move
        self.board[sr][sc] = piece
        self.board[er][ec] = original_piece
        
        # Handle special moves undo
        if special == "enpassant":
            self.board[sr][ec] = captured
        elif special == "castle":
            self.undo_castling(end_pos)
        
        # Restore king position
        if piece == "wk":
            self.white_king_pos = old_king_pos
        elif piece == "bk":
            self.black_king_pos = old_king_pos
            
        return in_check

    def get_pawn_moves(self, r, c, color):
        moves = []
        direction = -1 if color == 'w' else 1
        
        # Forward move
        if self.is_in_bounds(r + direction, c) and self.board[r + direction][c] == "--":
            moves.append((r + direction, c))
            # Double move from starting position
            if (color == 'w' and r == 6) or (color == 'b' and r == 1):
                if self.board[r + 2*direction][c] == "--":
                    moves.append((r + 2*direction, c))
        
        # Capture moves
        for dc in [-1, 1]:
            if self.is_in_bounds(r + direction, c + dc):
                target = self.board[r + direction][c + dc]
                if target != "--" and target[0] != color:
                    moves.append((r + direction, c + dc))
                    
        # En passant
        if self.en_passant_possible:
            ep_r, ep_c = self.en_passant_possible
            if r + direction == ep_r and abs(c - ep_c) == 1:
                moves.append((ep_r, ep_c, "enpassant"))
                    
        # Promotion
        promotion_row = 0 if color == 'w' else 7
        for move in moves.copy():
            if move[0] == promotion_row and len(move) == 2:  # Only simple moves
                moves.remove(move)
                for promo in ['q', 'r', 'b', 'n']:
                    moves.append((move[0], move[1], "promotion"))
        
        return moves

    def get_knight_moves(self, r, c, color):
        moves = []
        knight_moves = [
            (r+2, c+1), (r+2, c-1),
            (r-2, c+1), (r-2, c-1),
            (r+1, c+2), (r+1, c-2),
            (r-1, c+2), (r-1, c-2)
        ]
        for move in knight_moves:
            if self.is_in_bounds(move[0], move[1]):
                target = self.board[move[0]][move[1]]
                if target == "--" or target[0] != color:
                    moves.append(move)
        return moves

    def get_bishop_moves(self, r, c, color):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_r, new_c = r + i*dr, c + i*dc
                if not self.is_in_bounds(new_r, new_c):
                    break
                target = self.board[new_r][new_c]
                if target == "--":
                    moves.append((new_r, new_c))
                else:
                    if target[0] != color:
                        moves.append((new_r, new_c))
                    break
        return moves

    def get_rook_moves(self, r, c, color):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_r, new_c = r + i*dr, c + i*dc
                if not self.is_in_bounds(new_r, new_c):
                    break
                target = self.board[new_r][new_c]
                if target == "--":
                    moves.append((new_r, new_c))
                else:
                    if target[0] != color:
                        moves.append((new_r, new_c))
                    break
        return moves

    def get_queen_moves(self, r, c, color):
        return self.get_rook_moves(r, c, color) + self.get_bishop_moves(r, c, color)

    def get_king_moves(self, r, c, color):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_r, new_c = r + dr, c + dc
                if self.is_in_bounds(new_r, new_c):
                    target = self.board[new_r][new_c]
                    if target == "--" or target[0] != color:
                        moves.append((new_r, new_c))
        
        # Castling
        if not self.is_in_check():
            if color == 'w' and r == 7:
                # Kingside
                if self.white_castle.wk and self.board[7][5] == "--" and self.board[7][6] == "--":
                    if not self.square_under_attack(7, 5) and not self.square_under_attack(7, 6):
                        moves.append((7, 6, "castle"))
                # Queenside
                if self.white_castle.wq and self.board[7][3] == "--" and self.board[7][2] == "--" and self.board[7][1] == "--":
                    if not self.square_under_attack(7, 3) and not self.square_under_attack(7, 2):
                        moves.append((7, 2, "castle"))
            elif color == 'b' and r == 0:
                # Kingside
                if self.black_castle.bk and self.board[0][5] == "--" and self.board[0][6] == "--":
                    if not self.square_under_attack(0, 5) and not self.square_under_attack(0, 6):
                        moves.append((0, 6, "castle"))
                # Queenside
                if self.black_castle.bq and self.board[0][3] == "--" and self.board[0][2] == "--" and self.board[0][1] == "--":
                    if not self.square_under_attack(0, 3) and not self.square_under_attack(0, 2):
                        moves.append((0, 2, "castle"))
        
        return moves

    def square_under_attack(self, r, c, enemy_color=None):
        if enemy_color is None:
            enemy_color = 'b' if self.white_to_move else 'w'
        
        # Check pawn attacks
        direction = 1 if enemy_color == 'w' else -1
        for dc in [-1, 1]:
            if self.is_in_bounds(r + direction, c + dc):
                piece = self.board[r + direction][c + dc]
                if piece == enemy_color + 'p':
                    return True
        
        # Check knight attacks
        knight_moves = [
            (r+2, c+1), (r+2, c-1),
            (r-2, c+1), (r-2, c-1),
            (r+1, c+2), (r+1, c-2),
            (r-1, c+2), (r-1, c-2)
        ]
        for move in knight_moves:
            if self.is_in_bounds(*move):
                piece = self.board[move[0]][move[1]]
                if piece == enemy_color + 'n':
                    return True
        
        # Check bishop/queen diagonal attacks
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_r, new_c = r + i*dr, c + i*dc
                if not self.is_in_bounds(new_r, new_c):
                    break
                piece = self.board[new_r][new_c]
                if piece != "--":
                    if piece[0] == enemy_color and piece[1] in ['b', 'q']:
                        return True
                    break
        
        # Check rook/queen straight attacks
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_r, new_c = r + i*dr, c + i*dc
                if not self.is_in_bounds(new_r, new_c):
                    break
                piece = self.board[new_r][new_c]
                if piece != "--":
                    if piece[0] == enemy_color and piece[1] in ['r', 'q']:
                        return True
                    break
        
        # Check king attacks
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                if self.is_in_bounds(r + dr, c + dc):
                    piece = self.board[r + dr][c + dc]
                    if piece == enemy_color + 'k':
                        return True
        
        return False

    def update_game_status(self):
        if self.is_checkmate():
            winner = "Black" if self.white_to_move else "White"
            self.game_status = f"Checkmate! {winner} wins!"
            self.checkmate = True
        elif self.is_stalemate():
            self.game_status = "Stalemate!"
            self.stalemate = True
        elif self.is_in_check():
            self.game_status = "White's turn (Check)" if self.white_to_move else "Black's turn (Check)"
        else:
            self.game_status = "White's turn" if self.white_to_move else "Black's turn"

    def is_checkmate(self):
        if not self.is_in_check():
            return False
            
        # Check if any move can get out of check
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if (piece[0] == 'w' and self.white_to_move) or (piece[0] == 'b' and not self.white_to_move):
                    if self.get_valid_moves((r, c)):
                        return False
        return True

    def is_stalemate(self):
        if self.is_in_check():
            return False
            
        # Check if any legal move exists
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if (piece[0] == 'w' and self.white_to_move) or (piece[0] == 'b' and not self.white_to_move):
                    if self.get_valid_moves((r, c)):
                        return False
        return True

    def is_in_check(self):
        king_pos = self.white_king_pos if self.white_to_move else self.black_king_pos
        return self.square_under_attack(king_pos[0], king_pos[1])

    def update_timers(self):
        if self.last_move_time is not None:
            current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
            elapsed = current_time - self.last_move_time
            
            if self.white_to_move:
                self.black_time -= elapsed
            else:
                self.white_time -= elapsed
                
            if self.white_time <= 0 or self.black_time <= 0:
                winner = "White" if self.black_time <= 0 else "Black"
                self.game_status = f"Time's up! {winner} wins!"
                self.checkmate = True
                
        self.last_move_time = pygame.time.get_ticks() / 1000

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def add_move_to_history(self, start, end, piece, captured, special=None):
        sr, sc = start
        er, ec = end
        piece_type = piece[1]
        color = piece[0]
        
        # Convert to algebraic notation
        col_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        move_str = ""
        
        if piece_type != 'p':
            move_str += piece_type.upper()
        
        if captured != "--":
            if piece_type == 'p':
                move_str += col_names[sc]
            move_str += 'x'
        
        move_str += col_names[ec] + str(8 - er)
        
        if special == "castle":
            if ec > sc:  # Kingside
                move_str = "O-O"
            else:  # Queenside
                move_str = "O-O-O"
        elif special == "promotion":
            move_str += "=Q"  # Default to queen, actual choice will be shown
        
        self.move_history.append(move_str)

    def undo_move(self):
        if len(self.move_log) == 0:
            return False
            
        last_move = self.move_log.pop()
        start = last_move["start"]
        end = last_move["end"]
        piece = last_move["piece"]
        captured = last_move["captured"]
        special = last_move["special"]
        
        # Restore board position
        self.board[start[0]][start[1]] = piece
        self.board[end[0]][end[1]] = captured
        
        # Handle special moves
        if special == "enpassant":
            self.board[end[0]][start[1]] = captured
            self.board[end[0]][end[1]] = "--"
        elif special == "castle":
            self.undo_castling(end)
        
        # Restore king position
        if piece == "wk":
            self.white_king_pos = start
        elif piece == "bk":
            self.black_king_pos = start
        
        # Restore castling rights
        if len(self.castle_rights_log) > 0:
            self.castle_rights_log.pop()
            if len(self.castle_rights_log) > 0:
                prev_rights = self.castle_rights_log[-1]
                self.white_castle = CastleRights(prev_rights.wk, prev_rights.wq)
                self.black_castle = CastleRights(prev_rights.bk, prev_rights.bq)
        
        # Remove last move from history
        if len(self.move_history) > 0:
            self.move_history.pop()
        
        # Switch turns and update status
        self.white_to_move = not self.white_to_move
        self.update_game_status()
        self.update_timers()
        
        return True

    def undo_castling(self, end):
        r, c = end
        if c == 6:  # Kingside
            self.board[r][7] = self.board[r][5]
            self.board[r][5] = "--"
        elif c == 2:  # Queenside
            self.board[r][0] = self.board[r][3]
            self.board[r][3] = "--"

    def update_animation(self):
        if self.animation:
            self.animation["progress"] += ANIMATION_SPEED
            if self.animation["progress"] >= 100:
                self.animation = None

    def draw_animated_piece(self, screen):
        if not self.animation:
            return

        progress = self.animation["progress"] / 100
        sr, sc = self.animation["start"]
        er, ec = self.animation["end"]
        
        x = sc * SQUARE_SIZE + (ec - sc) * SQUARE_SIZE * progress
        y = sr * SQUARE_SIZE + (er - sr) * SQUARE_SIZE * progress
        
        screen.blit(PIECE_IMAGES[self.animation["piece"]], (x, y))
import random
import copy
from constants import *

class ChessAI:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.depth = AI_DIFFICULTIES[difficulty]["depth"]
        
    def find_best_move(self, game):
        valid_moves = []
        for r in range(8):
            for c in range(8):
                piece = game.board[r][c]
                if (piece[0] == 'b' and not game.white_to_move) or (piece[0] == 'w' and game.white_to_move):
                    moves = game.get_valid_moves((r, c))
                    for move in moves:
                        # Only use the position part for AI moves
                        valid_moves.append(((r, c), move[:2]))
        
        if not valid_moves:
            return None
            
        if self.difficulty == "easy":
            return random.choice(valid_moves)
        else:
            best_move = None
            best_score = -9999 if game.white_to_move else 9999
            
            for move in valid_moves:
                game_copy = copy.deepcopy(game)
                game_copy.move_piece(move[0], move[1])
                
                if self.difficulty == "medium":
                    score = self.evaluate_board(game_copy)
                else:  # hard
                    score = self.minimax(game_copy, self.depth-1, -10000, 10000, not game.white_to_move)
                
                if (game.white_to_move and score > best_score) or (not game.white_to_move and score < best_score):
                    best_score = score
                    best_move = move
                    
            return best_move

    def evaluate_board(self, game):
        piece_values = {
            'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0
        }
        
        score = 0
        for r in range(8):
            for c in range(8):
                piece = game.board[r][c]
                if piece != "--":
                    value = piece_values[piece[1]]
                    if piece[0] == 'w':
                        score += value
                    else:
                        score -= value
                        
        return score

    def minimax(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.checkmate or game.stalemate:
            return self.evaluate_board(game)
            
        valid_moves = []
        for r in range(8):
            for c in range(8):
                piece = game.board[r][c]
                if (piece[0] == 'w' and maximizing_player) or (piece[0] == 'b' and not maximizing_player):
                    moves = game.get_valid_moves((r, c))
                    for move in moves:
                        valid_moves.append(((r, c), move[:2]))
        
        if maximizing_player:
            max_eval = -9999
            for move in valid_moves:
                game_copy = copy.deepcopy(game)
                game_copy.move_piece(move[0], move[1])
                eval = self.minimax(game_copy, depth-1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 9999
            for move in valid_moves:
                game_copy = copy.deepcopy(game)
                game_copy.move_piece(move[0], move[1])
                eval = self.minimax(game_copy, depth-1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
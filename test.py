from stockfish import Stockfish

# Make sure the path is correct
stockfish = Stockfish(path="engines/stockfish.exe")

# Set skill level from 0 (weakest) to 20 (strongest)
stockfish.set_skill_level(5)

# Set up the default board position
stockfish.set_position([])

# Get the best move from the starting position
best_move = stockfish.get_best_move()

print("Stockfish best move from starting position:", best_move)

import os
import pygame

# Initialize pygame for font loading
pygame.init()

# Window dimensions
WIDTH = 1000
HEIGHT = 800

# Board dimensions
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (247, 247, 105, 150)
MOVE_COLOR = (106, 168, 79, 150)
CHECK_COLOR = (255, 0, 0, 150)
UI_BG = (240, 240, 240)
TEXT_COLOR = (50, 50, 50)

# Fonts
FONT_LARGE = pygame.font.SysFont('Arial', 36)
FONT_MEDIUM = pygame.font.SysFont('Arial', 24)
FONT_SMALL = pygame.font.SysFont('Arial', 18)

# Game settings
FPS = 60
ANIMATION_SPEED = 15
GAME_TIME = 600  # 10 minutes in seconds

# Piece images
PIECE_IMAGES = {}
for color in ['w', 'b']:
    for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
        key = f"{color}{piece}"
        try:
            img = pygame.image.load(f"assets/pieces/{key}.png")
            PIECE_IMAGES[key] = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
        except:
            # Fallback if image not found
            surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(surf, (200, 0, 0) if color == 'w' else (0, 0, 200), 
                             (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
            PIECE_IMAGES[key] = surf

# Game modes
GAME_MODES = {
    "human_vs_human": "Human vs Human",
    "human_vs_ai": "Human vs Computer",
    "ai_vs_ai": "Computer vs Computer"
}

# AI difficulties
AI_DIFFICULTIES = {
    "easy": {"depth": 1, "name": "Easy"},
    "medium": {"depth": 3, "name": "Medium"},
    "hard": {"depth": 5, "name": "Hard"}
}
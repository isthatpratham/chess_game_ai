# ♟️ Chess Game with AI (Python + Pygame)

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/github/license/isthatpratham/chess_game_ai)
![Made with Pygame](https://img.shields.io/badge/Made%20with-Pygame-2b303a?logo=pygame)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

A full-featured chess game built in Python using Pygame. Supports Human vs Human, Human vs AI, and AI vs AI—with move animation, special rules like castling and en passant, move history, time control, and a clean UI.


### 🚩 Features

- 🎮 Game Modes:
  - Human vs Human
  - Human vs AI
  - AI vs AI

- 🤖 AI Difficulties:
  - Easy – random legal moves
  - Medium – material-based evaluation
  - Hard – minimax with alpha-beta pruning (depth: 5)

- ♟️ Fully implemented rules:
  - Castling
  - En Passant
  - Promotion (with GUI menu)
  - Check, Checkmate, Stalemate
  - Timer-based victories

- ⏱️ Game Clock:
  - 10-minute timer for each player
  - Clock updates live during gameplay

- 📝 UI Highlights:
  - Valid moves
  - Selected piece
  - King in check
  - Move history
  - Animated piece movement

<br>

### 📸 Screenshots

<img width="990" height="819" alt="Screenshot 2025-07-20 142405" src="https://github.com/user-attachments/assets/d8f90828-3709-4986-bddc-3093709624d4" />
<br>
<img width="988" height="820" alt="Screenshot 2025-07-20 142439" src="https://github.com/user-attachments/assets/0bbaf147-df88-464c-bd48-1bdb03e25510" />
<br>
<img width="993" height="822" alt="Screenshot 2025-07-20 142657" src="https://github.com/user-attachments/assets/92c54b6b-6699-4825-bc52-96ae26a26145" />
<br>
<img width="993" height="822" alt="Screenshot 2025-07-20 142657" src="https://github.com/user-attachments/assets/3ff24354-ddcd-43eb-a421-8f0630dc984b" />
<br>
<img width="991" height="824" alt="Screenshot 2025-07-20 142608" src="https://github.com/user-attachments/assets/b77eec4f-6ee7-4deb-bd1e-77ef0e84482c" />


<br>

### To Start follow these steps:

#### 1. Clone the repository

```bash
git clone https://github.com/isthatpratham/chess_game_ai.git
cd chess_game_ai
```

#### 2. Install dependencies

```bash
pip install pygame
```

#### 3. Install Stockfish (for engine-based analysis)

- Download Stockfish from: https://stockfishchess.org/download/
- Add the executable to your system PATH or keep it in the project folder.
- Make sure it's accessible via command line with `stockfish`.

#### 4. Run the game

```bash
python main.py
```

---

### 📁 Folder Structure

```
.
├── ai.py                 # AI logic and evaluation
├── board.py              # Initial board layout
├── chess_engine.py       # Move generation and game state
├── constants.py          # Configs, colors, fonts, image loading
├── main.py               # GUI and event handling
└── assets/
    └── pieces/           # Chess piece images (e.g. wq.png, br.png)
```

---

### ⌨️ Controls

| Action         | Shortcut       |
|----------------|----------------|
| Move Piece     | Mouse click    |
| Undo Move      | Ctrl + Z       |
| Open Menu      | ESC            |

---

### 🧠 AI Logic

- **Easy**: Random legal moves
- **Medium**: Evaluates material on board
- **Hard**: Minimax + alpha-beta pruning (depth: 5)

---

### 🧰 Areas of Improvement (Upcoming)

- [ ] Fix **Hard Mode** logic in Human vs AI and AI vs AI
- [ ] Add **evaluation bar** to reflect real-time position score
- [ ] Fix **UI bugs** in game mode selection screen (Human vs AI & AI vs AI)

---

### 🖼️ Custom Game Icon (Optional)

To add a custom window icon:

1. Place your icon (preferably 32x32 `.png`) inside the `assets/` folder, e.g. `assets/icon.png`.

2. Add this to the top of `main.py`, **after** `pygame.init()`:

```python
icon = pygame.image.load("assets/icon.png")
pygame.display.set_icon(icon)
```

---

### 📜 License

MIT License

---

### 👨‍💻 Author

**Pratham Debnath**

- 🔗 [GitHub](https://github.com/isthatpratham)
- 💼 [LinkedIn](https://www.linkedin.com/in/pratham-debnath-894471314/)
- 📸 [Instagram](https://www.instagram.com/prathamfrsure/)

---

*Built with Python. Designed to learn, improve, and maybe even checkmate you.*
```

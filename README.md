# Spoon Egg Farm
A simple idle clicker game implemented with Python and Pygame.
> An idle farm simulation mini-game. Click on the farm to produce eggs, watch your eggs appear on the screen. This project is developed for Python and Pygame learning practice.

## 🎮 Game Introduction
Spoon Egg Farm is a lightweight idle click game. When you click on the green farm area in the game window, new eggs will be generated and displayed on the screen. You can keep clicking to spawn more eggs. All eggs stay on the game screen. The game has simple graphic rendering and mouse event logic, suitable for beginners to learn 2D game development with Pygame.

## 📋 Game Features
- Mouse click event detection: left mouse click to spawn eggs
- Simple egg rendering and position randomization
- Fixed-size game window
- Basic background farm color
- Clean and readable source code structure
- Easy to modify and extend new game mechanics
- **Scrollable right-side control panel**: Top status text and bottom market UI stay fixed, only the middle button area scrolls, implemented with `screen.set_clip` for region clipping, preventing UI overflow
- Multi-egg drag: Support dragging multiple eggs at once

## 🧰 Environment & Dependencies
### Required
- Python 3.8 or higher
- Pygame >= 2.5.0

All dependencies are listed in `requirements.txt`

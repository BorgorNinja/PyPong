# PyPong 2025

A modern, animated version of the classic Pong game built with Python and Pygame.

## Features

- **Single-player mode**: Play against a CPU opponent with moderate AI.
- **Pause menu**: Press `ESC` during the game to pause and resume.
- **Animated UI**: Smooth button animations in the main menu.
- **Background music placeholders**: Easily replace with actual music files.
- **Sound effects placeholders**: Add your own sounds for ball hits, scoring, etc.
- **Win/Lose screen**: Displays a pulsating text animation when the game ends.

## Installation

### Prerequisites
Make sure you have Python installed on your system.

```sh
python --version
```

If Python is not installed, download and install it from [python.org](https://www.python.org/).

### Install Pygame

You need Pygame to run the game. Install it using:

```sh
pip install pygame
```

### Run the Game

Clone this repository and navigate to the project folder:

```sh
git clone https://github.com/your-username/pong-game.git
cd pong-game
```

Then, run the game with:

```sh
python pong.py
```

## Controls

| Action       | Key |
|-------------|-----|
| Move Up     | `W` |
| Move Down   | `S` |
| Pause       | `ESC` |

## How to Add Your Own Sounds

- Replace `play_background_music(track_name)` with actual sound file loading using `pygame.mixer.music.load()`.
- Modify `play_sound(name)` to play your own sound effects.

## How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy playing Pong! 🚀


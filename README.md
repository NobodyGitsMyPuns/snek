# genAi Snake Game (PoC)

This is a proof of concept (PoC) project exploring how far I could go building a game using mostly Python. The core logic and gameplay were all written in native Python, using the `pygame` library for rendering and interaction.

## Features

- Classic Snake game mechanics
- Keyboard input controls
- Score tracking with high score file persistence
- Background image support
- Sound effects for gameplay events

## Motivation

The goal was to create a simple but complete game using just Python. As the game evolved, I wanted to enhance the experience with music and a background image. That's where I broke out of "pure Python" and began leveraging AI tools to help finish the polish:

- 🎵 **Background music and sounds** — integrated using `pygame.mixer`
- 🧠 **Assisted development** — used ChatGPT and my own local LLM (via Ollama) to help debug issues and rapidly add features like high score persistence, file handling, and game polish

## Getting Started

### Requirements

- Python 3.10+
- `pygame` (install with `pip install pygame`)

### Running the Game

```bash
python game.py

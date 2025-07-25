import pytest
from game import SnakeGame  # Assuming the main game logic is in a class named 'SnakeGame'

def test_snake_movement():
    game = SnakeGame()
    initial_position = game.snake_pos
    game.update(direction="right")  # Assuming there's an update method that moves the snake
    assert game.snake_pos != initial_position, "Snake didn't move as expected!"

def test_food_eaten():
    game = SnakeGame()
    initial_score = game.score
    game.update(direction="right")  # Move the snake to eat food
    assert game.score > initial_score, "Food wasn't eaten as expected!"

def test_gameover():
    game = SnakeGame()
    game.snake_pos = game.food_pos  # Set the snake position to be on top of the food
    with pytest.raises(SystemExit):  # The game should exit when it's over
        game.update()

import pygame
import random
import sys
import time
import os

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Constants
screen_width = 800
screen_height = 600
BLOCK_SIZE = 20
HIGH_SCORE_FILE = 'highscores.txt'

# Set up display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game')

# Load background image or fallback to light blue
try:
    background_img = pygame.image.load("assets/images/background.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))
except:
    background_img = None
    light_blue = (173, 216, 230)

# Colors
green = (0, 255, 0)
red = (255, 0, 0)
gold = (255, 215, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

# Clock and fonts
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 48)

# Load sounds (fallback to print)
def load_sound(name):
    try:
        return pygame.mixer.Sound(name)
    except:
        class DummySound:
            def play(self): print(f"[SOUND] {name} missing or failed to play")
        return DummySound()

        return lambda: print(f"[SOUND] {name} missing")

score10_sound = load_sound("assets/audio/tenpt.mp3")
score50_sound = load_sound("assets/audio/fiftypt.mp3")
gameover_sound = load_sound("assets/audio/dead.mp3")
new_high_score_sound = load_sound("assets/audio/highscore.mp3")

try:
    pygame.mixer.music.load("assets/audio/background.mp3")
    pygame.mixer.music.play(-1)
except:
    print("[MUSIC] background_music.mp3 missing or failed to load")

# Snake and food
snake_pos = [BLOCK_SIZE * 5, BLOCK_SIZE * 5]
snake_body = [
    list(snake_pos),
    [snake_pos[0] - BLOCK_SIZE, snake_pos[1]],
    [snake_pos[0] - 2 * BLOCK_SIZE, snake_pos[1]]
]

food_pos = [300, 200]
gold_food = None
gold_spawn_time = None
gold_duration = 5
next_gold_spawn = time.time() + 10

# Direction
direction = 'RIGHT'
change_to = direction
speed = 10
score = 0

# UI for initials
def get_initials():
    input_text = ''
    while True:
        screen.fill((0, 0, 0))
        prompt = large_font.render("Enter 3-letter initials:", True, white)
        entered = large_font.render(input_text, True, white)
        screen.blit(prompt, (screen_width // 2 - prompt.get_width() // 2, 200))
        screen.blit(entered, (screen_width // 2 - entered.get_width() // 2, 270))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(input_text) == 3:
                    return input_text.upper()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif len(input_text) < 3 and event.unicode.isalpha():
                    input_text += event.unicode.upper()

def save_high_score(initials, score):
    scores = load_high_scores()
    scores.append((initials, score))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
    with open(HIGH_SCORE_FILE, 'w') as f:
        for name, s in scores:
            f.write(f"{name} {s}\n")

def load_high_scores():
    if not os.path.exists(HIGH_SCORE_FILE):
        return []
    with open(HIGH_SCORE_FILE, 'r') as f:
        return [(line.split()[0], int(line.split()[1])) for line in f.readlines()]

def display_new_high_score():
    new_text = large_font.render("NEW HIGH SCORE!!!", True, yellow)
    screen.fill((0, 0, 0))
    screen.blit(new_text, (screen_width // 2 - new_text.get_width() // 2, screen_height // 2 - new_text.get_height() // 2))
    pygame.display.update()
    new_high_score_sound.play()
    time.sleep(2)

def display_high_scores():
    screen.fill((0, 0, 0))
    title = font.render("TOP 10 HIGH SCORES", True, white)
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 50))
    for i, (name, s) in enumerate(load_high_scores()):
        txt = font.render(f"{i + 1}. {name} - {s}", True, white)
        screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, 100 + i * 30))
    pygame.display.update()
    time.sleep(5)

def cascade_you_lose():
    text = large_font.render("YOU LOSE", True, red)
    y = -text.get_height()
    center_x = screen_width // 2 - text.get_width() // 2
    center_y = screen_height // 2 - text.get_height() // 2

    while y < center_y:
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(light_blue)

        for i, block in enumerate(snake_body):
            color = (0, 200, 0) if i == 0 else green
            pygame.draw.rect(screen, color, pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(screen, red, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
        if gold_food:
            pygame.draw.rect(screen, gold, pygame.Rect(gold_food[0], gold_food[1], BLOCK_SIZE, BLOCK_SIZE))

        screen.blit(text, (center_x, y))
        pygame.display.update()
        y += 10
        clock.tick(30)

    time.sleep(2)

# Prompt initials
initials = get_initials()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and direction != 'DOWN':
                change_to = 'UP'
            elif event.key == pygame.K_s and direction != 'UP':
                change_to = 'DOWN'
            elif event.key == pygame.K_a and direction != 'RIGHT':
                change_to = 'LEFT'
            elif event.key == pygame.K_d and direction != 'LEFT':
                change_to = 'RIGHT'
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                speed += 1
            elif event.key == pygame.K_MINUS and speed > 1:
                speed -= 1

    direction = change_to
    if direction == 'UP':
        snake_pos[1] -= BLOCK_SIZE
    if direction == 'DOWN':
        snake_pos[1] += BLOCK_SIZE
    if direction == 'LEFT':
        snake_pos[0] -= BLOCK_SIZE
    if direction == 'RIGHT':
        snake_pos[0] += BLOCK_SIZE

    snake_pos[0] %= screen_width
    snake_pos[1] %= screen_height
    snake_body.insert(0, list(snake_pos))

    # Food collision
    ate = False
    if snake_pos == food_pos:
        score += 10
        score10_sound.play()
        food_pos = [random.randint(0, (screen_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                    random.randint(0, (screen_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE]
        ate = True

    # Gold food collision
    if gold_food and snake_pos == gold_food:
        score += 50
        score50_sound.play()
        gold_food = None
        gold_spawn_time = None
        ate = True

    if not ate:
        snake_body.pop()

    # Self collision
    if snake_pos in snake_body[1:]:
        gameover_sound.play()
        cascade_you_lose()
        high_scores = load_high_scores()
        if len(high_scores) < 10 or score > high_scores[-1][1]:
            display_new_high_score()
        save_high_score(initials, score)
        display_high_scores()
        pygame.quit()
        sys.exit()

    # Gold food spawn/despawn
    current_time = time.time()
    if not gold_food and current_time >= next_gold_spawn:
        gold_food = [random.randint(0, (screen_width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                     random.randint(0, (screen_height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE]
        gold_spawn_time = current_time
        next_gold_spawn = current_time + 10

    if gold_food and current_time - gold_spawn_time > gold_duration:
        gold_food = None
        gold_spawn_time = None

    # Draw
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(light_blue)

    for i, block in enumerate(snake_body):
        color = (0, 200, 0) if i == 0 else green
        pygame.draw.rect(screen, color, pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))

    pygame.draw.rect(screen, red, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
    if gold_food:
        pygame.draw.rect(screen, gold, pygame.Rect(gold_food[0], gold_food[1], BLOCK_SIZE, BLOCK_SIZE))

    score_text = font.render(f'{initials}  Score: {score}  Speed: {speed}', True, white)
    screen.blit(score_text, (10, 10))
    pygame.display.update()
    clock.tick(speed)

pygame.quit()
sys.exit()

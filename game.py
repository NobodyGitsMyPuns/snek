########################################################################
# Full Snake Game with Gold Food Explosion Effect and High Score System
########################################################################

import pygame
import random
import sys
import time
import os

# -----------------------------------------------------------------------------
# Initialize Pygame and Mixer
# -----------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
screen_width    = 800
screen_height   = 600
BLOCK_SIZE      = 20
HIGH_SCORE_FILE = 'highscores.txt'

# Explosion blast radius in blocks
BLAST_RADIUS    = 3  # 1 for 3x3, 2 for 5x5

# -----------------------------------------------------------------------------
# Setup display
# -----------------------------------------------------------------------------
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game')

# -----------------------------------------------------------------------------
# Load background image or fallback color
# -----------------------------------------------------------------------------
try:
    background_img = pygame.image.load("assets/images/background.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))
except Exception:
    background_img = None
    light_blue = (173, 216, 230)

# -----------------------------------------------------------------------------
# Colors
# -----------------------------------------------------------------------------
green      = (0,   255, 0)
red        = (255, 0,   0)
gold_color = (255, 215, 0)
white      = (255, 255, 255)
yellow     = (255, 255, 0)
orange     = (255, 140, 0)
dark_gray  = (50,  50,  50)
light_gray = (180, 180, 180)
black      = (0,    0,   0)

# -----------------------------------------------------------------------------
# Fonts and Clock
# -----------------------------------------------------------------------------
clock      = pygame.time.Clock()
font       = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 48)

# -----------------------------------------------------------------------------
# Sound Loading and Placeholders
# -----------------------------------------------------------------------------
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        # Fallback prints missing sound
        return lambda: print(f"[SOUND] {os.path.basename(path)} missing")

score10_sound        = load_sound("assets/audio/tenpt.mp3")
score50_sound        = load_sound("assets/audio/fiftypt.mp3")
gameover_sound       = load_sound("assets/audio/dead.mp3")
new_high_score_sound = load_sound("assets/audio/highscore.mp3")
body_cut_sound       = load_sound("assets/audio/slice.mp3")
head_shot_sound      = load_sound("assets/audio/headshot.mp3")
explosion_sound      = load_sound("assets/audio/explosion.mp3")
beep_sound           = load_sound("assets/audio/beepbomb.mp3")

# Background music
try:
    pygame.mixer.music.load("assets/audio/background.mp3")
    pygame.mixer.music.play(-1)
except Exception:
    print("[MUSIC] background.mp3 missing or failed to load")

# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def draw_background():
    """Draw the background image or fallback color."""
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(light_blue)


def draw_snake(snake_body):
    """Draw the snake blocks on screen."""
    for idx, block in enumerate(snake_body):
        color = (0, 200, 0) if idx == 0 else green
        rect = pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, color, rect)


def render_text_centered(text, font_obj, color, y_pos):
    """Render text centered horizontally at given y coordinate."""
    surf = font_obj.render(text, True, color)
    x = (screen_width - surf.get_width()) // 2
    screen.blit(surf, (x, y_pos))

# -----------------------------------------------------------------------------
# High Score Management
# -----------------------------------------------------------------------------

def load_high_scores():
    """Load top scores from file."""
    if not os.path.exists(HIGH_SCORE_FILE):
        return []
    scores = []
    with open(HIGH_SCORE_FILE, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                scores.append((parts[0], int(parts[1])))
    return scores


def save_high_score(initials, score):
    """Append and trim high scores, then save."""
    scores = load_high_scores()
    scores.append((initials, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:10]
    with open(HIGH_SCORE_FILE, 'w') as f:
        for name, pts in scores:
            f.write(f"{name} {pts}\n")


def display_high_scores():
    """Display the top 10 scores screen."""
    draw_background()
    render_text_centered("TOP 10 HIGH SCORES", font, white, 50)
    scores = load_high_scores()
    for i, (name, pts) in enumerate(scores):
        line = f"{i+1}. {name} - {pts}"
        render_text_centered(line, font, white, 100 + i * 30)
    pygame.display.update()
    time.sleep(3)

def cascade_new_high_score(initials, score):
    """Cascade the NEW HIGH SCORE text."""
    text_surf = large_font.render("NEW HIGH SCORE BY " + initials + " " + str(score), True, gold_color)
    time.sleep(1)
    x = (screen_width - text_surf.get_width()) // 2
    y = -text_surf.get_height()
    target_y = (screen_height - text_surf.get_height()) // 2
    while y < target_y:
        draw_background()
        screen.blit(text_surf, (x, y))
        pygame.display.update()
        y += 10
        clock.tick(30)
    time.sleep(1)

def check_highscore(initials, score):
    global highscore   # Declare highscore as a global variable
    if score > highscore:
        highscore = score
        
        font = pygame.font.Font(None, 36)   # Create a new font object for the message
        text_new_high_score = font.render("New High Score Achieved: " + str(highscore), True, white)   # Render the message as an image
        
        screen.blit(text_new_high_score, [250, 250])   # Display the message on the screen at coordinates (250, 250)
        pygame.display.flip()   # Update the display with the new high score message
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:   # Wait for the Enter key to be pressed
                        waiting = False
        
        return initials, highscore

    # -----------------------------------------------------------------------------
# User Initials Input
# -----------------------------------------------------------------------------

def get_initials():
    """Prompt the player for 3-letter initials."""
    initials = ''
    while True:
        draw_background()
        render_text_centered("Enter 3-letter initials:", large_font, white, 200)
        render_text_centered(initials, large_font, white, 260)
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                hs = load_high_scores()
                if len(hs) < 10 or score > hs[-1][1]:
                    handle_highscore(score, initials)
                pygame.quit()
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and len(initials) == 3:
                    return initials
                elif ev.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif ev.unicode.isalpha() and len(initials) < 3:
                    initials += ev.unicode.upper()

# -----------------------------------------------------------------------------
# Cascade 'You Lose' Animation
# -----------------------------------------------------------------------------

def cascade_you_lose(snake_body, food_pos, gold_food):
    """Animate losing sequence with snake and YOU LOSE text."""
    text_surf = large_font.render("YOU LOSE", True, red)
    x = (screen_width - text_surf.get_width()) // 2
    y = -text_surf.get_height()
    target_y = (screen_height - text_surf.get_height()) // 2
    while y < target_y:
        draw_background()
        draw_snake(snake_body)
        pygame.draw.rect(screen, red, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
        if gold_food:
            pygame.draw.rect(screen, gold_color, pygame.Rect(gold_food[0], gold_food[1], BLOCK_SIZE, BLOCK_SIZE))
        screen.blit(text_surf, (x, y))
        pygame.display.update()
        y += 10
        clock.tick(30)
    time.sleep(1)

# -----------------------------------------------------------------------------
# Explosion Effect
# -----------------------------------------------------------------------------

def explode_tiles(tiles):
    """Visual explosion sequence on tiles list."""
    sequence = [orange, red, dark_gray, light_gray, black]
    explosion_sound.play()
    for color in sequence:
        draw_background()
        for px, py in tiles:
            pygame.draw.rect(screen, color, pygame.Rect(px, py, BLOCK_SIZE, BLOCK_SIZE))
        pygame.display.update()
        pygame.time.delay(100)

def handle_highscore(score, initials):
    """Check and handle new high score state."""
    scores = load_high_scores()
    is_new = len(scores) < 10 or score > scores[-1][1]

    if is_new:
        save_high_score(initials, score)
        new_high_score_sound.play()
        cascade_new_high_score(initials, score)
        display_high_scores()

# -----------------------------------------------------------------------------
# Main Game Loop
# -----------------------------------------------------------------------------

def main():
    # Initial snake position and body
    snake_pos       = [BLOCK_SIZE * 5, BLOCK_SIZE * 5]
    snake_body      = [
        list(snake_pos),
        [snake_pos[0] - BLOCK_SIZE, snake_pos[1]],
        [snake_pos[0] - 2 * BLOCK_SIZE, snake_pos[1]]
    ]

    # Initial food positions and timers
    food_pos        = [
        random.randrange(0, screen_width, BLOCK_SIZE),
        random.randrange(0, screen_height, BLOCK_SIZE)
    ]
    gold_food       = None
    gold_spawn_time = 0
    gold_duration   = 5
    next_gold_spawn = time.time() + 10

    # Initial game state
    direction       = 'RIGHT'
    change_to       = direction
    speed           = 10
    score           = 0
    global highscore
    highscore = 0

    # get high score from file
    highscore = load_high_scores()
    if len(highscore) > 0:
        highscore = highscore[0][1]
    else:
        highscore = 0

    # Get player initials
    initials = get_initials()

    # Main loop
    while True:
        # Event handling
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                #check if it is a new high score
                hs = load_high_scores()
                if len(hs) < 10 or score > hs[-1][1]:
                    new_high_score_sound.play()
                    initials, scoreHigh = check_highscore(initials, score)
                    if scoreHigh > highscore:
                        highscore = scoreHigh
                        save_high_score(initials, scoreHigh)
                        cascade_new_high_score(initials, scoreHigh)
                        #play sound
                        display_high_scores()
                    else:
                        pygame.quit()
                else:
                    pygame.quit()
                    sys.exit(0)

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w and direction != 'DOWN':
                    change_to = 'UP'
                if ev.key == pygame.K_s and direction != 'UP':
                    change_to = 'DOWN'
                if ev.key == pygame.K_a and direction != 'RIGHT':
                    change_to = 'LEFT'
                if ev.key == pygame.K_d and direction != 'LEFT':
                    change_to = 'RIGHT'
                if ev.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    speed += 1
                if ev.key == pygame.K_MINUS and speed > 1:
                    speed -= 1

        # Update direction
        direction = change_to

        # Move snake head
        if direction == 'UP':    snake_pos[1] -= BLOCK_SIZE
        if direction == 'DOWN':  snake_pos[1] += BLOCK_SIZE
        if direction == 'LEFT':  snake_pos[0] -= BLOCK_SIZE
        if direction == 'RIGHT': snake_pos[0] += BLOCK_SIZE

        # Wrap around screen edges
        snake_pos[0] %= screen_width
        snake_pos[1] %= screen_height

        # Insert new head position
        snake_body.insert(0, list(snake_pos))

        ate = False

        # Check regular food collision
        if snake_pos == food_pos:
            score += 10
            score10_sound.play()
            food_pos = [
                random.randrange(0, screen_width, BLOCK_SIZE),
                random.randrange(0, screen_height, BLOCK_SIZE)
            ]
            ate = True

        # Check gold food collision
        if gold_food and snake_pos == gold_food:
            beep_sound.stop()
            explosion_sound.stop()
            score += 50
            score50_sound.play()
            gold_food = None
            gold_spawn_time = 0
            ate = True

        # If no food eaten, remove tail
        if not ate:
            snake_body.pop()

        # Self collision detection
        if snake_pos in snake_body[1:]:
            gameover_sound.play()
            cascade_you_lose(snake_body, food_pos, gold_food)
            handle_highscore(score, initials)
            pygame.quit()
            sys.exit()

        # Current time for timers
        current_time = time.time()

        # Spawn gold food periodically
        if not gold_food and current_time >= next_gold_spawn:
            gold_food = [
                random.randrange(0, screen_width, BLOCK_SIZE),
                random.randrange(0, screen_height, BLOCK_SIZE)
            ]
            gold_spawn_time = current_time
            next_gold_spawn = current_time + 10

        # Gold countdown flash and beep
        if gold_food:
            remaining = gold_duration - (current_time - gold_spawn_time)
            if remaining <= 2.5:
                if int(remaining * 4) % 2 == 0:
                    draw_background()
                if int(current_time * 4) % 4 == 0:
                    beep_sound.play()

        # Gold despawn and explosion effect
        if gold_food and current_time - gold_spawn_time > gold_duration:
            # Determine affected snake segments within blast radius
            beep_sound.stop()
            explosion_sound.play()
            affected = []
            for idx, part in enumerate(snake_body):
                dx = abs(part[0] - gold_food[0]) // BLOCK_SIZE
                dy = abs(part[1] - gold_food[1]) // BLOCK_SIZE
                if dx <= BLAST_RADIUS and dy <= BLAST_RADIUS:
                    affected.append((idx, part))
            if affected:
                # Sort by segment index
                affected.sort(key=lambda x: x[0])
                indices = [i for i, _ in affected]
                tiles   = [p for _, p in affected]

                # Show explosion animation on tiles
                explode_tiles(tiles)

                first_hit = indices[0]
                # If head hit => game over
                if first_hit == 0:
                    head_shot_sound.play()
                    gameover_sound.play()
                    cascade_you_lose(snake_body, food_pos, gold_food)
                    handle_highscore(score, initials)
                    pygame.quit()
                    sys.exit()
                else:
                    # Cut snake body and deduct score
                    cut_len = len(snake_body) - first_hit
                    score   = max(score - cut_len * 10, 0)
                    body_cut_sound.play()
                    snake_body = snake_body[:first_hit]

            # Reset gold food
            gold_food       = None
            gold_spawn_time = 0

        # ---------------------------------------------------------------------
        # Render everything
        # ---------------------------------------------------------------------
        draw_background()
        draw_snake(snake_body)

        # Draw foods
        pygame.draw.rect(screen, red,   pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
        if gold_food:
            pygame.draw.rect(screen, gold_color, pygame.Rect(gold_food[0], gold_food[1], BLOCK_SIZE, BLOCK_SIZE))

        # HUD: score and speed
        hud_text = f"Score: {score}  Speed: {speed} High Score: {highscore}"
        hud_surf = font.render(hud_text, True, white)
        screen.blit(hud_surf, (10, 10))

        pygame.display.update()
        clock.tick(speed)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_h]:
            initials, highscore = check_highscore(initials, score)

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()

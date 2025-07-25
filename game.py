import pygame, random, sys, time, os
from PIL import Image

pygame.init()
pygame.mixer.init()

screen_width, screen_height = 800, 600
BLOCK_SIZE = 20
HIGH_SCORE_FILE = 'highscores.txt'
BLAST_RADIUS = 3
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game')

def load_webp_frames(path, size=None):
    try:
        img = Image.open(path)
        frames, durations = [], []
        for i in range(img.n_frames):
            img.seek(i)
            frame = img.convert("RGBA")
            if size:
                frame = frame.resize(size)
            mode, size_, data = frame.mode, frame.size, frame.tobytes()
            surf = pygame.image.fromstring(data, size_, mode)
            frames.append(surf)
            durations.append(img.info.get("duration", 100) * 2)  # or *3, *4 etc.
        return frames, durations
    except Exception as e:
        print(f"[WEBP] Failed to load animation: {e}")
        return [], []

background_frames, frame_durations = load_webp_frames("assets/images/background.webp", (screen_width, screen_height))
current_frame_idx, frame_timer = 0, 0

green, red, gold_color, white,titanium_white = (0,255,0),(255,0,0),(255,215,0),(255,255,255),(255,255,255)
yellow, orange, dark_gray, light_gray, black = (255,255,0),(255,140,0),(50,50,50),(180,180,180),(0,0,0)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 48)

def load_sound(path):
    try: return pygame.mixer.Sound(path)
    except: return lambda: print(f"[SOUND] {os.path.basename(path)} missing")

score10_sound = load_sound("assets/audio/tenpt.mp3")
score50_sound = load_sound("assets/audio/fiftypt.mp3")
gameover_sound = load_sound("assets/audio/dead.mp3")
new_high_score_sound = load_sound("assets/audio/highscore.mp3")
body_cut_sound = load_sound("assets/audio/slice.mp3")
head_shot_sound = load_sound("assets/audio/headshot.mp3")
explosion_sound = load_sound("assets/audio/explosion.mp3")
beep_sound = load_sound("assets/audio/beepbomb.mp3")

try:
    pygame.mixer.music.load("assets/audio/background.mp3")
    pygame.mixer.music.play(-1)
except:
    print("[MUSIC] background.mp3 missing or failed to load")

def draw_background():
    global current_frame_idx, frame_timer
    if background_frames:
        now = pygame.time.get_ticks()
        if now - frame_timer >= frame_durations[current_frame_idx]:
            frame_timer = now
            current_frame_idx = (current_frame_idx + 1) % len(background_frames)
        screen.blit(background_frames[current_frame_idx], (0, 0))
    else:
        screen.fill((173,216,230))

def draw_snake(snake_body):
    for idx, block in enumerate(snake_body):
        color = (0,200,0) if idx == 0 else green
        pygame.draw.rect(screen, color, pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))

def render_text_centered(text, font_obj, color, y):
    surf = font_obj.render(text, True, color)
    x = (screen_width - surf.get_width()) // 2
    screen.blit(surf, (x, y))

def load_high_scores():
    if not os.path.exists(HIGH_SCORE_FILE): return []
    scores = []
    with open(HIGH_SCORE_FILE, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2: scores.append((parts[0], int(parts[1])))
    return scores

def get_high_score():
    scores = load_high_scores()
    return scores[0][1] if scores else 0

def is_new_highscore(score):
    scores = load_high_scores()
    return len(scores) < 10 or score > min(s[1] for s in scores)

def save_high_score(initials, score):
    scores = load_high_scores()
    scores.append((initials, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:10]
    with open(HIGH_SCORE_FILE, 'w') as f:
        for name, pts in scores: f.write(f"{name} {pts}\n")
def display_high_scores():
    while True:
        draw_background()
        render_text_centered("TOP 10 HIGH SCORES", font, white, 50)
        scores = load_high_scores()
        for i, (name, pts) in enumerate(scores):
            render_text_centered(f"{i+1}. {name} - {pts}", font, white, 100 + i * 30)
        render_text_centered("[B] Back", font, white, 500)
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_b:
                    return  # go back to menu


def cascade_new_high_score(initials, score):
    text_surf = large_font.render("NEW HIGH SCORE BY " + initials + " " + str(score), True, gold_color)
    time.sleep(1)
    x = (screen_width - text_surf.get_width()) // 2
    y, target_y = -text_surf.get_height(), (screen_height - text_surf.get_height()) // 2
    while y < target_y:
        draw_background()
        screen.blit(text_surf, (x, y))
        pygame.display.update()
        y += 10
        clock.tick(30)
    time.sleep(1)

def handle_highscore(score, initials):
    if is_new_highscore(score):
        save_high_score(initials, score)
        new_high_score_sound.play()
        cascade_new_high_score(initials, score)
        display_high_scores()

def get_initials():
    initials = ''
    while True:
        draw_background()
        render_text_centered("Enter 3-letter initials:", large_font, white, 200)
        render_text_centered(initials, large_font, white, 260)
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and len(initials) == 3: return initials
                elif ev.key == pygame.K_BACKSPACE: initials = initials[:-1]
                elif ev.unicode.isalpha() and len(initials) < 3: initials += ev.unicode.upper()

def cascade_you_lose(snake_body, food_pos, gold_food):
    text_surf = large_font.render("YOU LOSE", True, red)
    x = (screen_width - text_surf.get_width()) // 2
    y, target_y = -text_surf.get_height(), (screen_height - text_surf.get_height()) // 2
    while y < target_y:
        draw_background()
        draw_snake(snake_body)
        pygame.draw.rect(screen, titanium_white, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
        if gold_food: pygame.draw.rect(screen, gold_color, pygame.Rect(gold_food[0], gold_food[1], BLOCK_SIZE, BLOCK_SIZE))
        screen.blit(text_surf, (x, y))
        pygame.display.update()
        y += 10
        clock.tick(30)
    time.sleep(1)

def explode_tiles(tiles):
    sequence = [orange, red, dark_gray, light_gray, black]
    explosion_sound.play()
    for color in sequence:
        draw_background()
        for px, py in tiles:
            pygame.draw.rect(screen, color, pygame.Rect(px, py, BLOCK_SIZE, BLOCK_SIZE))
        pygame.display.update()
        pygame.time.delay(100)

def main():
    snake_pos = [BLOCK_SIZE * 5, BLOCK_SIZE * 5]
    snake_body = [list(snake_pos), [snake_pos[0]-BLOCK_SIZE, snake_pos[1]], [snake_pos[0]-2*BLOCK_SIZE, snake_pos[1]]]
    food_pos = [random.randrange(0, screen_width, BLOCK_SIZE), random.randrange(0, screen_height, BLOCK_SIZE)]
    gold_food, gold_spawn_time = None, 0
    gold_duration, next_gold_spawn = 5, time.time() + 10
    direction, change_to, speed, score = 'RIGHT', 'RIGHT', 15, 0
    initials, highscore = get_initials(), get_high_score()

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if is_new_highscore(score): handle_highscore(score, initials)
                return  # return to main_menu()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w and direction != 'DOWN': change_to = 'UP'
                if ev.key == pygame.K_s and direction != 'UP': change_to = 'DOWN'
                if ev.key == pygame.K_a and direction != 'RIGHT': change_to = 'LEFT'
                if ev.key == pygame.K_d and direction != 'LEFT': change_to = 'RIGHT'
                if ev.key in (pygame.K_PLUS, pygame.K_EQUALS): speed += 1
                if ev.key == pygame.K_MINUS and speed > 1: speed -= 1

        direction = change_to
        if direction == 'UP': snake_pos[1] -= BLOCK_SIZE
        if direction == 'DOWN': snake_pos[1] += BLOCK_SIZE
        if direction == 'LEFT': snake_pos[0] -= BLOCK_SIZE
        if direction == 'RIGHT': snake_pos[0] += BLOCK_SIZE
        snake_pos[0] %= screen_width
        snake_pos[1] %= screen_height
        snake_body.insert(0, list(snake_pos))

        ate = False
        if snake_pos == food_pos:
            score += 10
            score10_sound.play()
            food_pos = [random.randrange(0, screen_width, BLOCK_SIZE), random.randrange(0, screen_height, BLOCK_SIZE)]
            ate = True
        if gold_food and snake_pos == gold_food:
            beep_sound.stop(); explosion_sound.stop()
            score += 50
            score50_sound.play()
            gold_food, gold_spawn_time = None, 0
            ate = True
        if not ate: snake_body.pop()
        if snake_pos in snake_body[1:]:
            gameover_sound.play()
            cascade_you_lose(snake_body, food_pos, gold_food)
            if is_new_highscore(score): handle_highscore(score, initials)
            pygame.quit(); sys.exit()

        now = time.time()
        if not gold_food and now >= next_gold_spawn:
            gold_food = [random.randrange(0, screen_width, BLOCK_SIZE), random.randrange(0, screen_height, BLOCK_SIZE)]
            gold_spawn_time, next_gold_spawn = now, now + 10

        if gold_food:
            remaining = gold_duration - (now - gold_spawn_time)
            if remaining <= 2.5 and int(now * 4) % 4 == 0: beep_sound.play()
            if remaining <= 2.5 and int(remaining * 4) % 2 == 0: draw_background()

        if gold_food and now - gold_spawn_time > gold_duration:
            beep_sound.stop(); explosion_sound.play()
            affected = []
            for idx, part in enumerate(snake_body):
                dx, dy = abs(part[0]-gold_food[0])//BLOCK_SIZE, abs(part[1]-gold_food[1])//BLOCK_SIZE
                if dx <= BLAST_RADIUS and dy <= BLAST_RADIUS: affected.append((idx, part))
            if affected:
                affected.sort()
                indices, tiles = [i for i, _ in affected], [p for _, p in affected]
                explode_tiles(tiles)
                if indices[0] == 0:
                    head_shot_sound.play(); gameover_sound.play()
                    cascade_you_lose(snake_body, food_pos, gold_food)
                    if is_new_highscore(score): handle_highscore(score, initials)
                    pygame.quit(); sys.exit()
                else:
                    cut_len = len(snake_body) - indices[0]
                    score = max(score - cut_len * 10, 0)
                    body_cut_sound.play()
                    snake_body = snake_body[:indices[0]]
            gold_food, gold_spawn_time = None, 0

        draw_background()
        draw_snake(snake_body)
        pygame.draw.rect(screen, titanium_white, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
        if gold_food: pygame.draw.rect(screen, gold_color, pygame.Rect(gold_food[0], gold_food[1], BLOCK_SIZE, BLOCK_SIZE))
        hud = f"Score: {score}  Speed: {speed} High Score: {highscore}"
        screen.blit(font.render(hud, True, white), (10, 10))
        pygame.display.update()
        clock.tick(speed)
def main_menu():
    while True:
        draw_background()
        render_text_centered("SNAKE GAME", large_font, gold_color, 150)
        render_text_centered("[P] Play", font, white, 250)
        render_text_centered("[H] High Scores", font, white, 300)
        render_text_centered("[Q] Quit", font, white, 350)
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_p:
                    main()
                elif ev.key == pygame.K_h:
                    display_high_scores()
                elif ev.key == pygame.K_q:
                    pygame.quit(); sys.exit()

if __name__ == '__main__':
    main_menu()

"""
Geometry Dash — Simple Python Game
====================================
A simple Geometry Dash clone using pygame.

How to play:
  - Press SPACE or click the mouse to jump
  - Avoid the spikes!
  - Every spike you pass = +1 score

How to improve (ideas for you!):
  - Change PLAYER_COLOR to your favourite color
  - Change GRAVITY to make the jump higher or lower
  - Add a double-jump feature
  - Make the game faster over time
  - Add more obstacle shapes
  - Add sound effects with pygame.mixer
"""

import math
import random
import sys

import pygame
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS — change these to tweak the game!
# ─────────────────────────────────────────────────────────────────────────────

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
FPS = 60

# Colors  (Red, Green, Blue)  — values 0-255
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (30, 30, 50)       # dark blue-ish background
GROUND_COLOR = (80, 80, 120)
PLAYER_COLOR = (0, 200, 255)          # cyan — change this!
OBSTACLE_COLOR = (255, 80, 80)        # red spikes
SCORE_COLOR = (255, 255, 100)         # yellow text

GROUND_HEIGHT = 60                    # height of the ground strip at the bottom
GROUND_Y = WINDOW_HEIGHT - GROUND_HEIGHT  # y position of the ground top edge

# Player settings
PLAYER_SIZE = 40                      # square side length in pixels
PLAYER_X = 120                        # fixed horizontal position
JUMP_VELOCITY = -14                   # negative = upward  (try -10 to -18)
GRAVITY = 0.7                         # how fast the player falls (try 0.4 to 1.0)

# Obstacle settings
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 50
OBSTACLE_SPEED = 6                    # pixels per frame (increase for harder game)
OBSTACLE_MIN_GAP = 60                 # minimum frames between obstacles
OBSTACLE_MAX_GAP = 120                # maximum frames between obstacles

# Game mode settings
GAME_MODES = ("classic", "wave", "gravity")
HARDER_SPIKE_CHANCE = 0.35            # chance to create a second nearby spike
WAVE_OBSTACLE_AMPLITUDE = 80         # vertical movement amplitude for wave mode
WAVE_OBSTACLE_FREQUENCY = 0.02       # speed of vertical oscillation
GRAVITY_CHANGE_INTERVAL = 300        # frames (5 seconds at 60 FPS)
GRAVITY_MIN = 0.3
GRAVITY_MAX = 1.2

# shop settings
ICON_COLORS = [
    (0, 200, 255),   # default cyan
    (255, 100, 100), # red
    (100, 255, 100), # green
    (255, 255, 100), # yellow
    (255, 0, 255),   # magenta
]
UNLOCK_COST = 100

# Level settings
LEVELS = [
    {"name": "Level 1 - Easy", "speed": 5, "min_gap": 90, "max_gap": 150, "score_to_next": 9999, "block_chance": 0},
    {"name": "Level 2 - Medium", "speed": 7, "min_gap": 70, "max_gap": 120, "score_to_next": 9999, "block_chance": 0.05},
    {"name": "Level 3 - Hard", "speed": 11, "min_gap": 35, "max_gap": 65, "score_to_next": 9999, "block_chance": 0.1},
    {"name": "Level 4 - Insane Ride", "speed": 12, "min_gap": 25, "max_gap": 50, "score_to_next": 9999, "block_chance": 0.4},
]

# Editor settings
EDITOR_GRID_X = (100, WINDOW_WIDTH - 100)
EDITOR_GRID_Y = (GROUND_Y - 220, GROUND_Y - 40)
EDITOR_CELL_SIZE = 20
EDITOR_FRAMES_PER_PIXEL = 2


# ─────────────────────────────────────────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────────────────────────────────────────

class Player:
    """The player — a square that jumps over obstacles."""

    def __init__(self) -> None:
        self.x = PLAYER_X
        self.y = float(GROUND_Y - PLAYER_SIZE)
        self.velocity_y = 0.0
        self.on_ground = True
        self.angle = 0.0
        self.color = PLAYER_COLOR
        self.can_double_jump = False

    def reset(self) -> None:
        """Put the player back at the starting position."""
        self.x = PLAYER_X
        self.y = float(GROUND_Y - PLAYER_SIZE)
        self.velocity_y = 0.0
        self.on_ground = True
        self.can_double_jump = False
        self.angle = 0.0

    def jump(self) -> None:
        """Make the player jump (can jump on ground or double jump in the air)."""
        if self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False
            self.can_double_jump = True
        elif self.can_double_jump:
            self.velocity_y = JUMP_VELOCITY
            self.can_double_jump = False

    def update(self, gravity: float = GRAVITY) -> None:
        """Move the player each frame."""
        self.velocity_y += gravity
        self.y += self.velocity_y

        if not self.on_ground:
            self.angle -= 5

        if self.y >= GROUND_Y - PLAYER_SIZE:
            self.y = float(GROUND_Y - PLAYER_SIZE)
            self.velocity_y = 0.0
            self.on_ground = True
            self.can_double_jump = False
            self.angle = 0.0

    def get_rect(self) -> pygame.Rect:
        """Return the collision box (slightly smaller for fairness)."""
        margin = 4
        return pygame.Rect(
            self.x + margin,
            int(self.y) + margin,
            PLAYER_SIZE - margin * 2,
            PLAYER_SIZE - margin * 2,
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the spinning cube on screen."""
        cube_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(cube_surf, self.color, (0, 0, PLAYER_SIZE, PLAYER_SIZE), border_radius=4)
        pygame.draw.line(cube_surf, WHITE, (PLAYER_SIZE // 2, 4), (PLAYER_SIZE // 2, PLAYER_SIZE - 4), 2)
        pygame.draw.line(cube_surf, WHITE, (4, PLAYER_SIZE // 2), (PLAYER_SIZE - 4, PLAYER_SIZE // 2), 2)
        rotated = pygame.transform.rotate(cube_surf, self.angle)
        rect = rotated.get_rect(center=(self.x + PLAYER_SIZE // 2, int(self.y) + PLAYER_SIZE // 2))
        screen.blit(rotated, rect)


# ─────────────────────────────────────────────────────────────────────────────
# OBSTACLE (spike)
# ─────────────────────────────────────────────────────────────────────────────

class Obstacle:
    """A spike that scrolls from right to left."""

    def __init__(self, x: int, base_y: int = GROUND_Y, width: int = OBSTACLE_WIDTH, height: int = OBSTACLE_HEIGHT) -> None:
        self.x = x
        self.base_y = base_y
        self.width = width
        self.height = height
        self.passed = False
        self.speed = OBSTACLE_SPEED

    def update(self) -> None:
        """Move the obstacle to the left."""
        self.x -= self.speed

    def is_offscreen(self) -> bool:
        """True if the obstacle has scrolled past the left edge."""
        return self.x + self.width < 0

    def get_rect(self) -> pygame.Rect:
        """Return the collision box (the lower 60% of the spike for fairness)."""
        margin_x = 4
        return pygame.Rect(
            self.x + margin_x,
            self.base_y - int(self.height * 0.6),
            self.width - margin_x * 2,
            int(self.height * 0.6),
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Draw a triangle spike."""
        tip = (self.x + self.width // 2, self.base_y - self.height)
        bottom_left = (self.x, self.base_y)
        bottom_right = (self.x + self.width, self.base_y)
        pygame.draw.polygon(screen, OBSTACLE_COLOR, [tip, bottom_left, bottom_right])
        pygame.draw.polygon(screen, BLACK, [tip, bottom_left, bottom_right], 2)


class WaveObstacle(Obstacle):
    """Dynamic wave spike for wave mode."""

    def __init__(self, x: int, phase: float) -> None:
        super().__init__(x)
        self.phase = phase

    def update(self) -> None:
        self.x -= OBSTACLE_SPEED
        self.phase += WAVE_OBSTACLE_FREQUENCY
        self.base_y = GROUND_Y - int(WAVE_OBSTACLE_AMPLITUDE * (0.5 + 0.5 * math.sin(self.phase)))

    def draw(self, screen: pygame.Surface) -> None:
        tip = (self.x + self.width // 2, self.base_y - self.height)
        bottom_left = (self.x, self.base_y)
        bottom_right = (self.x + self.width, self.base_y)
        pygame.draw.polygon(screen, (170, 220, 255), [tip, bottom_left, bottom_right])
        pygame.draw.polygon(screen, BLACK, [tip, bottom_left, bottom_right], 2)

    def get_rect(self) -> pygame.Rect:
        margin_x = 4
        return pygame.Rect(
            self.x + margin_x,
            self.base_y - int(self.height * 0.6),
            self.width - margin_x * 2,
            int(self.height * 0.6),
        )


# ─────────────────────────────────────────────────────────────────────────────
# SCROLLING BACKGROUND LINES
# ─────────────────────────────────────────────────────────────────────────────

class Background:
    """Simple scrolling lines to give a sense of speed."""

    def __init__(self) -> None:
        self.lines: list[int] = list(range(0, WINDOW_WIDTH + 200, 200))

    def update(self) -> None:
        self.lines = [(x - OBSTACLE_SPEED) % (WINDOW_WIDTH + 200) for x in self.lines]

    def draw(self, screen: pygame.Surface) -> None:
        for x in self.lines:
            pygame.draw.line(screen, (50, 50, 80), (x - 200, 0), (x, GROUND_Y), 1)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def draw_text(
    screen: pygame.Surface,
    text: str,
    size: int,
    x: int,
    y: int,
    color: tuple[int, int, int] = WHITE,
    center: bool = False,
) -> None:
    """Draw text on screen."""
    font = pygame.font.SysFont("Arial", size, bold=True)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)


def generate_death_sound() -> pygame.mixer.Sound:
    """Generate a simple descending death sound."""
    sample_rate = 22050
    duration = 0.5  # seconds
    frequency_start = 800  # Hz
    frequency_end = 200  # Hz
    samples = int(sample_rate * duration)
    
    sound_array = np.zeros(samples, dtype=np.int16)
    for i in range(samples):
        # Descending frequency over time
        t = i / sample_rate
        freq = frequency_start - (frequency_start - frequency_end) * (t / duration)
        # Generate sine wave with fade out
        amplitude = 32767 * (1 - t / duration)
        sound_array[i] = int(amplitude * np.sin(2 * np.pi * freq * t))
    
    sound = pygame.mixer.Sound(buffer=sound_array.tobytes())
    return sound


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────────────────────────────────────

def run_game() -> None:
    """Launch and run the Geometry Dash game."""
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Geometry Dash")
    clock = pygame.time.Clock()
    
    death_sound = generate_death_sound()

    player = Player()
    background = Background()
    obstacles: list[Obstacle] = []
    score = 0
    coins = 0
    high_score = 0
    current_level = 0
    selected_level = 0
    frames_until_next = LEVELS[current_level]["min_gap"]
    game_over = False
    started = False
    game_state = "menu"  # menu, level_select, playing, shop, editor, profile, level_complete, gameover
    mode = "classic"  # toggle between classic and wave mode
    selected_icon = 0
    unlocked_icons = {0}
    editor_objects: list[dict[str, int|str]] = []
    editor_cursor = [EDITOR_GRID_X[0], EDITOR_GRID_Y[0]]
    custom_mode = False
    custom_events: list[dict[str, int|str]] = []
    custom_timer = 0
    current_speed = OBSTACLE_SPEED
    player_name = "Player"
    stars = 0
    stars_per_level = {0: 0, 1: 0, 2: 0, 3: 0}  # Track stars earned per level
    beaten_levels = set()
    gravity_change_timer = 0
    current_gravity = GRAVITY
    death_position = None
    
    # Star rewards per level when beaten
    STARS_FOR_LEVEL = {0: 2, 1: 4, 2: 5, 3: 8}  # Level index -> stars for beating it

    def reset() -> None:
        nonlocal obstacles, score, frames_until_next, game_over, started, current_level, game_state, custom_mode, custom_events, custom_timer, current_speed, gravity_change_timer, current_gravity, death_position, stars, stars_per_level, beaten_levels
        player.reset()
        obstacles = []
        score = 0
        current_level = 0
        frames_until_next = LEVELS[current_level]["min_gap"]
        game_over = False
        started = False
        game_state = "menu"
        custom_mode = False
        custom_events = []
        custom_timer = 0
        current_speed = OBSTACLE_SPEED
        gravity_change_timer = 0
        current_gravity = GRAVITY
        death_position = None

    while True:
        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                current_idx = GAME_MODES.index(mode)
                mode = GAME_MODES[(current_idx + 1) % len(GAME_MODES)]
                gravity_change_timer = 0
                current_gravity = GRAVITY

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and game_state == "menu":
                game_state = "level_select"
                selected_level = 0

            if event.type == pygame.KEYDOWN and event.key == pygame.K_p and game_state == "menu":
                game_state = "profile"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e and game_state == "menu":
                game_state = "level_select"
                selected_level = 0

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s and game_state == "menu":
                game_state = "shop"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_c and game_state == "menu":
                game_state = "editor"
                editor_cursor = [EDITOR_GRID_X[0], EDITOR_GRID_Y[0]]

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and game_state in {"shop", "editor", "level_select", "profile"}:
                game_state = "menu"

            if event.type == pygame.KEYDOWN and game_state == "level_select":
                if event.key == pygame.K_LEFT:
                    selected_level = (selected_level - 1) % len(LEVELS)
                if event.key == pygame.K_RIGHT:
                    selected_level = (selected_level + 1) % len(LEVELS)
                if event.key == pygame.K_RETURN:
                    game_state = "playing"
                    started = True
                    player.reset()
                    obstacles = []
                    score = 0
                    current_level = selected_level
                    frames_until_next = LEVELS[current_level]["min_gap"]
                    current_level = selected_level
                    frames_until_next = LEVELS[current_level]["min_gap"]

            if event.type == pygame.KEYDOWN and game_state == "editor":
                if event.key == pygame.K_RIGHT:
                    editor_cursor[0] = min(EDITOR_GRID_X[1], editor_cursor[0] + EDITOR_CELL_SIZE)
                if event.key == pygame.K_LEFT:
                    editor_cursor[0] = max(EDITOR_GRID_X[0], editor_cursor[0] - EDITOR_CELL_SIZE)
                if event.key == pygame.K_UP:
                    editor_cursor[1] = max(EDITOR_GRID_Y[0], editor_cursor[1] - EDITOR_CELL_SIZE)
                if event.key == pygame.K_DOWN:
                    editor_cursor[1] = min(EDITOR_GRID_Y[1], editor_cursor[1] + EDITOR_CELL_SIZE)

                if event.key == pygame.K_1:
                    # spike event: spawn at time based on x position
                    spawn_time = int((editor_cursor[0] - EDITOR_GRID_X[0]) * EDITOR_FRAMES_PER_PIXEL)
                    editor_objects.append({"type": "spike", "spawn_time": spawn_time, "y": editor_cursor[1]})
                if event.key == pygame.K_2:
                    spawn_time = int((editor_cursor[0] - EDITOR_GRID_X[0]) * EDITOR_FRAMES_PER_PIXEL)
                    editor_objects.append({"type": "block", "spawn_time": spawn_time, "y": editor_cursor[1]})
                if event.key == pygame.K_3:
                    spawn_time = int((editor_cursor[0] - EDITOR_GRID_X[0]) * EDITOR_FRAMES_PER_PIXEL)
                    editor_objects.append({"type": "speed", "spawn_time": spawn_time, "speed": max(3, current_speed + 2)})
                if event.key == pygame.K_d:
                    editor_objects = [obj for obj in editor_objects if not (obj["spawn_time"] == int((editor_cursor[0] - EDITOR_GRID_X[0]) * EDITOR_FRAMES_PER_PIXEL) and abs(obj.get("y", GROUND_Y) - editor_cursor[1]) <= 10)]
                if event.key == pygame.K_r:
                    game_state = "menu"
                if event.key == pygame.K_p or event.key == pygame.K_RETURN:
                    if editor_objects:
                        game_state = "playing"
                        started = True
                        player.reset()
                        obstacles = []
                        score = 0
                        current_level = selected_level
                        frames_until_next = LEVELS[current_level]["min_gap"]
                        custom_mode = True
                        custom_timer = 0
                        custom_events = sorted(editor_objects, key=lambda o: o["spawn_time"])
                        current_speed = OBSTACLE_SPEED

            jump = (
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
                or event.type == pygame.MOUSEBUTTONDOWN
            )
            if jump and game_state == "playing":
                started = True
                player.jump()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_state == "gameover":
                # Restart the same level
                player.reset()
                obstacles = []
                score = 0
                current_level = selected_level
                frames_until_next = LEVELS[current_level]["min_gap"]
                game_over = False
                started = False
                game_state = "playing"
                gravity_change_timer = 0
                current_gravity = GRAVITY
                death_position = None
            elif jump and game_state == "gameover":
                game_state = "menu"
                reset()

        # ── Update ────────────────────────────────────────────────────────────
        if started and not game_over and game_state == "playing":
            # Handle gravity changes in gravity mode
            if mode == "gravity":
                gravity_change_timer += 1
                if gravity_change_timer >= GRAVITY_CHANGE_INTERVAL:
                    current_gravity = random.uniform(GRAVITY_MIN, GRAVITY_MAX)
                    gravity_change_timer = 0
            else:
                current_gravity = GRAVITY
            
            player.update(current_gravity)
            background.update()

            if custom_mode:
                custom_timer += 1
                while custom_events and custom_events[0]["spawn_time"] <= custom_timer:
                    event_obj = custom_events.pop(0)
                    if event_obj["type"] == "speed":
                        current_speed = event_obj.get("speed", current_speed)
                        continue

                    if event_obj["type"] == "spike":
                        obs = Obstacle(WINDOW_WIDTH + 10, base_y=event_obj.get("y", GROUND_Y))
                    else:
                        obs = Obstacle(WINDOW_WIDTH + 10, base_y=event_obj.get("y", GROUND_Y), width=OBSTACLE_WIDTH*2, height=OBSTACLE_HEIGHT//2)

                    if mode == "wave":
                        wave_obs = WaveObstacle(obs.x, random.random() * 2 * math.pi)
                        wave_obs.base_y = obs.base_y
                        wave_obs.speed = current_speed
                        obstacles.append(wave_obs)
                    else:
                        obs.speed = current_speed
                        obstacles.append(obs)

                # stop if the map is done
                if not custom_events and not obstacles:
                    game_over = True
                    game_state = "gameover"
                    death_sound.play()
                    if score > high_score:
                        high_score = score

            else:
                level = LEVELS[current_level]
                current_speed = level["speed"]
                frames_until_next -= 1
                if frames_until_next <= 0:
                    def make_obs() -> Obstacle:
                        if mode == "wave":
                            wave_obs = WaveObstacle(WINDOW_WIDTH + 10, random.random() * 2 * math.pi)
                            wave_obs.speed = level["speed"]
                            return wave_obs
                        
                        # Decide if this should be a block or spike based on level difficulty
                        is_block = random.random() < level.get("block_chance", 0)
                        if is_block:
                            base = Obstacle(WINDOW_WIDTH + 10, width=OBSTACLE_WIDTH*2, height=OBSTACLE_HEIGHT//2)
                        else:
                            base = Obstacle(WINDOW_WIDTH + 10)
                        base.speed = level["speed"]
                        return base

                    first = make_obs()
                    obstacles.append(first)

                    if random.random() < HARDER_SPIKE_CHANCE:
                        extra = make_obs()
                        extra.x = WINDOW_WIDTH + 10 + OBSTACLE_WIDTH + 10
                        obstacles.append(extra)

                    frames_until_next = random.randint(level["min_gap"], level["max_gap"])

            for obs in obstacles:
                obs.update()
                if not obs.passed and obs.x + obs.width < player.x:
                    obs.passed = True
                    score += 1
                    coins += 1
                    if not custom_mode and score >= level["score_to_next"] and current_level + 1 < len(LEVELS):
                        current_level += 1

                if player.get_rect().colliderect(obs.get_rect()):
                    death_position = (player.x, player.y)
                    game_over = True
                    game_state = "gameover"
                    death_sound.play()
                    if score > high_score:
                        high_score = score
                    
                    # Award stars for beating the level (if not in custom mode and haven't beaten this level yet)
                    if not custom_mode and current_level not in beaten_levels and not custom_mode:
                        beaten_levels.add(current_level)
                        stars_per_level[current_level] = STARS_FOR_LEVEL.get(current_level, 0)
                        stars = sum(stars_per_level.values())

            obstacles = [o for o in obstacles if not o.is_offscreen()]

        # Ensure selected player's cube color is applied
        player.color = ICON_COLORS[selected_icon]

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BACKGROUND_COLOR)
        background.draw(screen)

        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WINDOW_WIDTH, GROUND_HEIGHT))
        pygame.draw.line(screen, (120, 120, 180), (0, GROUND_Y), (WINDOW_WIDTH, GROUND_Y), 2)

        for obs in obstacles:
            obs.draw(screen)

        player.draw(screen)

        if game_state == "menu":
            draw_text(screen, "GEOMETRY DASH", 60, WINDOW_WIDTH // 2, 100, PLAYER_COLOR, center=True)
            draw_text(screen, "Press ENTER to Play, P for Profile, E for Levels", 28, WINDOW_WIDTH // 2, 170, WHITE, center=True)
            draw_text(screen, "S for Shop, C for Create, M to toggle mode", 22, WINDOW_WIDTH // 2, 210, WHITE, center=True)
            draw_text(screen, f"Mode: {mode.upper()} (press M to cycle)", 20, WINDOW_WIDTH // 2, 260, (180, 180, 180), center=True)
            draw_text(screen, f"Coins: {coins}", 20, WINDOW_WIDTH // 2, 290, (180, 255, 180), center=True)

        elif game_state == "level_select":
            draw_text(screen, "SELECT LEVEL", 56, WINDOW_WIDTH // 2, 80, SCORE_COLOR, center=True)
            for idx, lvl in enumerate(LEVELS):
                color = SCORE_COLOR if idx == selected_level else (180, 180, 180)
                draw_text(screen, f"{idx+1} - {lvl['name']}", 40, WINDOW_WIDTH // 2, 160 + idx*50, color, center=True)
            draw_text(screen, "Use LEFT/RIGHT to choose, ENTER to play, ESC to menu", 20, WINDOW_WIDTH // 2, 320, WHITE, center=True)

        elif game_state == "profile":
            draw_text(screen, "PROFILE", 56, WINDOW_WIDTH // 2, 80, SCORE_COLOR, center=True)
            draw_text(screen, f"Name: {player_name}", 32, WINDOW_WIDTH // 2, 150, WHITE, center=True)
            
            # Show current icon
            icon_size = 60
            icon_x = WINDOW_WIDTH // 2 - icon_size // 2
            pygame.draw.rect(screen, ICON_COLORS[selected_icon], (icon_x, 220, icon_size, icon_size), border_radius=8)
            draw_text(screen, "Current Icon", 18, WINDOW_WIDTH // 2, 290, (180, 180, 180), center=True)
            
            draw_text(screen, f"★ Stars: {stars}", 32, WINDOW_WIDTH // 2, 330, SCORE_COLOR, center=True)
            draw_text(screen, f"Coins: {coins}", 24, WINDOW_WIDTH // 2, 370, (180, 255, 180), center=True)
            draw_text(screen, "Press ESC to return to menu", 20, WINDOW_WIDTH // 2, 370, WHITE, center=True)

        elif game_state == "shop":
            draw_text(screen, "SHOP", 56, WINDOW_WIDTH // 2, 70, SCORE_COLOR, center=True)
            draw_text(screen, f"Coins: {coins}", 32, WINDOW_WIDTH - 190, 20, SCORE_COLOR)
            draw_text(screen, "Use LEFT/RIGHT to select icon, U to unlock, ESC to menu", 20, WINDOW_WIDTH // 2, 110, WHITE, center=True)

            icon_y = 180
            for i, col in enumerate(ICON_COLORS):
                x = 120 + i * 120
                pygame.draw.rect(screen, col, (x, icon_y, 80, 80), border_radius=10)
                if i == selected_icon:
                    pygame.draw.rect(screen, WHITE, (x - 6, icon_y - 6, 92, 92), 3, border_radius=14)

                status = "OWNED" if i in unlocked_icons else f"{UNLOCK_COST} COINS"
                status_color = SCORE_COLOR if i in unlocked_icons else (255, 180, 180)
                draw_text(screen, status, 16, x + 40, icon_y + 92, status_color, center=True)

            sel_text = "Selected: {}".format("Owned" if selected_icon in unlocked_icons else "Locked")
            draw_text(screen, sel_text, 22, WINDOW_WIDTH // 2, 280, WHITE, center=True)
            if selected_icon in unlocked_icons:
                draw_text(screen, "Press P or ENTER to return to menu", 20, WINDOW_WIDTH // 2, 320, (180, 255, 180), center=True)
            else:
                draw_text(screen, f"Press U to unlock this cube for {UNLOCK_COST} coins", 20, WINDOW_WIDTH // 2, 320, (255, 220, 220), center=True)

        elif game_state == "editor":
            draw_text(screen, "LEVEL EDITOR", 56, WINDOW_WIDTH // 2, 70, SCORE_COLOR, center=True)
            draw_text(screen, "Arrows to move cursor, 1 spike, 2 block, 3 speed, D delete", 20, WINDOW_WIDTH // 2, 120, WHITE, center=True)
            draw_text(screen, "P/ENTER to play custom level, ESC/R to menu", 20, WINDOW_WIDTH // 2, 150, WHITE, center=True)
            draw_text(screen, f"Cursor: ({editor_cursor[0]}, {editor_cursor[1]})", 18, 120, 200, SCORE_COLOR)
            draw_text(screen, f"Editor objects: {len(editor_objects)}", 18, 120, 220, SCORE_COLOR)

            # draw editor placement grid and objects
            for x in range(EDITOR_GRID_X[0], EDITOR_GRID_X[1] + 1, EDITOR_CELL_SIZE):
                pygame.draw.line(screen, (80, 80, 100), (x, EDITOR_GRID_Y[0]), (x, EDITOR_GRID_Y[1]), 1)
            for y in range(EDITOR_GRID_Y[0], EDITOR_GRID_Y[1] + 1, EDITOR_CELL_SIZE):
                pygame.draw.line(screen, (80, 80, 100), (EDITOR_GRID_X[0], y), (EDITOR_GRID_X[1], y), 1)

            pygame.draw.circle(screen, (255, 255, 255), editor_cursor, 6)
            for obj in editor_objects:
                px = EDITOR_GRID_X[0] + int(obj["spawn_time"] / EDITOR_FRAMES_PER_PIXEL)
                py = obj.get("y", GROUND_Y)
                if obj["type"] == "spike":
                    pygame.draw.polygon(screen, OBSTACLE_COLOR, [(px, py), (px-10, py+20), (px+10, py+20)])
                elif obj["type"] == "block":
                    pygame.draw.rect(screen, (200, 200, 200), (px-15, py, 30, 20))
                elif obj["type"] == "speed":
                    pygame.draw.circle(screen, (255, 200, 0), (px, py), 8)

        else:
            draw_text(screen, f"Score: {score}", 28, 16, 16, SCORE_COLOR)
            draw_text(screen, f"Coins: {coins}", 20, 16, 50, (180, 255, 180))
            draw_text(screen, f"Best:  {high_score}", 20, 16, 80, (180, 180, 100))
            draw_text(screen, f"Mode: {mode.upper()} (press M to switch)", 20, 16, 110, (180, 180, 180))
            draw_text(screen, f"Level: {LEVELS[current_level]['name']}", 20, 16, 140, (200, 200, 255))
            
            if mode == "gravity" and game_state == "playing":
                draw_text(screen, f"Gravity: {current_gravity:.2f}", 18, 16, 170, (255, 180, 100))

            if game_state == "gameover":
                if death_position:
                    pygame.draw.rect(screen, (255, 0, 0), (int(death_position[0]) - 20, int(death_position[1]) - 20, 40, 40))
                draw_text(screen, "GAME OVER", 56, WINDOW_WIDTH // 2, 140, OBSTACLE_COLOR, center=True)
                draw_text(screen, f"Score: {score}   Best: {high_score}", 30, WINDOW_WIDTH // 2, 210, SCORE_COLOR, center=True)
                draw_text(screen, "Press R to retry level, SPACE/click to menu", 24, WINDOW_WIDTH // 2, 260, WHITE, center=True)

        pygame.display.flip()
        clock.tick(FPS)


def main() -> None:
    """Entry point."""
    run_game()


if __name__ == "__main__":
    main()

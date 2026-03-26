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
GAME_MODES = ("classic", "wave")
HARDER_SPIKE_CHANCE = 0.35            # chance to create a second nearby spike
WAVE_OBSTACLE_AMPLITUDE = 80         # vertical movement amplitude for wave mode
WAVE_OBSTACLE_FREQUENCY = 0.02       # speed of vertical oscillation

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
    {"name": "Easy", "speed": 5, "min_gap": 80, "max_gap": 140, "score_to_next": 10},
    {"name": "Medium", "speed": 7, "min_gap": 70, "max_gap": 120, "score_to_next": 20},
    {"name": "Hard", "speed": 9, "min_gap": 55, "max_gap": 100, "score_to_next": 30},
    {"name": "Insane", "speed": 11, "min_gap": 45, "max_gap": 90, "score_to_next": 9999},
]


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

    def reset(self) -> None:
        """Put the player back at the starting position."""
        self.x = PLAYER_X
        self.y = float(GROUND_Y - PLAYER_SIZE)
        self.velocity_y = 0.0
        self.on_ground = True
        self.angle = 0.0

    def jump(self) -> None:
        """Make the player jump (only if standing on the ground)."""
        if self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False

    def update(self) -> None:
        """Move the player each frame."""
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

        if not self.on_ground:
            self.angle -= 5

        if self.y >= GROUND_Y - PLAYER_SIZE:
            self.y = float(GROUND_Y - PLAYER_SIZE)
            self.velocity_y = 0.0
            self.on_ground = True
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

    def __init__(self, x: int) -> None:
        self.x = x
        self.base_y = GROUND_Y
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
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


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────────────────────────────────────

def run_game() -> None:
    """Launch and run the Geometry Dash game."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Geometry Dash")
    clock = pygame.time.Clock()

    player = Player()
    background = Background()
    obstacles: list[Obstacle] = []
    score = 0
    high_score = 0
    current_level = 0
    frames_until_next = LEVELS[current_level]["min_gap"]
    game_over = False
    started = False
    game_state = "menu"  # menu, playing, shop, gameover
    mode = "classic"  # toggle between classic and wave mode
    selected_icon = 0
    unlocked_icons = {0}

    def reset() -> None:
        nonlocal obstacles, score, frames_until_next, game_over, started, current_level, game_state
        player.reset()
        obstacles = []
        score = 0
        current_level = 0
        frames_until_next = LEVELS[current_level]["min_gap"]
        game_over = False
        started = False
        game_state = "menu"

    while True:
        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                mode = "wave" if mode == "classic" else "classic"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and game_state == "menu":
                game_state = "playing"
                started = True
                player.reset()
                obstacles = []
                score = 0
                current_level = 0
                frames_until_next = LEVELS[current_level]["min_gap"]

            if event.type == pygame.KEYDOWN and event.key == pygame.K_p and game_state == "menu":
                # Play from menu via P
                game_state = "playing"
                started = True
                player.reset()
                obstacles = []
                score = 0
                current_level = 0
                frames_until_next = LEVELS[current_level]["min_gap"]

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s and game_state == "menu":
                game_state = "shop"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and game_state == "shop":
                game_state = "menu"

            if event.type == pygame.KEYDOWN and game_state == "shop":
                if event.key == pygame.K_RIGHT:
                    selected_icon = (selected_icon + 1) % len(ICON_COLORS)
                if event.key == pygame.K_LEFT:
                    selected_icon = (selected_icon - 1) % len(ICON_COLORS)
                if event.key == pygame.K_u:
                    if selected_icon not in unlocked_icons and score >= UNLOCK_COST:
                        unlocked_icons.add(selected_icon)
                        score -= UNLOCK_COST
                if event.key == pygame.K_RETURN or event.key == pygame.K_p:
                    game_state = "menu"

            jump = (
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
                or event.type == pygame.MOUSEBUTTONDOWN
            )
            if jump and game_state == "playing":
                started = True
                player.jump()

            if jump and game_state == "gameover":
                game_state = "menu"
                reset()

        # ── Update ────────────────────────────────────────────────────────────
        if started and not game_over and game_state == "playing":
            player.update()
            background.update()

            level = LEVELS[current_level]
            OBSTACLE_SPEED = level["speed"]  # type: ignore[assignment]
            frames_until_next -= 1
            if frames_until_next <= 0:
                def make_obs() -> Obstacle:
                    if mode == "wave":
                        wave_obs = WaveObstacle(WINDOW_WIDTH + 10, random.random() * 2 * math.pi)
                        wave_obs.speed = level["speed"]
                        return wave_obs
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
                    if score >= level["score_to_next"] and current_level + 1 < len(LEVELS):
                        current_level += 1

                if player.get_rect().colliderect(obs.get_rect()):
                    game_over = True
                    game_state = "gameover"
                    if score > high_score:
                        high_score = score

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
            draw_text(screen, "Press ENTER or P to Play", 32, WINDOW_WIDTH // 2, 180, WHITE, center=True)
            draw_text(screen, "Press S for Shop", 26, WINDOW_WIDTH // 2, 220, WHITE, center=True)
            draw_text(screen, "Press M to toggle mode", 22, WINDOW_WIDTH // 2, 260, (180, 180, 180), center=True)
            draw_text(screen, f"Current level: {LEVELS[current_level]['name']}", 24, WINDOW_WIDTH // 2, 300, SCORE_COLOR, center=True)
            draw_text(screen, f"Mode: {mode.upper()}", 20, WINDOW_WIDTH // 2, 340, (180, 180, 180), center=True)

        elif game_state == "shop":
            draw_text(screen, "SHOP", 56, WINDOW_WIDTH // 2, 70, SCORE_COLOR, center=True)
            draw_text(screen, f"Score: {score}", 32, WINDOW_WIDTH - 190, 20, SCORE_COLOR)
            draw_text(screen, "Use LEFT/RIGHT to select icon, U to unlock, ESC to menu", 20, WINDOW_WIDTH // 2, 110, WHITE, center=True)

            icon_y = 180
            for i, col in enumerate(ICON_COLORS):
                x = 120 + i * 120
                pygame.draw.rect(screen, col, (x, icon_y, 80, 80), border_radius=10)
                if i == selected_icon:
                    pygame.draw.rect(screen, WHITE, (x - 6, icon_y - 6, 92, 92), 3, border_radius=14)

                status = "OWNED" if i in unlocked_icons else f"{UNLOCK_COST} SCORE"
                status_color = SCORE_COLOR if i in unlocked_icons else (255, 180, 180)
                draw_text(screen, status, 16, x + 40, icon_y + 92, status_color, center=True)

            sel_text = "Selected: {}".format("Owned" if selected_icon in unlocked_icons else "Locked")
            draw_text(screen, sel_text, 22, WINDOW_WIDTH // 2, 280, WHITE, center=True)
            if selected_icon in unlocked_icons:
                draw_text(screen, "Press P or ENTER to return to menu and play", 20, WINDOW_WIDTH // 2, 320, (180, 255, 180), center=True)
            else:
                draw_text(screen, f"Press U to unlock this cube for {UNLOCK_COST} score", 20, WINDOW_WIDTH // 2, 320, (255, 220, 220), center=True)

        else:
            draw_text(screen, f"Score: {score}", 28, 16, 16, SCORE_COLOR)
            draw_text(screen, f"Best:  {high_score}", 20, 16, 50, (180, 180, 100))
            draw_text(screen, f"Mode: {mode.upper()} (press M to switch)", 20, 16, 80, (180, 180, 180))
            draw_text(screen, f"Level: {LEVELS[current_level]['name']}", 20, 16, 110, (200, 200, 255))

            if game_state == "gameover":
                draw_text(screen, "GAME OVER", 56, WINDOW_WIDTH // 2, 140, OBSTACLE_COLOR, center=True)
                draw_text(screen, f"Score: {score}   Best: {high_score}", 30, WINDOW_WIDTH // 2, 210, SCORE_COLOR, center=True)
                draw_text(screen, "Press SPACE or click to return to menu", 24, WINDOW_WIDTH // 2, 260, WHITE, center=True)

        pygame.display.flip()
        clock.tick(FPS)


def main() -> None:
    """Entry point."""
    run_game()


if __name__ == "__main__":
    main()

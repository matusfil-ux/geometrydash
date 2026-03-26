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
        pygame.draw.rect(cube_surf, PLAYER_COLOR, (0, 0, PLAYER_SIZE, PLAYER_SIZE), border_radius=4)
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

    def update(self) -> None:
        """Move the obstacle to the left."""
        self.x -= OBSTACLE_SPEED

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
    frames_until_next = OBSTACLE_MIN_GAP
    game_over = False
    started = False

    def reset() -> None:
        nonlocal obstacles, score, frames_until_next, game_over, started
        player.reset()
        obstacles = []
        score = 0
        frames_until_next = OBSTACLE_MIN_GAP
        game_over = False
        started = False

    while True:
        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            jump = (
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
                or event.type == pygame.MOUSEBUTTONDOWN
            )
            if jump:
                if game_over:
                    reset()
                else:
                    started = True
                    player.jump()

        # ── Update ────────────────────────────────────────────────────────────
        if started and not game_over:
            player.update()
            background.update()

            frames_until_next -= 1
            if frames_until_next <= 0:
                obstacles.append(Obstacle(WINDOW_WIDTH + 10))
                frames_until_next = random.randint(OBSTACLE_MIN_GAP, OBSTACLE_MAX_GAP)

            for obs in obstacles:
                obs.update()
                if not obs.passed and obs.x + obs.width < player.x:
                    obs.passed = True
                    score += 1
                if player.get_rect().colliderect(obs.get_rect()):
                    game_over = True
                    if score > high_score:
                        high_score = score

            obstacles = [o for o in obstacles if not o.is_offscreen()]

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BACKGROUND_COLOR)
        background.draw(screen)

        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WINDOW_WIDTH, GROUND_HEIGHT))
        pygame.draw.line(screen, (120, 120, 180), (0, GROUND_Y), (WINDOW_WIDTH, GROUND_Y), 2)

        for obs in obstacles:
            obs.draw(screen)

        player.draw(screen)

        draw_text(screen, f"Score: {score}", 28, 16, 16, SCORE_COLOR)
        draw_text(screen, f"Best:  {high_score}", 20, 16, 50, (180, 180, 100))

        if not started and not game_over:
            draw_text(screen, "GEOMETRY DASH", 48, WINDOW_WIDTH // 2, 140, PLAYER_COLOR, center=True)
            draw_text(screen, "Press SPACE or click to start", 26, WINDOW_WIDTH // 2, 210, WHITE, center=True)
            draw_text(screen, "Jump over the red spikes!", 22, WINDOW_WIDTH // 2, 250, (180, 180, 180), center=True)

        if game_over:
            draw_text(screen, "GAME OVER", 56, WINDOW_WIDTH // 2, 140, OBSTACLE_COLOR, center=True)
            draw_text(screen, f"Score: {score}   Best: {high_score}", 30, WINDOW_WIDTH // 2, 210, SCORE_COLOR, center=True)
            draw_text(screen, "Press SPACE or click to restart", 24, WINDOW_WIDTH // 2, 260, WHITE, center=True)

        pygame.display.flip()
        clock.tick(FPS)


def main() -> None:
    """Entry point."""
    run_game()


if __name__ == "__main__":
    main()

"""
Geometry Dash — Pygame Version
================================
Features:
  - Player name entry  (shown on leaderboard)
  - 5 levels with increasing speed / gap difficulty
  - Animated starfield background
  - Glowing player cube with rotation
  - Particle trail + explosion on death
  - Floating coins you can collect mid-air
  - Animated spikes with outline glow
  - Leaderboard saved to  ~/.geometrydash_scores.json
  - HUD: score, coins, best, time-bar
  - Full screen support (toggle with F)

── HOW TO IMPROVE ──────────────────────────────────────────────────────────────
  * PLAYER_COLORS   – add your own colour for each player
  * GRAVITY / JUMP  – tweak the jump feel
  * LEVELS          – add more levels, change speed / gap
  * Add double-jump: increase MAX_JUMPS
  * Add a new obstacle shape in _draw_obstacles()
  * Add background music: put an .mp3 next to this file and
    call pygame.mixer.music.load("music.mp3") + .play(-1)
────────────────────────────────────────────────────────────────────────────────
"""

import json
import math
import os
import random
import sys
from pathlib import Path

import pygame

# ── CONFIG ───────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 500
FPS           = 60
TITLE         = "Geometry Dash 🎮"

SCORES_FILE   = Path.home() / ".geometrydash_scores.json"

# Physics (try changing these!)
GRAVITY       = 0.7      # pixels/frame²  – bigger = heavier
JUMP_VEL      = -15.0    # pixels/frame   – more negative = higher
MAX_JUMPS     = 2        # 1 = single, 2 = double-jump

# Player square
PLAYER_W      = 45
PLAYER_H      = 45
PLAYER_X      = 120

# Ground
GROUND_Y      = HEIGHT - 90  # top of ground strip
GROUND_H      = 90

# Obstacle
OBS_W         = 38
OBS_H         = 50

# Coin
COIN_R        = 10

# Colors
C_SKY1        = (15, 10, 40)
C_SKY2        = (30, 20, 70)
C_GROUND      = (50, 50, 100)
C_GROUND_LINE = (100, 100, 200)
C_WHITE       = (255, 255, 255)
C_YELLOW      = (255, 230, 50)
C_RED         = (255, 70, 70)
C_GREEN       = (80, 255, 120)
C_BLACK       = (0, 0, 0)
C_GREY        = (160, 160, 160)
C_SCORE       = (255, 240, 80)
C_DARK        = (20, 20, 50)

PLAYER_COLORS = [
    (0, 200, 255),   # cyan
    (255, 100, 200), # pink
    (100, 255, 100), # green
    (255, 180, 50),  # orange
    (180, 100, 255), # purple
]

LEVELS = [
    {"name": "Level 1 · Easy",   "speed":  4, "min_gap": 75, "max_gap": 130, "duration": 60, "coins": 3},
    {"name": "Level 2 · Medium", "speed":  6, "min_gap": 60, "max_gap": 110, "duration": 55, "coins": 5},
    {"name": "Level 3 · Hard",   "speed":  8, "min_gap": 45, "max_gap":  80, "duration": 50, "coins": 6},
    {"name": "Level 4 · Insane", "speed": 11, "min_gap": 30, "max_gap":  55, "duration": 45, "coins": 8},
    {"name": "Level 5 · Demon",  "speed": 14, "min_gap": 22, "max_gap":  40, "duration": 40, "coins": 10},
]


# ── HELPERS ───────────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def glow_surface(surf, color, radius=8, alpha=80):
    """Draw a soft glow around a surface (blurred outline)."""
    w, h = surf.get_size()
    glow = pygame.Surface((w + radius*2, h + radius*2), pygame.SRCALPHA)
    glow.fill((0, 0, 0, 0))
    r, g, b = color
    for i in range(radius, 0, -2):
        a = int(alpha * (i / radius) * 0.5)
        s = pygame.Surface((w + i*2, h + i*2), pygame.SRCALPHA)
        s.fill((r, g, b, a))
        glow.blit(s, (radius - i, radius - i))
    return glow


def draw_text(surf, text, x, y, font, color, center=False, shadow=True):
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        sr = shadow_surf.get_rect()
        if center:
            sr.center = (x+2, y+2)
        else:
            sr.topleft = (x+2, y+2)
        surf.blit(shadow_surf, sr)
    ts = font.render(text, True, color)
    r = ts.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(ts, r)
    return r


def load_scores():
    try:
        return json.loads(SCORES_FILE.read_text())
    except Exception:
        return {}


def save_scores(scores):
    try:
        SCORES_FILE.write_text(json.dumps(scores, indent=2))
    except Exception:
        pass


# ── PARTICLES ─────────────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color, vel=None, life=None, size=None):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 8) if vel is None else vel
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(1, 4)
        self.life = life or random.randint(20, 50)
        self.max_life = self.life
        self.size = size or random.uniform(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.vx *= 0.97
        self.life -= 1

    def draw(self, surf):
        t = self.life / self.max_life
        r, g, b = self.color
        alpha = int(220 * t)
        size = max(1, int(self.size * t))
        s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, alpha), (size, size), size)
        surf.blit(s, (int(self.x) - size, int(self.y) - size))

    @property
    def alive(self):
        return self.life > 0


class TrailParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, vel=2, life=15, size=5)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(0, 2)


# ── STARS ─────────────────────────────────────────────────────────────────────

class Star:
    def __init__(self):
        self.reset(initial=True)

    def reset(self, initial=False):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, GROUND_Y) if initial else random.uniform(0, GROUND_Y)
        self.size = random.uniform(0.5, 2.5)
        self.speed = random.uniform(0.3, 1.5)
        self.brightness = random.uniform(100, 255)
        self.twinkle = random.uniform(0, math.tau)

    def update(self, scroll_speed):
        self.x -= scroll_speed * 0.3
        self.twinkle += 0.07
        if self.x < 0:
            self.x = WIDTH
            self.y = random.uniform(0, GROUND_Y)

    def draw(self, surf):
        b = int(self.brightness * (0.6 + 0.4 * math.sin(self.twinkle)))
        c = (b, b, b)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), max(1, int(self.size)))


# ── GAME ──────────────────────────────────────────────────────────────────────

class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock  = pygame.time.Clock()
        self._fullscreen = False

        # Fonts
        self.font_huge  = pygame.font.SysFont("Arial Black", 56, bold=True)
        self.font_big   = pygame.font.SysFont("Arial Black", 36, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_tiny  = pygame.font.SysFont("Arial", 16)

        # Stars
        self.stars = [Star() for _ in range(120)]

        # Scores + player
        self.scores = load_scores()
        self.player_name  = ""
        self.player_color_idx = 0

        # State
        self.state = "name_entry"
        self.selected_level = 0
        self.particles: list[Particle] = []
        self.scroll_x = 0

        self._reset_round()

    # ── reset ─────────────────────────────────────────────────────────────────
    def _reset_round(self):
        self.player_y    = GROUND_Y - PLAYER_H
        self.vel_y       = 0.0
        self.on_ground   = True
        self.jumps_left  = MAX_JUMPS
        self.angle       = 0.0
        self.obstacles   : list[dict] = []
        self.coins       : list[dict] = []
        self.score       = 0
        self.coins_collected = 0
        self.level_timer = 0
        self.rng         = random.Random()
        lvl = LEVELS[self.selected_level]
        self.frames_until_obs  = lvl["min_gap"]
        self.frames_until_coin = self.rng.randint(40, 80)
        self.particles.clear()
        self.dead = False

    # ── main loop ─────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()

    # ── events ────────────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            if event.type == pygame.KEYDOWN:
                self._on_key(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_click(event)

    def _on_key(self, event):
        k = event.key
        # fullscreen toggle
        if k == pygame.K_f:
            self._toggle_fullscreen()
            return
        if k == pygame.K_ESCAPE:
            if self.state in ("playing",):
                self.state = "menu"
            elif self.state == "menu":
                self._quit()
            else:
                self.state = "menu"
            return

        if self.state == "name_entry":
            if k == pygame.K_RETURN and self.player_name.strip():
                self.state = "menu"
            elif k == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif k == pygame.K_TAB:
                self.player_color_idx = (self.player_color_idx + 1) % len(PLAYER_COLORS)
            elif event.unicode and len(self.player_name) < 16:
                if event.unicode.isprintable():
                    self.player_name += event.unicode

        elif self.state == "menu":
            if k == pygame.K_SPACE or k == pygame.K_RETURN:
                self.state = "level_select"
            if k == pygame.K_l:
                self.state = "leaderboard"

        elif self.state == "level_select":
            if k in (pygame.K_LEFT, pygame.K_a):
                self.selected_level = (self.selected_level - 1) % len(LEVELS)
                self._reset_round()
            if k in (pygame.K_RIGHT, pygame.K_d):
                self.selected_level = (self.selected_level + 1) % len(LEVELS)
                self._reset_round()
            if k == pygame.K_RETURN or k == pygame.K_SPACE:
                self._reset_round()
                self.state = "playing"

        elif self.state == "playing":
            if k in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self._jump()

        elif self.state in ("gameover", "complete"):
            if k in (pygame.K_SPACE, pygame.K_RETURN):
                self.state = "menu"
            if k == pygame.K_r:
                self._reset_round()
                self.state = "playing"

        elif self.state == "leaderboard":
            if k in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self.state = "menu"

    def _on_click(self, event):
        if self.state == "playing":
            self._jump()

    def _jump(self):
        if self.on_ground:
            self.vel_y = JUMP_VEL
            self.on_ground = False
            self.jumps_left = MAX_JUMPS - 1
            self._spawn_jump_particles()
        elif self.jumps_left > 0:
            self.vel_y = JUMP_VEL * 0.9
            self.jumps_left -= 1
            self._spawn_jump_particles()

    def _spawn_jump_particles(self):
        color = PLAYER_COLORS[self.player_color_idx]
        px = PLAYER_X + PLAYER_W // 2
        py = self.player_y + PLAYER_H
        for _ in range(10):
            self.particles.append(TrailParticle(px, py, color))

    def _spawn_death_particles(self):
        color = PLAYER_COLORS[self.player_color_idx]
        px = PLAYER_X + PLAYER_W // 2
        py = self.player_y + PLAYER_H // 2
        for _ in range(60):
            self.particles.append(Particle(px, py, color))
        for _ in range(20):
            self.particles.append(Particle(px, py, C_WHITE, life=30, size=4))

    def _toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def _quit(self):
        pygame.quit()
        sys.exit(0)

    # ── update ────────────────────────────────────────────────────────────────
    def _update(self):
        lvl = LEVELS[self.selected_level]
        speed = lvl["speed"]

        # always scroll stars + scroll counter
        self.scroll_x += speed
        for star in self.stars:
            star.update(speed)

        # particles always
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

        if self.state != "playing":
            return

        # physics
        self.vel_y += GRAVITY
        self.player_y += self.vel_y

        if self.player_y >= GROUND_Y - PLAYER_H:
            self.player_y = GROUND_Y - PLAYER_H
            self.vel_y = 0.0
            self.on_ground = True
            self.jumps_left = MAX_JUMPS
            self.angle = round(self.angle / 90) * 90  # snap to grid

        if not self.on_ground:
            self.angle -= 6

        # trail particles
        if self.level_timer % 3 == 0:
            color = PLAYER_COLORS[self.player_color_idx]
            self.particles.append(TrailParticle(PLAYER_X, self.player_y + PLAYER_H//2, color))

        # obstacles
        self.frames_until_obs -= 1
        if self.frames_until_obs <= 0:
            h = OBS_H + self.rng.randint(-10, 15)
            self.obstacles.append({"x": WIDTH + 20, "h": h, "passed": False, "glow": 0})
            # double spike sometimes
            if self.rng.random() < 0.35 and self.selected_level >= 2:
                self.obstacles.append({"x": WIDTH + 20 + OBS_W + 6, "h": h - 5, "passed": False, "glow": 0})
            self.frames_until_obs = self.rng.randint(lvl["min_gap"], lvl["max_gap"])

        for obs in self.obstacles:
            obs["x"] -= speed
            obs["glow"] = (obs["glow"] + 4) % 360
            if not obs["passed"] and obs["x"] + OBS_W < PLAYER_X:
                obs["passed"] = True
                self.score += 1
        self.obstacles = [o for o in self.obstacles if o["x"] + OBS_W > 0]

        # coins
        self.frames_until_coin -= 1
        if self.frames_until_coin <= 0:
            cy = self.rng.randint(GROUND_Y - 180, GROUND_Y - 50)
            self.coins.append({"x": WIDTH + 20, "y": cy, "collected": False, "anim": 0})
            self.frames_until_coin = self.rng.randint(40, 90)

        for coin in self.coins:
            coin["x"] -= speed
            coin["anim"] = (coin["anim"] + 3) % 360
        self.coins = [c for c in self.coins if c["x"] + COIN_R > 0 and not c["collected"]]

        # coin collision
        pr = pygame.Rect(PLAYER_X + 4, self.player_y + 4, PLAYER_W - 8, PLAYER_H - 8)
        for coin in self.coins:
            cx, cy = int(coin["x"]), int(coin["y"])
            if pr.collidepoint(cx, cy):
                coin["collected"] = True
                self.coins_collected += 1
                self.score += 2
                for _ in range(15):
                    self.particles.append(Particle(cx, cy, C_YELLOW, life=25, size=5))

        # obstacle collision
        for obs in self.obstacles:
            ox = int(obs["x"])
            oh = int(obs["h"])
            # triangle: base ox..ox+OBS_W at GROUND_Y, tip at GROUND_Y-oh
            # approximate bounding box with shrink
            m = 6
            obs_rect = pygame.Rect(ox + m, GROUND_Y - oh + m, OBS_W - 2*m, oh - m)
            if pr.colliderect(obs_rect):
                self._die()
                return

        self.level_timer += 1
        if self.level_timer >= FPS * lvl["duration"]:
            self._complete()

    def _die(self):
        self._spawn_death_particles()
        self.state = "gameover"
        self._update_score()

    def _complete(self):
        self.state = "complete"
        self._update_score()

    def _update_score(self):
        name = self.player_name.strip() or "Player"
        lvl_name = LEVELS[self.selected_level]["name"]
        key = f"{name}|{lvl_name}"
        prev = self.scores.get(key, {}).get("score", 0)
        if self.score > prev:
            self.scores[key] = {
                "name": name,
                "level": lvl_name,
                "score": self.score,
                "coins": self.coins_collected,
            }
            save_scores(self.scores)

    # ── draw ──────────────────────────────────────────────────────────────────
    def _draw(self):
        surf = self.screen

        # gradient sky
        for y in range(HEIGHT):
            t = y / HEIGHT
            c = lerp_color(C_SKY1, C_SKY2, t)
            pygame.draw.line(surf, c, (0, y), (WIDTH, y))

        # stars
        for star in self.stars:
            star.draw(surf)

        # animated grid lines (subtle)
        off = int(self.scroll_x) % 80
        for x in range(-80 + off, WIDTH + 80, 80):
            pygame.draw.line(surf, (30, 30, 60), (x, 0), (x, GROUND_Y), 1)
        for y in range(0, GROUND_Y, 60):
            pygame.draw.line(surf, (30, 30, 60), (0, y), (WIDTH, y), 1)

        # ground
        pygame.draw.rect(surf, C_GROUND, (0, GROUND_Y, WIDTH, GROUND_H))
        pygame.draw.line(surf, C_GROUND_LINE, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        # ground tile lines
        tile_off = int(self.scroll_x) % 60
        for x in range(-60 + tile_off, WIDTH + 60, 60):
            pygame.draw.line(surf, (70, 70, 130), (x, GROUND_Y), (x, HEIGHT), 1)

        # particles (behind player)
        for p in self.particles:
            p.draw(surf)

        # draw coins
        for coin in self.coins:
            self._draw_coin(surf, coin)

        # draw obstacles
        self._draw_obstacles(surf)

        # draw player (only if alive)
        if self.state in ("playing",) or (self.state in ("gameover",) and len(self.particles) > 30):
            self._draw_player(surf)
        elif self.state not in ("gameover", "complete"):
            self._draw_player(surf)

        # UI
        if self.state == "name_entry":
            self._draw_name_entry(surf)
        elif self.state == "menu":
            self._draw_menu(surf)
        elif self.state == "level_select":
            self._draw_level_select(surf)
        elif self.state == "playing":
            self._draw_hud(surf)
        elif self.state == "gameover":
            self._draw_gameover(surf)
        elif self.state == "complete":
            self._draw_complete(surf)
        elif self.state == "leaderboard":
            self._draw_leaderboard(surf)

    def _draw_player(self, surf):
        ps_w, ps_h = PLAYER_W, PLAYER_H
        color = PLAYER_COLORS[self.player_color_idx]
        cx = PLAYER_X + ps_w // 2
        cy = int(self.player_y) + ps_h // 2

        # glow
        glow_size = 30
        glow_surf = pygame.Surface((ps_w + glow_size*2, ps_h + glow_size*2), pygame.SRCALPHA)
        r, g, b = color
        for i in range(glow_size, 0, -3):
            a = int(60 * (i / glow_size))
            pygame.draw.rect(glow_surf, (r, g, b, a),
                             (glow_size - i, glow_size - i, ps_w + i*2, ps_h + i*2),
                             border_radius=4)
        surf.blit(glow_surf, (cx - ps_w//2 - glow_size, cy - ps_h//2 - glow_size))

        # rotated square
        half_w = ps_w / 2
        half_h = ps_h / 2
        ang = math.radians(self.angle)
        corners = []
        for rx, ry in [(-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h)]:
            rr = math.sqrt(rx*rx + ry*ry)
            a = math.atan2(ry, rx) + ang
            corners.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))

        pygame.draw.polygon(surf, color, corners)

        # inner pattern
        inner = 0.45
        ic = []
        for rx, ry in [(-half_w*inner, -half_h*inner), (half_w*inner, -half_h*inner),
                       (half_w*inner, half_h*inner), (-half_w*inner, half_h*inner)]:
            rr = math.sqrt(rx*rx + ry*ry)
            a = math.atan2(ry, rx) + ang
            ic.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        dark = tuple(max(0, c - 60) for c in color)
        pygame.draw.polygon(surf, dark, ic)

        # outline
        pygame.draw.polygon(surf, C_WHITE, corners, 2)

        # cross lines
        mids = [((corners[i][0]+corners[(i+1)%4][0])/2,
                 (corners[i][1]+corners[(i+1)%4][1])/2) for i in range(4)]
        pygame.draw.line(surf, C_WHITE, (int(mids[0][0]), int(mids[0][1])),
                         (int(mids[2][0]), int(mids[2][1])), 1)
        pygame.draw.line(surf, C_WHITE, (int(mids[1][0]), int(mids[1][1])),
                         (int(mids[3][0]), int(mids[3][1])), 1)

    def _draw_obstacles(self, surf):
        for obs in self.obstacles:
            ox = int(obs["x"])
            oh = int(obs["h"])
            base_y = GROUND_Y
            tip_y  = GROUND_Y - oh
            tip_x  = ox + OBS_W // 2

            # glow outline
            glow_a = int(100 + 80 * math.sin(math.radians(obs["glow"])))
            glow_color = (255, glow_a, glow_a)
            for off in range(5, 0, -2):
                pygame.draw.polygon(surf, (*glow_color, 40),
                                    [(ox - off, base_y), (ox + OBS_W + off, base_y), (tip_x, tip_y - off)])
            # fill
            pygame.draw.polygon(surf, C_RED,
                                 [(ox, base_y), (ox + OBS_W, base_y), (tip_x, tip_y)])
            # lighter face
            mid_x = (ox + tip_x) // 2
            mid_y = (base_y + tip_y) // 2
            pygame.draw.polygon(surf, (255, 130, 130),
                                 [(mid_x, mid_y), (ox + OBS_W, base_y), (tip_x, tip_y)])
            # outline
            pygame.draw.polygon(surf, C_BLACK,
                                 [(ox, base_y), (ox + OBS_W, base_y), (tip_x, tip_y)], 2)

    def _draw_coin(self, surf, coin):
        cx, cy = int(coin["x"]), int(coin["y"])
        a = math.radians(coin["anim"])
        # squish to simulate rotation
        rx = max(2, int(COIN_R * abs(math.cos(a))))
        ry = COIN_R
        color = (255, 210, 40)
        pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx*2, ry*2))
        pygame.draw.ellipse(surf, (255, 255, 150), (cx - rx//2, cy - ry//2, rx, ry))
        pygame.draw.ellipse(surf, (200, 160, 0), (cx - rx, cy - ry, rx*2, ry*2), 2)

    # ── UI screens ────────────────────────────────────────────────────────────
    def _draw_panel(self, surf, x, y, w, h, alpha=180):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((10, 10, 30, alpha))
        pygame.draw.rect(s, (80, 80, 200, 200), (0, 0, w, h), 2, border_radius=12)
        surf.blit(s, (x, y))

    def _draw_name_entry(self, surf):
        self._draw_panel(surf, WIDTH//2 - 320, HEIGHT//2 - 200, 640, 420)
        draw_text(surf, "GEOMETRY DASH", WIDTH//2, HEIGHT//2 - 155, self.font_huge, C_YELLOW, center=True)
        draw_text(surf, "Enter your name to begin!", WIDTH//2, HEIGHT//2 - 85, self.font_med, C_WHITE, center=True)

        # name box
        color = PLAYER_COLORS[self.player_color_idx]
        box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 45, 400, 55)
        pygame.draw.rect(surf, (30, 30, 60), box_rect, border_radius=8)
        pygame.draw.rect(surf, color, box_rect, 3, border_radius=8)
        display_name = self.player_name + ("|" if pygame.time.get_ticks() % 1000 < 500 else "")
        draw_text(surf, display_name, WIDTH//2, HEIGHT//2 - 22, self.font_big, color, center=True, shadow=False)

        draw_text(surf, "TAB = change colour", WIDTH//2, HEIGHT//2 + 35, self.font_small, C_GREY, center=True)

        # color swatches
        for i, c in enumerate(PLAYER_COLORS):
            cx = WIDTH//2 - len(PLAYER_COLORS)*25 + i*50
            pygame.draw.circle(surf, c, (cx, HEIGHT//2 + 80), 18)
            if i == self.player_color_idx:
                pygame.draw.circle(surf, C_WHITE, (cx, HEIGHT//2 + 80), 18, 3)

        draw_text(surf, "ENTER to start", WIDTH//2, HEIGHT//2 + 120, self.font_med, C_GREEN, center=True)

    def _draw_menu(self, surf):
        self._draw_panel(surf, WIDTH//2 - 300, HEIGHT//2 - 180, 600, 360)

        # pulsing title
        t = math.sin(pygame.time.get_ticks() / 400) * 0.08 + 1
        title_surf = self.font_huge.render("GEOMETRY DASH", True, C_YELLOW)
        tw = int(title_surf.get_width() * t)
        th = int(title_surf.get_height() * t)
        scaled = pygame.transform.scale(title_surf, (tw, th))
        surf.blit(scaled, (WIDTH//2 - tw//2, HEIGHT//2 - 160))

        name = self.player_name.strip() or "Player"
        color = PLAYER_COLORS[self.player_color_idx]
        draw_text(surf, f"Welcome,  {name}!", WIDTH//2, HEIGHT//2 - 65, self.font_med, color, center=True)
        draw_text(surf, "SPACE / ENTER  — Play", WIDTH//2, HEIGHT//2 - 20, self.font_small, C_WHITE, center=True)
        draw_text(surf, "L — Leaderboard",        WIDTH//2, HEIGHT//2 + 20, self.font_small, C_WHITE, center=True)
        draw_text(surf, "F — Fullscreen   ESC — Quit", WIDTH//2, HEIGHT//2 + 55, self.font_tiny, C_GREY, center=True)

        # best score
        name_key = name + "|"
        bests = [(k.split("|")[1], v["score"]) for k, v in self.scores.items() if k.startswith(name_key)]
        if bests:
            bests.sort(key=lambda x: x[1], reverse=True)
            lvl_name, sc = bests[0]
            draw_text(surf, f"Your best: {sc} pts on {lvl_name}",
                      WIDTH//2, HEIGHT//2 + 95, self.font_tiny, C_YELLOW, center=True)

    def _draw_level_select(self, surf):
        self._draw_panel(surf, WIDTH//2 - 340, 30, 680, HEIGHT - 60)
        draw_text(surf, "SELECT LEVEL", WIDTH//2, 65, self.font_big, C_YELLOW, center=True)
        draw_text(surf, "← → arrows  |  ENTER to play", WIDTH//2, 110, self.font_small, C_GREY, center=True)

        for i, lvl in enumerate(LEVELS):
            y = 160 + i * 58
            selected = i == self.selected_level
            box_color = (50, 50, 120) if selected else (20, 20, 50)
            border    = PLAYER_COLORS[self.player_color_idx] if selected else (60, 60, 100)
            self._draw_panel(surf, WIDTH//2 - 280, y - 5, 560, 50, alpha=200 if selected else 140)
            pygame.draw.rect(surf, border, (WIDTH//2 - 280, y - 5, 560, 50), 2, border_radius=8)
            text_color = C_YELLOW if selected else C_WHITE
            prefix = "▶  " if selected else "   "
            draw_text(surf, prefix + lvl["name"], WIDTH//2, y + 20,
                      self.font_med if selected else self.font_small, text_color, center=True)
            # show speed stars
            stars = "★" * (i + 1) + "☆" * (4 - i)
            draw_text(surf, stars, WIDTH//2 + 180, y + 20, self.font_small,
                      C_YELLOW if selected else C_GREY, center=True)

    def _draw_hud(self, surf):
        lvl = LEVELS[self.selected_level]
        remaining = max(0, lvl["duration"] - self.level_timer // FPS)
        progress   = min(1.0, self.level_timer / (FPS * lvl["duration"]))
        color = PLAYER_COLORS[self.player_color_idx]

        # top bar
        self._draw_panel(surf, 0, 0, WIDTH, 50, alpha=160)

        draw_text(surf, f"Score: {self.score}", 12, 12, self.font_med, C_SCORE)
        draw_text(surf, f"Coins: {self.coins_collected}", 200, 12, self.font_small, C_YELLOW)
        draw_text(surf, lvl["name"], WIDTH//2, 14, self.font_small, C_WHITE, center=True)
        draw_text(surf, f"Time: {remaining}s", WIDTH - 130, 12, self.font_med, C_WHITE)

        # progress bar
        bar_w = WIDTH - 240
        bar_x = 120
        bar_y = 42
        pygame.draw.rect(surf, (40, 40, 80), (bar_x, bar_y, bar_w, 6), border_radius=3)
        pygame.draw.rect(surf, color, (bar_x, bar_y, int(bar_w * progress), 6), border_radius=3)

        # jump indicator
        for j in range(MAX_JUMPS):
            filled = j < (MAX_JUMPS - self.jumps_left if not self.on_ground else 0)
            c = color if not filled else (40, 40, 80)
            pygame.draw.circle(surf, c, (WIDTH - 20 - j*22, 20), 8)
            pygame.draw.circle(surf, C_WHITE, (WIDTH - 20 - j*22, 20), 8, 1)

    def _draw_gameover(self, surf):
        self._draw_panel(surf, WIDTH//2 - 300, HEIGHT//2 - 200, 600, 400)
        # shake text
        shake = random.randint(-2, 2) if len(self.particles) > 5 else 0
        draw_text(surf, "GAME OVER", WIDTH//2 + shake, HEIGHT//2 - 155,
                  self.font_huge, C_RED, center=True)
        color = PLAYER_COLORS[self.player_color_idx]
        draw_text(surf, f"Score: {self.score}   Coins: {self.coins_collected}",
                  WIDTH//2, HEIGHT//2 - 80, self.font_med, color, center=True)
        # check if new best
        name = self.player_name.strip() or "Player"
        key  = f"{name}|{LEVELS[self.selected_level]['name']}"
        best = self.scores.get(key, {}).get("score", 0)
        if self.score >= best and self.score > 0:
            draw_text(surf, "🏆  NEW PERSONAL BEST!", WIDTH//2, HEIGHT//2 - 30,
                      self.font_med, C_YELLOW, center=True)
        draw_text(surf, "SPACE / ENTER — Menu", WIDTH//2, HEIGHT//2 + 40,
                  self.font_small, C_WHITE, center=True)
        draw_text(surf, "R — Try Again",        WIDTH//2, HEIGHT//2 + 80,
                  self.font_small, C_WHITE, center=True)

    def _draw_complete(self, surf):
        self._draw_panel(surf, WIDTH//2 - 300, HEIGHT//2 - 200, 600, 400)
        t = abs(math.sin(pygame.time.get_ticks() / 300))
        c = lerp_color(C_GREEN, C_YELLOW, t)
        draw_text(surf, "LEVEL COMPLETE!", WIDTH//2, HEIGHT//2 - 155,
                  self.font_huge, c, center=True)
        color = PLAYER_COLORS[self.player_color_idx]
        draw_text(surf, f"Score: {self.score}   Coins: {self.coins_collected}",
                  WIDTH//2, HEIGHT//2 - 80, self.font_med, color, center=True)
        name = self.player_name.strip() or "Player"
        key  = f"{name}|{LEVELS[self.selected_level]['name']}"
        best = self.scores.get(key, {}).get("score", 0)
        if self.score >= best and self.score > 0:
            draw_text(surf, "🏆  NEW PERSONAL BEST!", WIDTH//2, HEIGHT//2 - 30,
                      self.font_med, C_YELLOW, center=True)
        draw_text(surf, "SPACE / ENTER — Menu", WIDTH//2, HEIGHT//2 + 40,
                  self.font_small, C_WHITE, center=True)
        draw_text(surf, "R — Play Again",       WIDTH//2, HEIGHT//2 + 80,
                  self.font_small, C_WHITE, center=True)

    def _draw_leaderboard(self, surf):
        self._draw_panel(surf, WIDTH//2 - 360, 20, 720, HEIGHT - 40)
        draw_text(surf, "🏆  LEADERBOARD", WIDTH//2, 50, self.font_big, C_YELLOW, center=True)
        if not self.scores:
            draw_text(surf, "No scores yet — go play!", WIDTH//2, HEIGHT//2,
                      self.font_med, C_GREY, center=True)
        else:
            rows = sorted(self.scores.values(), key=lambda v: v["score"], reverse=True)[:12]
            for i, row in enumerate(rows):
                y = 110 + i * 36
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
                c = [C_YELLOW, C_WHITE, (205, 127, 50)][i] if i < 3 else C_GREY
                draw_text(surf, f"{medal}  {row['name']:<14} {row['level']:<20} {row['score']:>4} pts  {row['coins']} 🪙",
                          WIDTH//2, y, self.font_small, c, center=True)
        draw_text(surf, "SPACE to return", WIDTH//2, HEIGHT - 55, self.font_small, C_GREY, center=True)


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

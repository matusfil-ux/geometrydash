"""
Geometry Dash — Toga Version
Runs on Mac:  python -m geometrydash
iOS:          briefcase create iOS → Xcode → Cmd+R
"""

import asyncio
import math
import random

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

# ── SETTINGS ← edit these! ────────────────────────────────────────────────────
FPS            = 60
BG_COLOR       = "#1E1E33"
GROUND_COLOR   = "#4F4F78"
PLAYER_COLOR   = "#00C7FF"   # change this!
OBSTACLE_COLOR = "#FF4F4F"
SCORE_COLOR    = "#FFFF63"
WHITE          = "#FFFFFF"

# All positions are fractions of window size (0.0 – 1.0)
GROUND_H_FRAC  = 0.15   # ground strip height
PLAYER_SIZE    = 0.10   # player square size
PLAYER_X_FRAC  = 0.15   # player x position
OBS_W_FRAC     = 0.04   # obstacle width
OBS_H_FRAC     = 0.13   # obstacle height

JUMP_VEL       = 0.022  # bigger = higher jump
GRAVITY        = 0.0012 # bigger = falls faster

LEVELS = [
    {"name": "Level 1 · Easy",   "speed": 0.006, "min_gap": 90,  "max_gap": 150, "duration": 60},
    {"name": "Level 2 · Medium", "speed": 0.009, "min_gap": 70,  "max_gap": 120, "duration": 60},
    {"name": "Level 3 · Hard",   "speed": 0.013, "min_gap": 35,  "max_gap": 65,  "duration": 50},
    {"name": "Level 4 · Insane", "speed": 0.015, "min_gap": 25,  "max_gap": 50,  "duration": 45},
    {"name": "Level 5 · Demon",  "speed": 0.007, "min_gap": 20,  "max_gap": 40,  "duration": 40},
]
# ─────────────────────────────────────────────────────────────────────────────


class GeometryDashApp(toga.App):

    def startup(self):
        self.canvas = toga.Canvas(style=Pack(flex=1), on_press=self._on_press)
        box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        box.add(self.canvas)
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()
        self._init_state()

    def on_running(self):
        """Override — called when the event loop starts."""
        asyncio.create_task(self._game_loop())

    # ── state ─────────────────────────────────────────────────────────────────
    def _init_state(self):
        self.state = "menu"
        self.selected_level = 0
        self.coins = 0
        self.high_score = 0
        self._reset_round()

    def _reset_round(self):
        self.obstacles = []
        self.score = 0
        self.level_timer = 0
        self.rng = random.Random()
        lvl = LEVELS[self.selected_level]
        self.frames_until_next = lvl["min_gap"]
        # player_y_frac: fraction from TOP of window (0=top, 1=bottom)
        # ground top = 1 - GROUND_H_FRAC  → player sits just above it
        self.player_y_frac = 1.0 - GROUND_H_FRAC - PLAYER_SIZE
        self.vel_y = 0.0       # positive = moving DOWN
        self.on_ground = True
        self.angle = 0.0
        self.max_jumps = (3 if self.selected_level == 3
                          else 1 if self.selected_level == 4
                          else 2)
        self.jumps_left = self.max_jumps

    # ── game loop ─────────────────────────────────────────────────────────────
    async def _game_loop(self):
        while True:
            if self.state == "playing":
                self._update()
            self._draw()
            await asyncio.sleep(1.0 / FPS)

    # ── input ─────────────────────────────────────────────────────────────────
    def _on_press(self, widget, x, y, **kwargs):
        w = self._w()
        if self.state == "menu":
            self.state = "level_select"
        elif self.state == "level_select":
            if x < w * 0.25:
                self.selected_level = (self.selected_level - 1) % len(LEVELS)
                self._reset_round()
            elif x > w * 0.75:
                self.selected_level = (self.selected_level + 1) % len(LEVELS)
                self._reset_round()
            else:
                self._reset_round()
                self.state = "playing"
        elif self.state == "playing":
            self._jump()
        elif self.state in ("gameover", "complete"):
            self.state = "menu"

    def _jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_VEL      # negative = moving UP (y decreases)
            self.on_ground = False
            self.jumps_left = self.max_jumps - 1
        elif self.jumps_left > 0:
            self.vel_y = -JUMP_VEL
            self.jumps_left -= 1

    # ── update ────────────────────────────────────────────────────────────────
    def _update(self):
        lvl = LEVELS[self.selected_level]

        # gravity pulls DOWN → vel_y increases
        self.vel_y += GRAVITY
        self.player_y_frac += self.vel_y
        if not self.on_ground:
            self.angle -= 5

        # ground: top of ground strip = 1 - GROUND_H_FRAC
        ground_top = 1.0 - GROUND_H_FRAC - PLAYER_SIZE
        if self.player_y_frac >= ground_top:
            self.player_y_frac = ground_top
            self.vel_y = 0.0
            self.on_ground = True
            self.jumps_left = self.max_jumps
            self.angle = 0.0

        # spawn
        self.frames_until_next -= 1
        if self.frames_until_next <= 0:
            self.obstacles.append({"x": 1.05, "passed": False})
            if self.rng.random() < 0.3 and self.selected_level != 4:
                self.obstacles.append({"x": 1.05 + OBS_W_FRAC + 0.01, "passed": False})
            self.frames_until_next = self.rng.randint(lvl["min_gap"], lvl["max_gap"])

        # move
        for obs in self.obstacles:
            obs["x"] -= lvl["speed"]
            if not obs["passed"] and obs["x"] + OBS_W_FRAC < PLAYER_X_FRAC:
                obs["passed"] = True
                self.score += 1
                self.coins += 1
        self.obstacles = [o for o in self.obstacles if o["x"] + OBS_W_FRAC > 0]

        # collision (all fractions)
        m = PLAYER_SIZE * 0.12
        pr = (PLAYER_X_FRAC + m,
              self.player_y_frac + m,
              PLAYER_SIZE - 2*m,
              PLAYER_SIZE - 2*m)
        obs_top = 1.0 - GROUND_H_FRAC - OBS_H_FRAC
        for obs in self.obstacles:
            om = OBS_W_FRAC * 0.15
            orect = (obs["x"] + om, obs_top, OBS_W_FRAC - 2*om, OBS_H_FRAC)
            if self._overlap(pr, orect):
                if self.score > self.high_score:
                    self.high_score = self.score
                self.state = "gameover"
                return

        self.level_timer += 1
        if self.level_timer >= FPS * lvl["duration"]:
            if self.score > self.high_score:
                self.high_score = self.score
            self.state = "complete"

    @staticmethod
    def _overlap(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return x1 < x2+w2 and x1+w1 > x2 and y1 < y2+h2 and y1+h1 > y2

    # ── helpers ───────────────────────────────────────────────────────────────
    def _w(self):
        v = self.canvas.layout.content_width
        return v if v and v > 10 else 800

    def _h(self):
        v = self.canvas.layout.content_height
        return v if v and v > 10 else 600

    # ── draw ──────────────────────────────────────────────────────────────────
    def _draw(self):
        W, H = self._w(), self._h()
        ctx = self.canvas.context
        ctx.clear()

        # Background
        ctx.fill(color=BG_COLOR)
        ctx.rect(0, 0, W, H)

        # Ground strip (bottom of screen)
        gy = H * (1.0 - GROUND_H_FRAC)   # y where ground starts (top of strip)
        ctx.fill(color=GROUND_COLOR)
        ctx.rect(0, gy, W, H * GROUND_H_FRAC)

        # Ground line
        ctx.stroke(color="#7878B4", line_width=2)
        ctx.begin_path()
        ctx.move_to(0, gy)
        ctx.line_to(W, gy)

        # Obstacles (triangles pointing UP from ground)
        ow = W * OBS_W_FRAC
        oh = H * OBS_H_FRAC
        for obs in self.obstacles:
            ox = obs["x"] * W          # left edge
            base_y = gy                # bottom of triangle = ground line
            tip_y  = gy - oh           # tip points UP
            tip_x  = ox + ow / 2
            ctx.fill(color=OBSTACLE_COLOR)
            ctx.begin_path()
            ctx.move_to(ox, base_y)
            ctx.line_to(ox + ow, base_y)
            ctx.line_to(tip_x, tip_y)
            ctx.close_path()
            ctx.stroke(color="#000000", line_width=1)
            ctx.begin_path()
            ctx.move_to(ox, base_y)
            ctx.line_to(ox + ow, base_y)
            ctx.line_to(tip_x, tip_y)
            ctx.close_path()

        # Player square (rotated)
        ps = H * PLAYER_SIZE
        px_abs = PLAYER_X_FRAC * W
        py_abs = self.player_y_frac * H   # top-left corner y
        cx = px_abs + ps / 2
        cy = py_abs + ps / 2
        ang = math.radians(self.angle)
        half = ps / 2
        corners = []
        for rx, ry in [(-half, -half), (half, -half), (half, half), (-half, half)]:
            rr = math.sqrt(rx*rx + ry*ry)
            a = math.atan2(ry, rx) + ang
            corners.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))

        ctx.fill(color=PLAYER_COLOR)
        ctx.begin_path()
        ctx.move_to(*corners[0]); ctx.line_to(*corners[1])
        ctx.line_to(*corners[2]); ctx.line_to(*corners[3])
        ctx.close_path()

        ctx.stroke(color="#FFFFFF", line_width=1)
        ctx.begin_path()
        ctx.move_to(*corners[0]); ctx.line_to(*corners[1])
        ctx.line_to(*corners[2]); ctx.line_to(*corners[3])
        ctx.close_path()

        # ── HUD / menus ───────────────────────────────────────────────────────
        fs_big   = max(12, int(H * 0.09))
        fs_med   = max(10, int(H * 0.05))
        fs_small = max(9,  int(H * 0.035))

        if self.state == "menu":
            self._txt(ctx, "GEOMETRY DASH",   W/2, H*0.40, fs_big,   SCORE_COLOR, True)
            self._txt(ctx, "TAP to start",    W/2, H*0.55, fs_med,   WHITE,       True)
            self._txt(ctx, f"Coins: {self.coins}   Best: {self.high_score}",
                      W/2, H*0.65, fs_small, WHITE, True)

        elif self.state == "level_select":
            self._txt(ctx, "SELECT LEVEL",    W/2, H*0.12, fs_med,   SCORE_COLOR, True)
            self._txt(ctx, "< tap left/right >   tap centre to play",
                      W/2, H*0.22, fs_small, WHITE, True)
            for i, lvl in enumerate(LEVELS):
                col = SCORE_COLOR if i == self.selected_level else WHITE
                sz  = int(H * (0.048 if i == self.selected_level else 0.036))
                mark = "> " if i == self.selected_level else "  "
                self._txt(ctx, f"{mark}{lvl['name']}", W/2, H*(0.35 + i*0.12), max(9, sz), col, True)

        elif self.state == "playing":
            self._txt(ctx, f"Score: {self.score}",      10, 24,       fs_med,   SCORE_COLOR)
            self._txt(ctx, f"Best: {self.high_score}",  10, 24+fs_med+4, fs_small, WHITE)
            remaining = max(0, LEVELS[self.selected_level]["duration"] - self.level_timer // FPS)
            self._txt(ctx, f"Time: {remaining}s",       10, 24+fs_med+4+fs_small+4, fs_small, WHITE)

        elif self.state == "gameover":
            self._txt(ctx, "GAME OVER",   W/2, H*0.35, fs_big,   OBSTACLE_COLOR, True)
            self._txt(ctx, f"Score: {self.score}   Best: {self.high_score}",
                      W/2, H*0.50, fs_med, SCORE_COLOR, True)
            self._txt(ctx, "TAP to menu", W/2, H*0.62, fs_small, WHITE, True)

        elif self.state == "complete":
            self._txt(ctx, "LEVEL COMPLETE!", W/2, H*0.35, fs_big,   "#63FF63", True)
            self._txt(ctx, f"Score: {self.score}   Best: {self.high_score}",
                      W/2, H*0.50, fs_med, SCORE_COLOR, True)
            self._txt(ctx, "TAP to menu",    W/2, H*0.62, fs_small, WHITE, True)

        self.canvas.redraw()

    def _txt(self, ctx, text, x, y, size, color, center=False):
        font = toga.Font("sans-serif", size)
        if center:
            x -= len(text) * size * 0.30
        ctx.fill(color=color)
        ctx.write_text(text, x, y, font=font)


def main():
    return GeometryDashApp("Geometry Dash", "com.filip.geometrydash")


if __name__ == "__main__":
    main().main_loop()

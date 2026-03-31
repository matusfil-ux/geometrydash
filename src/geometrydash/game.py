"""
Geometry Dash — Toga Version
============================
Runs on Mac and iPad/iPhone using BeeWare Toga + briefcase.

Mac:  python -m geometrydash
iOS:  briefcase create iOS  → open Xcode → Cmd+R

How to improve:
  - Change PLAYER_COLOR to your favourite color (#RRGGBB hex)
  - Change GRAVITY / JUMP_VELOCITY to adjust jump feel
  - Change LEVELS list to add or change levels
"""

import asyncio
import math
import random

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS  ← start here!
# ─────────────────────────────────────────────────────────────────────────────

FPS = 60

# Colors — hex strings (#RRGGBB)
BG_COLOR       = "#1E1E33"
GROUND_COLOR   = "#4F4F78"
PLAYER_COLOR   = "#00C7FF"   # cyan  — change this!
OBSTACLE_COLOR = "#FF4F4F"   # red
SCORE_COLOR    = "#FFFF63"   # yellow
WHITE          = "#FFFFFF"
LINE_COLOR     = "#333350"
GROUND_LINE    = "#7878B4"

GROUND_RATIO   = 0.15   # ground height = this × window height
PLAYER_RATIO   = 0.10   # player size   = this × window height
PLAYER_X_RATIO = 0.15   # player x      = this × window width
OBS_W_RATIO    = 0.04   # obstacle width  (fraction of window width)
OBS_H_RATIO    = 0.13   # obstacle height (fraction of window height)

JUMP_VELOCITY  = 0.022   # bigger = higher jump  (try 0.030 for moon jump)
GRAVITY        = 0.0012  # bigger = falls faster  (try 0.0006 for floaty)

LEVELS = [
    {"name": "Level 1 · Easy",   "speed": 0.006, "min_gap": 90, "max_gap": 150, "duration": 60},
    {"name": "Level 2 · Medium", "speed": 0.009, "min_gap": 70, "max_gap": 120, "duration": 60},
    {"name": "Level 3 · Hard",   "speed": 0.013, "min_gap": 35, "max_gap": 65,  "duration": 50},
    {"name": "Level 4 · Insane", "speed": 0.015, "min_gap": 25, "max_gap": 50,  "duration": 45},
    {"name": "Level 5 · Demon",  "speed": 0.007, "min_gap": 20, "max_gap": 40,  "duration": 40},
]


# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────

class GeometryDashApp(toga.App):

    # ── startup ───────────────────────────────────────────────────────────────
    def startup(self):
        self.canvas = toga.Canvas(
            style=Pack(flex=1),
            on_press=self._on_press,
        )
        box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        box.add(self.canvas)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = box
        self.main_window.show()

        self._init_state()
        self.add_background_task(self._game_loop)

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
        self.player_y_frac = GROUND_RATIO
        self.vel_y_frac = 0.0
        self.on_ground = True
        self.angle = 0.0
        self.max_jumps = (3 if self.selected_level == 3
                          else 1 if self.selected_level == 4
                          else 2)
        self.jumps_left = self.max_jumps

    # ── game loop ─────────────────────────────────────────────────────────────
    async def _game_loop(self, app, **kwargs):
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
            self.vel_y_frac = JUMP_VELOCITY
            self.on_ground = False
            self.jumps_left = self.max_jumps - 1
        elif self.jumps_left > 0:
            self.vel_y_frac = JUMP_VELOCITY
            self.jumps_left -= 1

    # ── update ────────────────────────────────────────────────────────────────
    def _update(self):
        lvl = LEVELS[self.selected_level]
        speed_frac = lvl["speed"]

        self.vel_y_frac -= GRAVITY
        self.player_y_frac += self.vel_y_frac
        if not self.on_ground:
            self.angle -= 5

        if self.player_y_frac <= GROUND_RATIO:
            self.player_y_frac = GROUND_RATIO
            self.vel_y_frac = 0.0
            self.on_ground = True
            self.jumps_left = self.max_jumps
            self.angle = 0.0

        # spawn obstacles
        self.frames_until_next -= 1
        if self.frames_until_next <= 0:
            self.obstacles.append({"x": 1.05, "passed": False})
            if self.rng.random() < 0.3 and self.selected_level != 4:
                self.obstacles.append({"x": 1.05 + OBS_W_RATIO + 0.01, "passed": False})
            self.frames_until_next = self.rng.randint(lvl["min_gap"], lvl["max_gap"])

        # move obstacles
        for obs in self.obstacles:
            obs["x"] -= speed_frac
            if not obs["passed"] and obs["x"] + OBS_W_RATIO < PLAYER_X_RATIO:
                obs["passed"] = True
                self.score += 1
                self.coins += 1

        self.obstacles = [o for o in self.obstacles if o["x"] + OBS_W_RATIO > 0]

        # collision
        ps = PLAYER_RATIO
        m = ps * 0.1
        pr = (PLAYER_X_RATIO + m, self.player_y_frac + m, ps - 2*m, ps - 2*m)
        for obs in self.obstacles:
            om = OBS_W_RATIO * 0.15
            orect = (obs["x"] + om, GROUND_RATIO, OBS_W_RATIO - 2*om, OBS_H_RATIO * 0.6)
            if self._overlap(pr, orect):
                if self.score > self.high_score:
                    self.high_score = self.score
                self.state = "gameover"
                return

        # timer
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

        # Scrolling diagonal lines
        ctx.stroke(color=LINE_COLOR, line_width=1)
        for i in range(-1, int(W / 200) + 3):
            x_off = (self.level_timer * 3) % 200
            lx = i * 200 - x_off
            ctx.begin_path()
            ctx.move_to(lx, 0)
            ctx.line_to(lx + 200, H * 0.85)

        # Ground fill
        gy = H * GROUND_RATIO
        ctx.fill(color=GROUND_COLOR)
        ctx.rect(0, 0, W, gy)

        # Ground line
        ctx.stroke(color=GROUND_LINE, line_width=2)
        ctx.begin_path()
        ctx.move_to(0, gy)
        ctx.line_to(W, gy)

        # Obstacles (triangles)
        ow = W * OBS_W_RATIO
        oh = H * OBS_H_RATIO
        for obs in self.obstacles:
            ox = obs["x"] * W
            oy = GROUND_RATIO * H
            tip_x = ox + ow / 2
            tip_y = oy + oh
            # filled triangle
            ctx.fill(color=OBSTACLE_COLOR)
            ctx.begin_path()
            ctx.move_to(tip_x, tip_y)
            ctx.line_to(ox, oy)
            ctx.line_to(ox + ow, oy)
            ctx.close_path()
            # outline
            ctx.stroke(color="#000000", line_width=1.5)
            ctx.begin_path()
            ctx.move_to(tip_x, tip_y)
            ctx.line_to(ox, oy)
            ctx.line_to(ox + ow, oy)
            ctx.close_path()

        # Player (rotated square = two triangles)
        ps = H * PLAYER_RATIO
        px_abs = PLAYER_X_RATIO * W
        py_abs = self.player_y_frac * H
        cx = px_abs + ps / 2
        cy = py_abs + ps / 2
        ang = math.radians(self.angle)
        half = ps / 2
        r = []
        for rx, ry in [(-half, -half), (half, -half), (half, half), (-half, half)]:
            rr = math.sqrt(rx*rx + ry*ry)
            a = math.atan2(ry, rx) + ang
            r.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))

        # fill — two triangles
        ctx.fill(color=PLAYER_COLOR)
        ctx.begin_path()
        ctx.move_to(*r[0]); ctx.line_to(*r[1]); ctx.line_to(*r[2]); ctx.close_path()
        ctx.begin_path()
        ctx.move_to(*r[0]); ctx.line_to(*r[2]); ctx.line_to(*r[3]); ctx.close_path()

        # outline
        ctx.stroke(color="#FFFFFFAA", line_width=1.5)
        ctx.begin_path()
        ctx.move_to(*r[0]); ctx.line_to(*r[1])
        ctx.line_to(*r[2]); ctx.line_to(*r[3]); ctx.close_path()

        # cross lines
        ctx.stroke(color="#FFFFFFAA", line_width=1)
        mid_t  = ((r[0][0]+r[1][0])/2, (r[0][1]+r[1][1])/2)
        mid_b  = ((r[2][0]+r[3][0])/2, (r[2][1]+r[3][1])/2)
        mid_l  = ((r[0][0]+r[3][0])/2, (r[0][1]+r[3][1])/2)
        mid_ri = ((r[1][0]+r[2][0])/2, (r[1][1]+r[2][1])/2)
        ctx.begin_path(); ctx.move_to(*mid_t);  ctx.line_to(*mid_b)
        ctx.begin_path(); ctx.move_to(*mid_l);  ctx.line_to(*mid_ri)

        # ── UI text ──────────────────────────────────────────────────────────
        fnt_big   = toga.Font("sans-serif", int(H * 0.09))
        fnt_med   = toga.Font("sans-serif", int(H * 0.05))
        fnt_small = toga.Font("sans-serif", int(H * 0.035))
        fnt_tiny  = toga.Font("sans-serif", int(H * 0.030))

        if self.state == "menu":
            self._text(ctx, "GEOMETRY DASH",  W/2, H*0.68, fnt_big,   SCORE_COLOR, center=True)
            self._text(ctx, "TAP to continue", W/2, H*0.55, fnt_small, WHITE,       center=True)
            self._text(ctx, f"Coins: {self.coins}   Best: {self.high_score}",
                       W/2, H*0.45, fnt_small, WHITE, center=True)

        elif self.state == "level_select":
            self._text(ctx, "SELECT LEVEL", W/2, H*0.82, fnt_med,   SCORE_COLOR, center=True)
            self._text(ctx, "◀ tap left/right ▶   tap centre to play",
                       W/2, H*0.73, fnt_small, WHITE, center=True)
            for i, lvl in enumerate(LEVELS):
                col  = SCORE_COLOR if i == self.selected_level else WHITE
                fnt  = toga.Font("sans-serif", int(H * (0.048 if i == self.selected_level else 0.036)))
                mark = "▶ " if i == self.selected_level else "  "
                self._text(ctx, f"{mark}{lvl['name']}", W/2, H*(0.60 - i*0.10), fnt, col, center=True)

        elif self.state == "playing":
            self._text(ctx, f"Score: {self.score}",     16, H*0.93, fnt_med,   SCORE_COLOR)
            self._text(ctx, f"Best:  {self.high_score}", 16, H*0.87, fnt_small, WHITE)
            remaining = max(0, LEVELS[self.selected_level]["duration"] - self.level_timer // FPS)
            self._text(ctx, f"Time: {remaining}s",       16, H*0.81, fnt_small, WHITE)
            self._text(ctx, LEVELS[self.selected_level]["name"], 16, H*0.75, fnt_tiny, "#C7C7FF")

        elif self.state == "gameover":
            self._text(ctx, "GAME OVER",  W/2, H*0.65, fnt_big, OBSTACLE_COLOR, center=True)
            self._text(ctx, f"Score: {self.score}   Best: {self.high_score}",
                       W/2, H*0.52, fnt_med, SCORE_COLOR, center=True)
            self._text(ctx, "TAP to menu", W/2, H*0.42, fnt_small, WHITE, center=True)

        elif self.state == "complete":
            self._text(ctx, "LEVEL COMPLETE!", W/2, H*0.65, fnt_big, "#63FF63", center=True)
            self._text(ctx, f"Score: {self.score}   Best: {self.high_score}",
                       W/2, H*0.52, fnt_med, SCORE_COLOR, center=True)
            self._text(ctx, "TAP to menu", W/2, H*0.42, fnt_small, WHITE, center=True)

        self.canvas.redraw()

    def _text(self, ctx, text, x, y, font, color, center=False):
        if center:
            # estimate center offset (~0.35 × font_size per char wide, ~1 line tall)
            est_w = len(text) * font.size * 0.55
            est_h = font.size
            x -= est_w / 2
            y -= est_h / 2
        ctx.fill(color=color)
        ctx.write_text(text, x, y, font=font)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    return GeometryDashApp(
        "Geometry Dash",
        "com.filip.geometrydash",
    )


if __name__ == "__main__":
    main().main_loop()

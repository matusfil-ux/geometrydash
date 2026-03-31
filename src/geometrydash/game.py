"""
Geometry Dash — Kivy Version
============================
Runs on Mac, iPhone, and iPad using Kivy.

How to play:
  - Tap / click / press SPACE to jump
  - Avoid the spikes!
  - Survive the timer to complete the level

How to improve:
  - Change PLAYER_COLOR to your favourite color
  - Change GRAVITY to adjust jump feel
  - Change LEVELS to add new levels
  - Add new obstacle types in the Obstacle class
"""

import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, Triangle
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from kivy.graphics.texture import Texture


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

FPS = 60

# Colors (R, G, B, A) — values 0.0 to 1.0
BG_COLOR        = (0.12, 0.12, 0.20, 1)
GROUND_COLOR    = (0.31, 0.31, 0.47, 1)
PLAYER_COLOR    = (0.0,  0.78, 1.0,  1)   # cyan — change this!
OBSTACLE_COLOR  = (1.0,  0.31, 0.31, 1)   # red
SCORE_COLOR     = (1.0,  1.0,  0.39, 1)   # yellow
WHITE           = (1.0,  1.0,  1.0,  1)
LINE_COLOR      = (0.20, 0.20, 0.31, 1)

GROUND_HEIGHT_RATIO = 0.15   # fraction of window height
PLAYER_SIZE_RATIO   = 0.10   # fraction of window height
PLAYER_X_RATIO      = 0.15   # fraction of window width

JUMP_VELOCITY   = 0.022      # fraction of window height per frame
GRAVITY         = 0.0012     # fraction of window height per frame²

OBSTACLE_WIDTH_RATIO  = 0.04
OBSTACLE_HEIGHT_RATIO = 0.13

LEVELS = [
    {"name": "Level 1 · Easy",        "speed": 0.006, "min_gap": 90,  "max_gap": 150, "duration": 60},
    {"name": "Level 2 · Medium",       "speed": 0.009, "min_gap": 70,  "max_gap": 120, "duration": 60},
    {"name": "Level 3 · Hard",         "speed": 0.013, "min_gap": 35,  "max_gap": 65,  "duration": 50},
    {"name": "Level 4 · Insane",       "speed": 0.015, "min_gap": 25,  "max_gap": 50,  "duration": 45},
    {"name": "Level 5 · Demon Ride",   "speed": 0.007, "min_gap": 20,  "max_gap": 40,  "duration": 40},
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — draw text onto canvas
# ─────────────────────────────────────────────────────────────────────────────

def make_label_texture(text: str, font_size: int, color=(1, 1, 1, 1)) -> Texture:
    label = CoreLabel(text=text, font_size=font_size, bold=True, color=color)
    label.refresh()
    return label.texture


# ─────────────────────────────────────────────────────────────────────────────
# GAME WIDGET
# ─────────────────────────────────────────────────────────────────────────────

class GameWidget(Widget):

    # ── init ──────────────────────────────────────────────────────────────────
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "menu"      # menu | level_select | playing | gameover | complete
        self.selected_level = 0
        self.coins = 0
        self.high_score = 0
        self._tick_event = None
        self._reset_game()
        self._bind_keyboard()
        self._schedule_tick()

    def _bind_keyboard(self):
        Window.bind(on_key_down=self._on_key_down)

    def _schedule_tick(self):
        if self._tick_event:
            self._tick_event.cancel()
        self._tick_event = Clock.schedule_interval(self._tick, 1.0 / FPS)

    # ── reset ─────────────────────────────────────────────────────────────────
    def _reset_game(self):
        w, h = Window.width, Window.height
        self.ground_y    = h * GROUND_HEIGHT_RATIO
        self.player_size = h * PLAYER_SIZE_RATIO
        self.player_x    = w * PLAYER_X_RATIO
        self.player_y    = self.ground_y
        self.vel_y       = 0.0
        self.on_ground   = True
        self.angle       = 0.0
        self.max_jumps   = 2
        self.jumps_left  = 2
        self.obstacles   = []          # list of {x, base_y}
        self.score       = 0
        self.level_timer = 0           # frames elapsed
        self.frames_until_next = LEVELS[self.selected_level]["min_gap"]
        self.rng         = random.Random()

    # ── keyboard ──────────────────────────────────────────────────────────────
    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        K_SPACE  = 32
        K_RETURN = 13
        K_LEFT   = 276
        K_RIGHT  = 275
        K_ESCAPE = 27
        K_r      = 114

        if self.state == "menu":
            if key == K_RETURN:
                self.state = "level_select"
        elif self.state == "level_select":
            if key == K_LEFT:
                self.selected_level = (self.selected_level - 1) % len(LEVELS)
            elif key == K_RIGHT:
                self.selected_level = (self.selected_level + 1) % len(LEVELS)
            elif key == K_RETURN:
                self._start_level()
            elif key == K_ESCAPE:
                self.state = "menu"
        elif self.state == "playing":
            if key == K_SPACE:
                self._jump()
        elif self.state in ("gameover", "complete"):
            if key == K_r:
                self._reset_game()
                self._start_level()
            elif key == K_SPACE or key == K_RETURN:
                self.state = "menu"

    def _start_level(self):
        lvl = LEVELS[self.selected_level]
        self.max_jumps = 3 if self.selected_level == 3 else (1 if self.selected_level == 4 else 2)
        self._reset_game()
        self.state = "playing"

    # ── touch ─────────────────────────────────────────────────────────────────
    def on_touch_down(self, touch):
        if self.state == "menu":
            self.state = "level_select"
        elif self.state == "level_select":
            w = Window.width
            # left half = prev, right half = next; center = start
            tx = touch.x
            if tx < w * 0.25:
                self.selected_level = (self.selected_level - 1) % len(LEVELS)
            elif tx > w * 0.75:
                self.selected_level = (self.selected_level + 1) % len(LEVELS)
            else:
                self._start_level()
        elif self.state == "playing":
            self._jump()
        elif self.state in ("gameover", "complete"):
            self.state = "menu"
        return True

    # ── jump ──────────────────────────────────────────────────────────────────
    def _jump(self):
        h = Window.height
        if self.on_ground:
            self.vel_y = JUMP_VELOCITY * h
            self.on_ground = False
            self.jumps_left = self.max_jumps - 1
        elif self.jumps_left > 0:
            self.vel_y = JUMP_VELOCITY * h
            self.jumps_left -= 1

    # ── collision ─────────────────────────────────────────────────────────────
    def _player_rect(self):
        m = self.player_size * 0.1
        return (self.player_x + m, self.player_y + m,
                self.player_size - 2*m, self.player_size - 2*m)

    def _obs_rect(self, obs):
        w  = Window.width  * OBSTACLE_WIDTH_RATIO
        h  = Window.height * OBSTACLE_HEIGHT_RATIO
        mx = w * 0.15
        return (obs["x"] + mx, obs["base_y"], w - 2*mx, h * 0.6)

    @staticmethod
    def _rects_overlap(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return x1 < x2+w2 and x1+w1 > x2 and y1 < y2+h2 and y1+h1 > y2

    # ── tick (game loop) ──────────────────────────────────────────────────────
    def _tick(self, dt):
        if self.state == "playing":
            self._update()
        self._draw()

    def _update(self):
        w, h   = Window.width, Window.height
        level  = LEVELS[self.selected_level]
        speed  = level["speed"] * w

        # player physics
        self.vel_y   -= GRAVITY * h
        self.player_y += self.vel_y
        if not self.on_ground:
            self.angle -= 5

        if self.player_y <= self.ground_y:
            self.player_y  = self.ground_y
            self.vel_y     = 0.0
            self.on_ground = True
            self.jumps_left = self.max_jumps
            self.angle     = 0.0

        # spawn obstacles
        self.frames_until_next -= 1
        if self.frames_until_next <= 0:
            self.obstacles.append({"x": w + 10, "base_y": self.ground_y, "passed": False})
            if self.rng.random() < 0.3 and self.selected_level != 4:
                ow = w * OBSTACLE_WIDTH_RATIO
                self.obstacles.append({"x": w + 10 + ow + 10, "base_y": self.ground_y, "passed": False})
            self.frames_until_next = self.rng.randint(level["min_gap"], level["max_gap"])

        # move obstacles
        for obs in self.obstacles:
            obs["x"] -= speed
            if not obs["passed"] and obs["x"] + w * OBSTACLE_WIDTH_RATIO < self.player_x:
                obs["passed"] = True
                self.score += 1
                self.coins += 1

        # remove off-screen
        self.obstacles = [o for o in self.obstacles if o["x"] + w * OBSTACLE_WIDTH_RATIO > 0]

        # collision detection
        pr = self._player_rect()
        for obs in self.obstacles:
            if self._rects_overlap(pr, self._obs_rect(obs)):
                if self.score > self.high_score:
                    self.high_score = self.score
                self.state = "gameover"
                return

        # level timer
        self.level_timer += 1
        duration = level["duration"]
        if self.level_timer >= FPS * duration:
            if self.score > self.high_score:
                self.high_score = self.score
            self.state = "complete"

    # ── draw ──────────────────────────────────────────────────────────────────
    def _draw(self):
        w, h = Window.width, Window.height
        self.canvas.clear()

        with self.canvas:
            # Background
            Color(*BG_COLOR)
            Rectangle(pos=(0, 0), size=(w, h))

            # Scrolling lines (decorative)
            Color(*LINE_COLOR)
            for i in range(0, w + 200, 200):
                x_off = (self.level_timer * 3) % 200
                lx = i - x_off
                Line(points=[lx - 200, 0, lx, h * 0.85], width=1)

            # Ground
            Color(*GROUND_COLOR)
            Rectangle(pos=(0, 0), size=(w, self.ground_y))
            Color(0.47, 0.47, 0.70, 1)
            Line(points=[0, self.ground_y, w, self.ground_y], width=2)

            # Obstacles (triangles)
            ow = w * OBSTACLE_WIDTH_RATIO
            oh = h * OBSTACLE_HEIGHT_RATIO
            Color(*OBSTACLE_COLOR)
            for obs in self.obstacles:
                ox, oy = obs["x"], obs["base_y"]
                tip = (ox + ow / 2, oy + oh)
                bl  = (ox, oy)
                br  = (ox + ow, oy)
                Triangle(points=[tip[0], tip[1], bl[0], bl[1], br[0], br[1]])
                Color(0, 0, 0, 1)
                Line(points=[tip[0], tip[1], bl[0], bl[1], br[0], br[1], tip[0], tip[1]], width=1.5)
                Color(*OBSTACLE_COLOR)

            # Player (rotated square drawn as lines)
            ps   = self.player_size
            px   = self.player_x
            py   = self.player_y
            cx   = px + ps / 2
            cy   = py + ps / 2
            ang  = math.radians(self.angle)
            corners = [(-ps/2, -ps/2), (ps/2, -ps/2), (ps/2, ps/2), (-ps/2, ps/2)]
            rotated = []
            for rx, ry in corners:
                rr = math.sqrt(rx*rx + ry*ry)
                a  = math.atan2(ry, rx) + ang
                rotated.append((cx + rr*math.cos(a), cy + rr*math.sin(a)))
            Color(*PLAYER_COLOR)
            pts = []
            for vx, vy in rotated:
                pts += [vx, vy]
            pts += [rotated[0][0], rotated[0][1]]
            # fill
            # Use a quad approximation: draw as 4-point polygon via two triangles
            r = rotated
            Triangle(points=[r[0][0], r[0][1], r[1][0], r[1][1], r[2][0], r[2][1]])
            Triangle(points=[r[0][0], r[0][1], r[2][0], r[2][1], r[3][0], r[3][1]])
            # outline
            Color(1, 1, 1, 0.6)
            Line(points=pts, width=1.5)
            # cross
            mid_top    = ((r[0][0]+r[1][0])/2, (r[0][1]+r[1][1])/2)
            mid_bottom = ((r[2][0]+r[3][0])/2, (r[2][1]+r[3][1])/2)
            mid_left   = ((r[0][0]+r[3][0])/2, (r[0][1]+r[3][1])/2)
            mid_right  = ((r[1][0]+r[2][0])/2, (r[1][1]+r[2][1])/2)
            Line(points=[mid_top[0], mid_top[1], mid_bottom[0], mid_bottom[1]], width=1)
            Line(points=[mid_left[0], mid_left[1], mid_right[0], mid_right[1]], width=1)

        # ── UI overlays ───────────────────────────────────────────────────────
        with self.canvas:
            if self.state == "menu":
                self._blit_text("GEOMETRY DASH", int(h*0.10), SCORE_COLOR, w/2, h*0.70, center=True)
                self._blit_text("TAP to continue", int(h*0.04), WHITE, w/2, h*0.55, center=True)
                self._blit_text(f"Coins: {self.coins}   Best: {self.high_score}", int(h*0.035), WHITE, w/2, h*0.45, center=True)

            elif self.state == "level_select":
                self._blit_text("SELECT LEVEL", int(h*0.07), SCORE_COLOR, w/2, h*0.80, center=True)
                self._blit_text("◀ TAP LEFT/RIGHT to browse ▶   TAP CENTRE to play", int(h*0.035), WHITE, w/2, h*0.70, center=True)
                for i, lvl in enumerate(LEVELS):
                    col = SCORE_COLOR if i == self.selected_level else WHITE
                    size_f = 0.055 if i == self.selected_level else 0.040
                    self._blit_text(f"{'▶ ' if i == self.selected_level else '  '}{lvl['name']}", int(h*size_f), col,
                                    w/2, h*(0.58 - i*0.10), center=True)

            elif self.state == "playing":
                self._blit_text(f"Score: {self.score}", int(h*0.045), SCORE_COLOR, 16, h*0.92)
                self._blit_text(f"Best: {self.high_score}", int(h*0.035), WHITE, 16, h*0.87)
                remaining = max(0, LEVELS[self.selected_level]["duration"] - self.level_timer // FPS)
                self._blit_text(f"Time: {remaining}s", int(h*0.035), WHITE, 16, h*0.82)
                self._blit_text(LEVELS[self.selected_level]["name"], int(h*0.030), (0.78, 0.78, 1.0, 1), 16, h*0.77)

            elif self.state == "gameover":
                self._blit_text("GAME OVER", int(h*0.09), OBSTACLE_COLOR, w/2, h*0.65, center=True)
                self._blit_text(f"Score: {self.score}   Best: {self.high_score}", int(h*0.05), SCORE_COLOR, w/2, h*0.53, center=True)
                self._blit_text("R to retry · TAP to menu", int(h*0.04), WHITE, w/2, h*0.43, center=True)

            elif self.state == "complete":
                self._blit_text("LEVEL COMPLETE!", int(h*0.09), (0.39, 1.0, 0.39, 1), w/2, h*0.65, center=True)
                self._blit_text(f"Score: {self.score}   Best: {self.high_score}", int(h*0.05), SCORE_COLOR, w/2, h*0.53, center=True)
                self._blit_text("R to retry · TAP to menu", int(h*0.04), WHITE, w/2, h*0.43, center=True)

    def _blit_text(self, text, font_size, color, x, y, center=False):
        tex = make_label_texture(text, font_size, color)
        if center:
            x -= tex.width / 2
            y -= tex.height / 2
        Color(1, 1, 1, 1)
        Rectangle(texture=tex, pos=(x, y), size=(tex.width, tex.height))


# ─────────────────────────────────────────────────────────────────────────────
# KIVY APP
# ─────────────────────────────────────────────────────────────────────────────

class GeometryDashApp(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.20, 1)
        return GameWidget()


def main():
    GeometryDashApp().run()


if __name__ == "__main__":
    main()

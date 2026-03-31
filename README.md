# Geometry Dash 🎮 — Python Game

**Version:** 0.1.0  
**Last Updated:** 2026-03-31  
**Platform:** macOS (Apple Silicon M1 / M2 / M3)  
**Language:** Python 3.10+  
**Dependencies:** `pygame`, `numpy` — managed with [uv](https://github.com/astral-sh/uv) + `pyproject.toml`

> 🎮 **Jump over spikes, earn coins, unlock cube colors, build your own levels — then open `game.py` and make it even better!**  
> This is a real Python package — the same structure used by professional programmers.

---

## 🗺️ What This Document Covers

| I want to… | Where to look |
|---|---|
| [Set up and run the game → Quick Start](#-quick-start) | Install uv, clone, run — 5 steps |
| [How to play → Controls](#-how-to-play) | Keys and what each screen does |
| [Understand the files → Project Structure](#-project-structure) | What each file does |
| [Change the game → Improve It!](#-improve-the-game) | Colors, speed, gravity, new features |
| [Understand the code → Code Tour](#-code-tour) | Map of game.py — classes and game loop |
| [Make an iPhone/iPad app → Mobile](#-iphone--ipad-app) | How to turn this into an iOS app |
| [Fix a problem → Troubleshooting](#-troubleshooting) | Common errors and fixes |

---

## ⚡ Quick Start

Follow these steps **in order**. Each one builds on the previous.

---

### Step 1 — Install `uv`

`uv` is a fast Python tool that creates virtual environments and installs packages for you.

Open **Terminal** (`Cmd+Space` → type `Terminal` → Enter) and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen Terminal, then check it works:

```bash
uv --version
# → uv 0.x.x
```

---

### Step 2 — Clone the repo

```bash
git clone https://github.com/matusfil-ux/geometrydash
cd geometrydash
```

> 💡 `cd geometrydash` means "go into the project folder". All the following commands must be run from inside this folder.

---

### Step 3 — Create a virtual environment

A **virtual environment** (`.venv`) is a private Python sandbox — packages installed here stay separate from everything else on your Mac.

```bash
uv venv
```

---

### Step 4 — Install dependencies

Reads `pyproject.toml` and installs `pygame` + `numpy`:

```bash
uv pip install -e .
```

> 💡 `-e .` = *editable mode* — changes you make to the code work immediately, no reinstall needed.

---

### Step 5 — Run the game! 🚀

```bash
source .venv/bin/activate
python -m geometrydash
```

A game window opens. **Press ENTER to get to level select, then ENTER again to start!**

> 💡 To quit: close the window or press `Ctrl+C` in Terminal.

---

### Every time you come back

```bash
cd geometrydash
source .venv/bin/activate
python -m geometrydash
```

---

## 🕹️ How to Play

### Main Menu

| Key | Action |
|-----|--------|
| `ENTER` | Go to level select |
| `P` | Profile (name, stars, coins, cube colour) |
| `S` | Shop (unlock new cube colours) |
| `C` | Level Editor (build your own level!) |
| `M` | Cycle game mode: Classic → Wave → Gravity |
| `A` | Quit the game |

### Level Select

| Key | Action |
|-----|--------|
| `←` / `→` | Browse levels |
| `ENTER` | Play selected level |
| `ESC` | Back to menu |

### Playing

| Key / Mouse | Action |
|-------------|--------|
| `SPACE` or click | Jump (hold for air-jump if available) |
| `M` | Toggle game mode mid-run |

### Game Over / Level Complete

| Key | Action |
|-----|--------|
| `R` | Retry the same level |
| `SPACE` or click | Back to menu |

---

### 5 Levels

| Level | Name | Difficulty | Duration | Jumps |
|-------|------|-----------|----------|-------|
| 1 | Easy | 🟢 | 80 s | 2 (double jump) |
| 2 | Medium | 🟡 | 80 s | 2 |
| 3 | Hard | 🟠 | 60 s | 2 |
| 4 | Insane Ride | 🔴 | 60 s | 3 (triple jump!) |
| 5 | Demon Ride | 💀 | 45 s | 1 (single jump only) |

### 3 Game Modes (press `M` to cycle)

| Mode | What happens |
|------|-------------|
| **Classic** | Normal — jump over spikes |
| **Wave** | Spikes move up and down in waves |
| **Gravity** | Gravity randomly changes every 5 seconds |

---

## 📁 Project Structure

```
geometrydash/
│
├── pyproject.toml              ← project config + dependencies (pygame, numpy)
├── README.md                   ← this file
│
└── src/
    └── geometrydash/
        ├── __init__.py         ← package version
        ├── __main__.py         ← makes `python -m geometrydash` work
        └── game.py             ← ⭐ THE WHOLE GAME — edit this file!
```

### What each file does

| File | What it does |
|------|-------------|
| `pyproject.toml` | Lists `pygame` and `numpy` as dependencies. `uv pip install -e .` reads this. |
| `src/geometrydash/game.py` | Player, obstacles, levels, shop, editor, game loop. **Edit this!** |
| `src/geometrydash/__main__.py` | Called by `python -m geometrydash`. Calls `main()` from `game.py`. |
| `src/geometrydash/__init__.py` | Marks the folder as a Python package. |

---

## 🎨 Improve the Game

Open `src/geometrydash/game.py` in VS Code:

```bash
code src/geometrydash/game.py
```

Look for the **SETTINGS** block near the top:

```python
# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS — change these to tweak the game!
# ─────────────────────────────────────────────────────────────────────────────
```

After every change: save (`Cmd+S`), then run again.

---

### 🟢 Easy — Change colors

```python
PLAYER_COLOR = (0, 200, 255)    # cyan  ← try (255, 100, 0) for orange
OBSTACLE_COLOR = (255, 80, 80)  # red   ← try (0, 200, 100) for green
BACKGROUND_COLOR = (30, 30, 50) # dark  ← try (0, 0, 0) for pure black
```

---

### 🟢 Easy — Add a new cube color to the shop

Find `ICON_COLORS` in the SETTINGS:

```python
ICON_COLORS = [
    (0, 200, 255),   # default cyan
    (255, 100, 100), # red
    (100, 255, 100), # green
    (255, 255, 100), # yellow
    (255, 0, 255),   # magenta
]
```

Add your own color to the list — e.g. for white:

```python
    (255, 255, 255), # white ← add this line
```

---

### 🟡 Medium — Change level difficulty

Find the `LEVELS` list and change numbers:

```python
LEVELS = [
    {"name": "Level 1 - Easy", "speed": 5, "min_gap": 90, "max_gap": 150, "duration": 80, ...},
    ...
]
```

| Setting | What it does |
|---------|-------------|
| `speed` | How fast spikes scroll (pixels/frame) |
| `min_gap` / `max_gap` | Minimum/maximum frames between spikes |
| `duration` | How many seconds you need to survive |
| `block_chance` | Probability (0–1) of a wide block instead of a spike |

---

### 🟡 Medium — Change physics

```python
JUMP_VELOCITY = -14   # bigger = higher jump (try -18 for moon jump)
GRAVITY = 0.7         # bigger = falls faster (try 0.4 for floaty)
```

> ⚠️ `JUMP_VELOCITY` must stay **negative** (minus = upward).

---

### 🟠 Medium — Add a new level

Find `LEVELS` and add a dict at the end:

```python
{"name": "Level 6 - My Level", "speed": 8, "min_gap": 50, "max_gap": 90,
 "score_to_next": 9999, "block_chance": 0.2, "duration": 60},
```

---

### 🔴 Hard — Add a new obstacle shape

After the `Obstacle` class, add:

```python
class TallObstacle(Obstacle):
    """A tall thin spike — harder to jump over!"""
    def __init__(self, x: int) -> None:
        super().__init__(x)
        self.width = 15    # narrower
        self.height = 80   # much taller
```

Then in `make_obs()` inside `run_game()`, randomly use it:

```python
if level_rng.random() < 0.2:
    base = TallObstacle(WINDOW_WIDTH + 10)
else:
    base = Obstacle(WINDOW_WIDTH + 10)
```

---

### 🔴 Hard — Add a high score leaderboard (save to file)

At the top of `run_game()`, after `high_score = 0`, load from a file:

```python
import json, pathlib
SAVE_FILE = pathlib.Path("scores.json")
if SAVE_FILE.exists():
    high_score = json.loads(SAVE_FILE.read_text()).get("high_score", 0)
```

Where `high_score` is updated, also save it:

```python
if score > high_score:
    high_score = score
    SAVE_FILE.write_text(json.dumps({"high_score": high_score}))
```

---

## 🧭 Code Tour

```
game.py
│
├── SETTINGS block         ← colors, sizes, speed, gravity, levels — start here!
│
├── class Player           ← the spinning cube you control
│   ├── reset()            ← puts the player at the start
│   ├── jump()             ← fires on SPACE — handles multi-jump too
│   ├── update(gravity)    ← gravity, landing, spin rotation
│   ├── get_rect()         ← collision box
│   └── draw()             ← spinning cube with cross pattern
│
├── class Obstacle         ← a red triangle spike
│   └── draw() / get_rect() / update() / is_offscreen()
│
├── class WaveObstacle     ← spike that moves up/down (wave mode)
│   └── inherits Obstacle, overrides update() and draw()
│
├── class Background       ← scrolling diagonal lines
│
├── draw_text()            ← helper to draw any text on screen
│
├── generate_death_sound() ← uses numpy to make a descending beep sound
│
└── run_game()             ← THE MAIN GAME LOOP ⭐
    ├── Events             ← keyboard/mouse input for all screens
    ├── Update             ← move player, spawn/move obstacles, count score
    │                          level timer, gravity mode, custom level playback
    └── Draw               ← draw the right screen:
        ├── "menu"         ← title screen
        ├── "level_select" ← pick a level
        ├── "profile"      ← name, stars, coins, cube colour
        ├── "shop"         ← unlock cube colours with coins
        ├── "editor"       ← build your own level with arrow keys
        ├── "playing"      ← HUD: score, coins, mode, jumps, timer
        ├── "gameover"     ← red death marker, retry or menu
        └── "level_complete" ← success screen
```

### The Game Loop

Every game (Minecraft, Fortnite, this one) runs a loop **60 times per second**:

```
while True:
    1. Read input   ← keyboard / mouse
    2. Update       ← move everything, check collisions, count score
    3. Draw         ← clear screen, draw everything
    4. Wait         ← pause until 1/60 s has passed
    → repeat
```

---

## 📱 iPhone / iPad App

> 🍎 **Yes, you can turn this pygame game into an iPhone or iPad app!**

📄 **Full step-by-step guide: [DEPLOY_IOS.md](DEPLOY_IOS.md)**

The guide covers:
- Installing Xcode and signing in with your Apple ID (free)
- Swapping `pygame` → `pygame-ce` (drop-in replacement that works on mobile)
- Adding finger-tap controls to `game.py`
- Running in the iOS Simulator on your Mac (no cable needed)
- Installing on a **real iPhone or iPad** via USB cable
- Re-signing after 7 days (takes 30 seconds)
- Troubleshooting common errors

### Quick summary

| Step | Command |
|------|---------|
| Install Briefcase | `uv pip install briefcase` |
| Create iOS project | `briefcase create iOS` |
| Build | `briefcase build iOS` |
| Run in Simulator | `briefcase run iOS` |
| Run on real device | `briefcase run iOS --device "iPhone Name"` |
| Update after code changes | `briefcase update iOS && briefcase run iOS` |

> 📌 **Start with [DEPLOY_IOS.md](DEPLOY_IOS.md)** — it walks you through every step from zero to a working app on your iPhone.

---

## 🔍 Troubleshooting

---

### ❌ `ModuleNotFoundError: No module named 'pygame'`

Virtual environment not activated or not installed.

**Fix:**
```bash
source .venv/bin/activate
uv pip install -e .
python -m geometrydash
```

---

### ❌ `ModuleNotFoundError: No module named 'numpy'`

Same fix as above — `numpy` is installed alongside `pygame`.

```bash
uv pip install -e .
```

---

### ❌ `ModuleNotFoundError: No module named 'geometrydash'`

Package not installed in editable mode.

**Fix:**
```bash
uv pip install -e .
```

---

### ❌ `uv: command not found`

Close Terminal fully, reopen, and try again. If still missing:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### ❌ Window opens but nothing happens

Press **ENTER** on the main menu, then **ENTER** again on level select to start playing.

---

### ❌ `(.venv)` not showing in terminal prompt

```bash
source .venv/bin/activate
```

---

## 🔗 Quick Reference

| Task | Command |
|------|---------|
| Create virtual environment | `uv venv` |
| Install / update dependencies | `uv pip install -e .` |
| Activate virtual environment | `source .venv/bin/activate` |
| **Run the game** | `python -m geometrydash` |
| Edit the game | `code src/geometrydash/game.py` |
| Add a new package | Add to `dependencies` in `pyproject.toml`, then `uv pip install -e .` |
| Pull latest from Filip's branch | `git fetch matusfil && git checkout matusfil/version1 -- src/geometrydash/game.py` |

---

> 🚀 **Beat Level 5 Demon Ride — then start building the iPhone version!**

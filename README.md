# 🎮 Geometry Dash — Python Game

**Version:** 0.1.0 · **Python:** 3.11 · **Package manager:** [uv](https://github.com/astral-sh/uv)

> Jump over spikes, earn coins, unlock cube colors, build your own levels —  
> then open `game.py` and make it even better!

---

## 📋 Contents

| # | What I want to do | Jump to |
|---|---|---|
| 1 | Install and run on Mac | [▶ Mac Quick Start](#1--mac-quick-start) |
| 2 | Learn the controls | [🕹 How to Play](#2--how-to-play) |
| 3 | Understand the files | [📁 Project Structure](#3--project-structure) |
| 4 | Tweak and improve the game | [🎨 Improve the Game](#4--improve-the-game) |
| 5 | Read the code | [🧭 Code Tour](#5--code-tour) |
| 6 | Put it on iPhone or iPad | [📱 Deploy to iPhone / iPad](#6--deploy-to-iphone--ipad) |
| 7 | Fix a problem | [🔍 Troubleshooting](#7--troubleshooting) |

---

## 1 · Mac Quick Start

> ⏱ Takes about 5 minutes the first time.

### Step 1 — Install `uv`

`uv` creates virtual environments and installs packages — much faster than plain pip.

Open **Terminal** (`Cmd+Space` → type `Terminal` → Enter):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen Terminal, then check:

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

> 💡 All following commands must be run from inside the `geometrydash` folder.

---

### Step 3 — Create a virtual environment with Python 3.11

```bash
uv venv --python 3.11
```

> ⚠️ Use Python **3.11** — not 3.12, 3.13, or 3.14. The iOS deploy tools require 3.11.

If Python 3.11 is not installed:
```bash
brew install python@3.11
uv venv --python 3.11
```

---

### Step 4 — Install dependencies

```bash
source .venv/bin/activate
uv pip install pygame-ce numpy
uv pip install -e .
```

> 💡 `-e .` = editable mode — changes you make to `game.py` work immediately, no reinstall needed.

---

### Step 5 — Run the game 🚀

```bash
python -m geometrydash
```

A window opens. **Press ENTER to reach level select, then ENTER again to start!**

---

### Every time you come back

```bash
cd geometrydash
source .venv/bin/activate
python -m geometrydash
```

---

## 2 · How to Play

### Main Menu

| Key | Action |
|-----|--------|
| `ENTER` | Go to level select |
| `P` | Profile — set your name, see stars & coins, pick cube colour |
| `S` | Shop — spend coins to unlock new cube colours |
| `C` | Level Editor — build your own level! |
| `M` | Cycle game mode: Classic → Wave → Gravity |
| `A` | Quit |

### Level Select

| Key | Action |
|-----|--------|
| `←` / `→` | Browse levels |
| `ENTER` | Play selected level |
| `ESC` | Back to menu |

### Playing

| Key / Mouse | Action |
|-------------|--------|
| `SPACE` or click | Jump |
| `M` | Switch game mode mid-run |

### Game Over / Complete

| Key | Action |
|-----|--------|
| `R` | Retry |
| `SPACE` or click | Back to menu |

---

### 5 Levels

| # | Name | Difficulty | Duration | Jumps |
|---|------|-----------|----------|-------|
| 1 | Easy | 🟢 | 80 s | 2 (double jump) |
| 2 | Medium | 🟡 | 80 s | 2 |
| 3 | Hard | 🟠 | 60 s | 2 |
| 4 | Insane Ride | 🔴 | 60 s | 3 (triple jump!) |
| 5 | Demon Ride | 💀 | 45 s | 1 (single jump only) |

### 3 Game Modes

| Mode | What happens |
|------|-------------|
| **Classic** | Normal — jump over spikes |
| **Wave** | Spikes move up and down in waves |
| **Gravity** | Gravity randomly flips every 5 seconds |

---

## 3 · Project Structure

```
geometrydash/
│
├── pyproject.toml          ← project config + iOS/macOS dependency settings
├── README.md               ← this file
│
└── src/
    └── geometrydash/
        ├── __init__.py     ← package version
        ├── __main__.py     ← makes `python -m geometrydash` work
        └── game.py         ← ⭐ THE WHOLE GAME — edit this!
```

| File | What it does |
|------|-------------|
| `pyproject.toml` | Declares dependencies for Mac and iPhone separately. |
| `game.py` | Player, obstacles, levels, shop, editor, game loop. **Edit this!** |
| `__main__.py` | Entry point called by `python -m geometrydash`. |
| `__init__.py` | Marks the folder as a Python package. |

---

## 4 · Improve the Game

Open `game.py` in VS Code:

```bash
code src/geometrydash/game.py
```

Find the **SETTINGS block** near the top — every tweak starts there.  
After each change: save (`Cmd+S`), then run again.

---

### 🟢 Easy — Change colors

```python
PLAYER_COLOR    = (0, 200, 255)    # cyan  → try (255, 100, 0) for orange
OBSTACLE_COLOR  = (255, 80, 80)    # red   → try (0, 200, 100) for green
BACKGROUND_COLOR = (30, 30, 50)    # dark  → try (0, 0, 0) for pure black
```

---

### 🟢 Easy — Add a cube color to the shop

Find `ICON_COLORS` in the SETTINGS and add a new line:

```python
ICON_COLORS = [
    (0, 200, 255),   # cyan (default)
    (255, 100, 100), # red
    (100, 255, 100), # green
    (255, 255, 100), # yellow
    (255, 0, 255),   # magenta
    (255, 255, 255), # white  ← add this!
]
```

---

### 🟡 Medium — Change physics

```python
JUMP_VELOCITY = -14   # higher number = bigger jump  (try -18 for moon jump)
GRAVITY       = 0.7   # higher = falls faster         (try 0.4 for floaty)
```

> ⚠️ `JUMP_VELOCITY` must stay **negative** (minus = up).

---

### 🟡 Medium — Change level difficulty

```python
LEVELS = [
    {"name": "Level 1 - Easy", "speed": 5, "min_gap": 90, "max_gap": 150, "duration": 80, ...},
]
```

| Setting | What it does |
|---------|-------------|
| `speed` | How fast obstacles scroll (pixels/frame) |
| `min_gap` / `max_gap` | Frames between obstacles |
| `duration` | Seconds you need to survive |
| `block_chance` | 0–1 chance of a block instead of a spike |

---

### 🟠 Medium — Add a new level

Append to the `LEVELS` list:

```python
{"name": "Level 6 - My Level", "speed": 8, "min_gap": 50, "max_gap": 90,
 "score_to_next": 9999, "block_chance": 0.2, "duration": 60},
```

---

### 🔴 Hard — New obstacle shape

```python
class TallObstacle(Obstacle):
    """A tall thin spike."""
    def __init__(self, x: int) -> None:
        super().__init__(x)
        self.width  = 15
        self.height = 80
```

Then in `make_obs()` inside `run_game()`:

```python
if level_rng.random() < 0.2:
    base = TallObstacle(WINDOW_WIDTH + 10)
else:
    base = Obstacle(WINDOW_WIDTH + 10)
```

---

### 🔴 Hard — Save high score to a file

After `high_score = 0`, add:

```python
import json, pathlib
SAVE_FILE = pathlib.Path("scores.json")
if SAVE_FILE.exists():
    high_score = json.loads(SAVE_FILE.read_text()).get("high_score", 0)
```

Where `high_score` is updated:

```python
if score > high_score:
    high_score = score
    SAVE_FILE.write_text(json.dumps({"high_score": high_score}))
```

---

## 5 · Code Tour

```
game.py
│
├── SETTINGS block          ← start here — colors, speed, gravity, levels
│
├── class Player            ← the spinning cube you control
│   ├── jump()              ← fires on SPACE / tap
│   ├── update(gravity)     ← gravity, landing, rotation
│   └── draw()              ← spinning cube with cross pattern
│
├── class Obstacle          ← red triangle spike
├── class WaveObstacle      ← spike that bobs up/down (wave mode)
├── class Background        ← scrolling diagonal lines
│
├── draw_text()             ← helper to draw text anywhere on screen
├── generate_death_sound()  ← descending beep on death (pure Python, no numpy on iOS)
│
└── run_game()              ← THE MAIN LOOP ⭐
    ├── Events              ← keyboard / mouse / finger input
    ├── Update              ← move everything, check collisions, count score
    └── Draw                ← pick the right screen and draw it
        ├── "menu"
        ├── "level_select"
        ├── "profile"
        ├── "shop"
        ├── "editor"
        ├── "playing"       ← HUD: score, coins, mode, timer
        ├── "gameover"
        └── "level_complete"
```

### The Game Loop (60 times per second)

```
while True:
    1. Read input   ← SPACE, mouse click, finger tap
    2. Update       ← move player + obstacles, check collisions, add score
    3. Draw         ← clear screen, draw everything
    4. Wait         ← pause until 1/60 s has passed
```

---

## 6 · Deploy to iPhone / iPad

> 🍎 Turn your Python game into a real iPhone app using **BeeWare Briefcase**.  
> You need a free Apple ID — no $99/year developer account required.

---

### What you need (one-time setup)

| Tool | How to get it |
|------|--------------|
| **Xcode** (~9 GB) | Mac App Store → search Xcode → Install |
| **iOS Runtime** (~9 GB) | Xcode will prompt you the first time — click Download & Install |
| **Apple ID** | Already have one if you use an iPhone |
| **briefcase** | `uv pip install briefcase` (see below) |

> ⏱ Plan for 1–2 hours the first time — mostly waiting for downloads.

---

### Step 1 — Install Xcode

1. Open **App Store** → search **Xcode** → Install
2. After installing, open Xcode once (it installs extra components)
3. In Terminal:
   ```bash
   xcode-select --install
   sudo xcodebuild -license accept
   ```

---

### Step 2 — Sign in with your Apple ID in Xcode

1. Open **Xcode** → menu **Xcode** → **Settings** → **Accounts** tab
2. Click **+** → **Apple ID** → sign in

---

### Step 3 — Install briefcase and downgrade pip

```bash
cd geometrydash
source .venv/bin/activate
uv pip install briefcase
uv pip install "pip==23.3.2"   # required — newer pip crashes on iOS cross-compilation
```

---

### Step 4 — Update pyproject.toml

Make sure your `pyproject.toml` matches this **exactly** (copy-paste the whole file):

```toml
[project]
name = "geometrydash"
version = "0.1.0"
description = "A simple Geometry Dash game in Python"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.scripts]
geometrydash = "geometrydash.game:main"

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.briefcase]
project_name = "Geometry Dash"
bundle = "com.filip.geometrydash"
version = "0.1.0"
url = "https://github.com/matusfil-ux/geometrydash"
license = "MIT"
author = "Filip"
author_email = "matus.fil@gmail.com"

[tool.briefcase.app.geometrydash]
formal_name = "Geometry Dash"
description = "Jump over spikes, earn coins, build levels!"
sources = ["src/geometrydash"]
requires = []

[tool.briefcase.app.geometrydash.macOS]
requires = [
    "pygame-ce>=2.5.0",
    "numpy>=1.24.0",
]

[tool.briefcase.app.geometrydash.iOS]
requires = []
minimum_os_version = "16.0"
```

> ⚠️ `dependencies = []` is intentional — briefcase would otherwise try to install `pygame-ce` on iOS where there are no wheels. Install it manually for Mac dev with `uv pip install pygame-ce numpy`.

---

### Step 5 — Add touch controls to game.py

iPhones have no keyboard — finger taps must make the player jump. Open `game.py` and find the jump detection:

```python
jump = (
    (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
    or event.type == pygame.MOUSEBUTTONDOWN
)
```

**Add one line:**

```python
jump = (
    (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
    or event.type == pygame.MOUSEBUTTONDOWN
    or event.type == pygame.FINGERDOWN        # ← finger tap on touchscreen
)
```

Save (`Cmd+S`), then reinstall:
```bash
uv pip install -e .
```

---

### Step 6 — Create the Xcode project

```bash
briefcase create iOS
```

Expected output ends with:
```
[geometrydash] Created build/geometrydash/ios/xcode
```

---

### Step 7 — Open in Xcode

```bash
open "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"
```

---

### Step 8 — Connect your iPhone

1. Plug your iPhone into the Mac with a USB cable
2. On your iPhone: tap **Trust** when asked "Trust This Computer?"
3. Wait ~10 seconds for Xcode to recognise the device

---

### Step 9 — Select your device and fix signing

1. In Xcode **top bar** — click the device selector and pick your **iPhone** (not a simulator)
2. In the **left panel** click the blue **Geometry Dash** project icon
3. Click the **Geometry Dash** target → **Signing & Capabilities** tab
4. Under **Team** — click the dropdown → click **"Add an Account..."**
5. Sign in with your Apple ID (the Gmail you used for `matusfil-ux`)
6. After adding, select **your personal team** from the Team dropdown
7. Press `Cmd+R`

> ⚠️ **If Xcode asks for a Keychain password** (e.g. "codesign wants access to key Apple Development: Rastislav Matus"):
> - This happens when the certificate belongs to a different user account on the Mac
> - **Fix:** In **Team** dropdown → **Add an Account...** → add **your own** Apple ID → select your team
> - Your certificate goes into your own keychain → no password conflict

> ⚠️ **If "This Apple account cannot be used for development":**
> - The Mac user account needs admin rights
> - Fix: run Xcode as admin:
>   ```bash
>   sudo open -a Xcode "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"
>   ```

---

### Step 10 — Install iOS Device Support (first time)

When you press `Cmd+R` for the first time, Xcode may prompt:

> *"iOS Device Support files for iPhone (iOS xx.x) are required"*

Click **Download and Install** (~9 GB, one-time per iOS version).  
This is required and cannot be skipped.

---

### Step 11 — Build and run 🚀

Press **`Cmd+R`** in Xcode.

Xcode will:
1. Compile the app
2. Install it on your iPhone
3. Launch it automatically

---

### Step 12 — Trust the developer on your iPhone (first time)

On your iPhone:
1. **Settings** → **General** → **VPN & Device Management**
2. Tap your Apple ID under **Developer App**
3. Tap **Trust** → **Trust** again

Open the app from your home screen — it works! 🎉

---

### After code changes

```bash
briefcase update iOS
```

Then press `Cmd+R` in Xcode again.

---

### Re-sign after 7 days

Free Apple IDs expire after 7 days. Just press `Cmd+R` in Xcode again — it re-signs automatically.

---

### Quick reference — iOS deploy

| Task | Command |
|------|---------|
| Install briefcase | `uv pip install briefcase` |
| Downgrade pip (required) | `uv pip install "pip==23.3.2"` |
| Create Xcode project | `briefcase create iOS` |
| Open in Xcode | `open "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"` |
| Build & run | `Cmd+R` in Xcode |
| Update after code change | `briefcase update iOS` → `Cmd+R` |

---

## 7 · Troubleshooting

---

### ❌ `ModuleNotFoundError: No module named 'pygame'`

```bash
source .venv/bin/activate
uv pip install pygame-ce numpy
python -m geometrydash
```

---

### ❌ `uv: command not found`

Close Terminal, reopen, and try again. If still missing:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### ❌ `uv venv --python 3.11` fails — Python 3.11 not found

```bash
brew install python@3.11
uv venv --python 3.11.15
```

---

### ❌ `briefcase create iOS` — `No matching distribution found for pygame-ce`

Your `pyproject.toml` `dependencies` section still lists `pygame-ce`. Set it to empty:
```toml
dependencies = []
```
And re-run `briefcase create iOS`.

---

### ❌ `briefcase create iOS` — `AttributeError: module 'platform' has no attribute 'ios_ver'`

pip version is too new. Downgrade:
```bash
uv pip install "pip==23.3.2"
rm -rf build
briefcase create iOS
```

---

### ❌ `briefcase build iOS` — `No available simulator runtimes`

This only affects the simulator. **Use the real iPhone instead** — open the Xcode project and select your phone in the device selector. No simulator runtime needed for real devices.

---

### ❌ Xcode — `This Apple account cannot be used for development`

The Mac user account is not an administrator. Run Xcode with admin rights:
```bash
sudo open -a Xcode "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"
```

---

### ❌ Xcode — `Signing certificate not found`

1. Xcode → **Settings** → **Accounts** → select your Apple ID → **Manage Certificates**
2. Click **+** → **Apple Development**
3. Try `Cmd+R` again

---

### ❌ iPhone shows "Untrusted Developer"

Settings → General → VPN & Device Management → tap Apple ID → **Trust**

---

### ❌ Window opens but nothing happens

Press **ENTER** on the main menu, then **ENTER** again on level select.

---

### ❌ `(.venv)` not showing in Terminal

```bash
source .venv/bin/activate
```

---

## 🔗 Quick Reference

| Task | Command |
|------|---------|
| Create venv (Python 3.11) | `uv venv --python 3.11` |
| Activate venv | `source .venv/bin/activate` |
| Install game deps | `uv pip install pygame-ce numpy && uv pip install -e .` |
| **Run the game** | `python -m geometrydash` |
| Edit the game | `code src/geometrydash/game.py` |
| iOS: create Xcode project | `briefcase create iOS` |
| iOS: open in Xcode | `open "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"` |
| iOS: build & run | `Cmd+R` in Xcode |
| iOS: update after changes | `briefcase update iOS` → `Cmd+R` |

---

> 🚀 **Beat Level 5 Demon Ride — then deploy it to your iPhone and show your friends!**

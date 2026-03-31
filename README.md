# 🎮 Geometry Dash — Python Game

**Version:** 0.1.0 · **Python:** 3.11 · **Package manager:** [uv](https://github.com/astral-sh/uv) · **Framework:** [Kivy](https://kivy.org)

> Jump over spikes, earn coins, unlock cube colors, build your own levels —  
> then open `game.py` and make it even better!  
> Runs on **Mac**, **iPhone**, and **iPad**.

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

---

### Step 3 — Create a virtual environment with Python 3.11

```bash
uv venv --python 3.11
```

If Python 3.11 is not installed:
```bash
brew install python@3.11
uv venv --python 3.11
```

---

### Step 4 — Install dependencies

```bash
source .venv/bin/activate
uv pip install "kivy[base]"
uv pip install -e .
```

> 💡 `-e .` = editable mode — changes you make to `game.py` work immediately, no reinstall needed.

---

### Step 5 — Run the game 🚀

```bash
python -m geometrydash
```

A window opens. **Tap or click to jump!**

---

### Every time you come back

```bash
cd geometrydash
source .venv/bin/activate
python -m geometrydash
```

---

## 2 · How to Play

### Controls

| Key / Touch | Action |
|-------------|--------|
| **Tap / Click** | Jump |
| `SPACE` | Jump |
| `ENTER` | Confirm / start |
| `←` / `→` | Browse levels |
| `R` | Retry after game over |
| `ESC` | Back to menu |

### Screens

| Screen | How to navigate |
|--------|----------------|
| **Menu** | Tap anywhere → Level Select |
| **Level Select** | Tap left quarter = previous level · Tap right quarter = next level · Tap centre = play |
| **Playing** | Tap / SPACE to jump |
| **Game Over** | `R` to retry · Tap to go back to menu |
| **Level Complete** | `R` to retry · Tap to go back to menu |

### 5 Levels

| # | Name | Difficulty | Jumps |
|---|------|-----------|-------|
| 1 | Easy | 🟢 | double jump |
| 2 | Medium | 🟡 | double jump |
| 3 | Hard | 🟠 | double jump |
| 4 | Insane | 🔴 | triple jump! |
| 5 | Demon Ride | 💀 | single jump only |

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

---

## 4 · Improve the Game

Open `game.py` in VS Code:

```bash
code src/geometrydash/game.py
```

Find the **SETTINGS block** near the top. After each change: save (`Cmd+S`), then run again.

---

### 🟢 Easy — Change the player color

Colors use values from 0.0 to 1.0 (not 0–255):

```python
PLAYER_COLOR = (0.0, 0.78, 1.0, 1)   # cyan (default)
```

Try these:
```python
PLAYER_COLOR = (1.0, 0.39, 0.0, 1)   # orange
PLAYER_COLOR = (0.39, 1.0, 0.39, 1)  # green
PLAYER_COLOR = (1.0, 0.0, 1.0, 1)    # magenta
```

---

### 🟢 Easy — Change obstacle color

```python
OBSTACLE_COLOR = (1.0, 0.31, 0.31, 1)  # red (default)
OBSTACLE_COLOR = (1.0, 0.78, 0.0,  1)  # yellow
```

---

### 🟡 Medium — Change physics

```python
JUMP_VELOCITY = 0.022   # higher = bigger jump  (try 0.030 for moon jump)
GRAVITY       = 0.0012  # higher = falls faster  (try 0.0006 for floaty)
```

---

### 🟡 Medium — Change level difficulty

```python
LEVELS = [
    {"name": "Level 1 · Easy", "speed": 0.006, "min_gap": 90, "max_gap": 150, "duration": 60},
]
```

| Setting | What it does |
|---------|-------------|
| `speed` | Fraction of screen width per frame (bigger = faster) |
| `min_gap` / `max_gap` | Frames between obstacles (smaller = harder) |
| `duration` | Seconds you need to survive |

---

### 🟠 Medium — Add a new level

Append to the `LEVELS` list:

```python
{"name": "Level 6 · My Level", "speed": 0.011, "min_gap": 40, "max_gap": 80, "duration": 55},
```

---

### 🔴 Hard — Change background color

```python
BG_COLOR = (0.12, 0.12, 0.20, 1)   # dark blue (default)
BG_COLOR = (0.0,  0.0,  0.0,  1)   # pure black
BG_COLOR = (0.05, 0.15, 0.05, 1)   # dark green
```

---

## 5 · Code Tour

```
game.py
│
├── SETTINGS block          ← start here — colors, speed, gravity, levels
│
├── make_label_texture()    ← helper: renders text onto the canvas
│
└── class GameWidget        ← THE WHOLE GAME ⭐
    │
    ├── __init__()          ← set up state, keyboard, start clock
    ├── _reset_game()       ← reset player/obstacles for a new game
    ├── _on_key_down()      ← keyboard input
    ├── on_touch_down()     ← tap/click input (works on iPhone too!)
    ├── _jump()             ← fires on tap / SPACE
    ├── _tick()             ← called 60 times per second
    ├── _update()           ← move everything, check collisions, count score
    └── _draw()             ← draw background, ground, obstacles, player, UI
```

### The Game Loop (60 times per second)

```
Clock calls _tick() →
    1. _update()  ← move player + obstacles, check collisions
    2. _draw()    ← clear canvas, draw everything
```

### How Kivy drawing works

```python
with self.canvas:
    Color(1.0, 0.0, 0.0, 1)              # set color to red (R, G, B, A)
    Rectangle(pos=(x, y), size=(w, h))   # draw a filled rectangle
    Triangle(points=[x1,y1, x2,y2, x3,y3])  # draw a filled triangle
    Line(points=[x1,y1, x2,y2], width=2)    # draw a line
```

---

## 6 · Deploy to iPhone / iPad

> 🍎 Turn your Python game into a real iPhone/iPad app using **BeeWare Briefcase** + **Kivy**.  
> You need a **free Apple ID** — no $99/year developer account required.

---

### What you need (one-time setup)

| Tool | How to get it |
|------|--------------|
| **Xcode** (~9 GB) | Mac App Store → search Xcode → Install |
| **iOS Runtime** (~9 GB) | Xcode will prompt you the first time |
| **Apple ID** | Any Gmail or iCloud account |
| **briefcase** | `uv pip install briefcase` (see below) |

> ⏱ Plan for 1–2 hours the first time — mostly waiting for downloads.

---

### Step 1 — Install Xcode

1. **App Store** → search **Xcode** → Install
2. After installing, open Xcode once (it installs extra components)
3. In Terminal:
   ```bash
   xcode-select --install
   sudo xcodebuild -license accept
   ```

---

### Step 2 — Sign in with your Apple ID in Xcode

1. Open **Xcode** → menu **Xcode** → **Settings** → **Accounts** tab
2. Click **+** → **Apple ID** → sign in with any Apple ID

> 💡 **You can use any Apple ID** — it doesn't need to match GitHub or iCloud on the iPhone.  
> The Apple ID is only used for the developer certificate.

---

### Step 3 — Install briefcase and downgrade pip

```bash
cd geometrydash
source .venv/bin/activate
uv pip install briefcase
uv pip install "pip==23.3.2"   # required — newer pip crashes on iOS cross-compilation
```

---

### Step 4 — Check pyproject.toml iOS section

Make sure your `pyproject.toml` has this iOS section (it already does if you cloned the repo):

```toml
[tool.briefcase.app.geometrydash.iOS]
requires = [
    "kivy",
]
minimum_os_version = "16.0"
```

---

### Step 5 — Create the Xcode project

```bash
briefcase create iOS
```

Expected output ends with:
```
[geometrydash] Created build/geometrydash/ios/xcode
```

---

### Step 6 — Open in Xcode

```bash
open "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"
```

---

### Step 7 — Connect your iPhone or iPad

1. Plug your device into the Mac with a USB cable
2. On the device: tap **Trust** when asked "Trust This Computer?"
3. Wait ~10 seconds for Xcode to recognise the device

---

### Step 8 — Select device and fix signing

1. In Xcode **top bar** → click device selector → pick your **iPhone/iPad**
2. Left panel → click blue **Geometry Dash** project icon
3. **Geometry Dash** target → **Signing & Capabilities** tab
4. **Team** dropdown → **"Add an Account..."**
5. Sign in with **any Apple ID** you want to use
6. Select **that account's personal team**
7. Press **`Cmd+R`**

> ⚠️ **If Xcode asks for Keychain password (e.g. "Apple Development: Rastislav Matus")**:
> - The certificate belongs to a different Mac user account
> - Fix: add **your own** Apple ID → Xcode creates a new cert in your keychain → no conflict

> ⚠️ **To switch Apple IDs**: Team dropdown → Add an Account... → pick different account

---

### Step 9 — Install iOS Device Support (first time)

If Xcode prompts *"iOS Device Support files required"* → click **Download and Install** (~9 GB, one-time).

---

### Step 10 — Build and run 🚀

Press **`Cmd+R`** in Xcode → app compiles, installs, and launches on your device.

---

### Step 11 — Trust the developer on your device (first time)

On iPhone/iPad:
1. **Settings** → **General** → **VPN & Device Management**
2. Tap your Apple ID → **Trust** → **Trust** again

Open app from home screen → it runs! 🎉

---

### After code changes

```bash
briefcase update iOS
```

Then press `Cmd+R` in Xcode.

---

### Re-sign after 7 days

Free Apple IDs expire after 7 days. Press `Cmd+R` in Xcode — it re-signs automatically.

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

### ❌ `ModuleNotFoundError: No module named 'kivy'`

```bash
source .venv/bin/activate
uv pip install "kivy[base]"
python -m geometrydash
```

---

### ❌ `uv: command not found`

Close Terminal, reopen, and try again. If still missing:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### ❌ `uv venv --python 3.11` fails

```bash
brew install python@3.11
uv venv --python 3.11
```

---

### ❌ `briefcase create iOS` — `AttributeError: module 'platform' has no attribute 'ios_ver'`

pip version is too new. Downgrade:
```bash
uv pip install "pip==23.3.2"
rm -rf build
briefcase create iOS
```

---

### ❌ Xcode — `This Apple account cannot be used for development`

The Mac user is not an admin. Run Xcode with admin rights:
```bash
sudo open -a Xcode "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"
```

---

### ❌ Xcode — Keychain password dialog appears

The certificate belongs to a different Mac user account. Fix:
- Xcode → **Signing & Capabilities** → **Team** → **Add an Account...** → add your own Apple ID → select your team

---

### ❌ iPhone shows "Untrusted Developer"

**Settings** → **General** → **VPN & Device Management** → tap Apple ID → **Trust**

---

### ❌ App starts but immediately crashes on iPhone

Check Xcode console (bottom panel) for red text. Most common cause: kivy not bundled.
Run:
```bash
briefcase update iOS --update-requirements
```
Then `Cmd+R` in Xcode.

---

### ❌ Window opens but game doesn't respond to keyboard

Make sure you clicked on the game window first to give it focus, then press SPACE or ENTER.

---

## 🔗 Quick Reference

| Task | Command |
|------|---------|
| Create venv (Python 3.11) | `uv venv --python 3.11` |
| Activate venv | `source .venv/bin/activate` |
| Install game deps | `uv pip install "kivy[base]" && uv pip install -e .` |
| **Run the game** | `python -m geometrydash` |
| Edit the game | `code src/geometrydash/game.py` |
| iOS: create Xcode project | `briefcase create iOS` |
| iOS: open in Xcode | `open "build/geometrydash/ios/xcode/Geometry Dash.xcodeproj"` |
| iOS: build & run | `Cmd+R` in Xcode |
| iOS: update after changes | `briefcase update iOS` → `Cmd+R` |

---

> 🚀 **Beat Level 5 Demon Ride — then deploy it to your iPhone and show your friends!**

# Deploy Geometry Dash to iPhone / iPad 📱

**Platform:** macOS (Apple Silicon M1 / M2 / M3)  
**Target:** iPhone or iPad (physical device or iOS Simulator)  
**Tool:** [BeeWare Briefcase](https://briefcase.readthedocs.io/)  
**Time:** ~1–2 hours the first time (mostly Xcode downloading)

> 🍎 This guide takes your Python pygame game and puts it on a real iPhone or iPad.  
> You do **not** need to pay for an Apple Developer account to test on your own device.

---

## 🗺️ What This Document Covers

| I want to… | Where to look |
|---|---|
| [What you need before starting → Requirements](#-requirements) | Xcode, Apple ID, Briefcase |
| [Set up the project → One-time Setup](#-one-time-setup) | pyproject.toml changes, pygame-ce, briefcase |
| [Add touch controls → Touch Support](#-add-touch-controls) | Finger tap to jump |
| [Run in the Simulator → iOS Simulator](#-run-in-ios-simulator) | See the game on a virtual iPhone |
| [Run on your real device → Real Device](#-run-on-a-real-iphone-or-ipad) | USB cable, Xcode, trust |
| [Fix problems → Troubleshooting](#-troubleshooting) | Common errors |

---

## ✅ Requirements

You need **4 things** before starting. Do them in order.

---

### 1 — Xcode (free, ~10 GB)

Xcode is Apple's development tool. You must install it from the Mac App Store.

1. Open **App Store** (`Cmd+Space` → `App Store`)
2. Search for **Xcode**
3. Click **Get** → **Install**
4. Wait (it's large — can take 30–60 minutes on a slow connection)
5. Open Xcode once after installing — it will install extra components

Then open Terminal and run:

```bash
xcode-select --install
sudo xcodebuild -license accept
```

Check it works:

```bash
xcodebuild -version
# → Xcode 15.x (or newer)
```

---

### 2 — Apple ID (free)

You already have one if you use an iPhone. You just need to sign into Xcode with it.

1. Open **Xcode**
2. Menu → **Xcode** → **Settings** → **Accounts** tab
3. Click **+** → **Apple ID**
4. Sign in with your Apple ID and password

> 💡 A free Apple ID lets you install apps on **your own devices** for 7 days.  
> After 7 days you just re-sign (same command, takes 10 seconds).  
> You do **not** need to pay $99/year unless you want to publish to the App Store.

---

### 3 — Briefcase

Briefcase is a Python tool that packages your game for iOS.

```bash
cd geometrydash
source .venv/bin/activate
uv pip install briefcase
```

Check it works:

```bash
briefcase --version
# → Briefcase 0.x.x
```

---

### 4 — pygame-ce (community edition)

Standard `pygame` does not work on iOS. `pygame-ce` is a drop-in replacement that does.

```bash
uv pip uninstall pygame
uv pip install pygame-ce
```

> 💡 Your `game.py` does not need any changes — the `import pygame` line stays exactly the same. `pygame-ce` uses the same name.

---

## 🔧 One-time Setup

Do this once to prepare the project for iOS.

---

### Step 1 — Update pyproject.toml

Open `pyproject.toml` and **replace the whole file** with this:

```toml
[project]
name = "geometrydash"
version = "0.1.0"
description = "A simple Geometry Dash game in Python"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "pygame-ce>=2.5.0",
    "numpy>=1.24.0",
]

[project.scripts]
geometrydash = "geometrydash.game:main"

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

# ── BeeWare Briefcase iOS config ──────────────────────────────────────────────

[tool.briefcase]
project_name = "Geometry Dash"
bundle = "com.filip.geometrydash"
version = "0.1.0"
url = "https://github.com/matusfil-ux/geometrydash"
license = "MIT"
author = "Filip"
author_email = "filip@example.com"

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
requires = [
    "pygame-ce",
]
```

---

### Step 2 — Add touch controls to game.py

iPhones and iPads have no keyboard — tapping the screen must make the player jump.

Open `src/geometrydash/game.py` in VS Code:

```bash
code src/geometrydash/game.py
```

Find the events loop — look for this line:

```python
jump = (
    (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
    or event.type == pygame.MOUSEBUTTONDOWN
)
```

**Replace it** with:

```python
jump = (
    (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
    or event.type == pygame.MOUSEBUTTONDOWN
    or event.type == pygame.FINGERDOWN        # ← finger tap on touchscreen
)
```

Also find the menu start screen drawing block and add a tap instruction:

```python
if not started and not game_over:
    draw_text(screen, "TAP TO JUMP", 30, WINDOW_WIDTH // 2, 290, (180, 180, 180), center=True)
```

Save the file (`Cmd+S`).

---

### Step 3 — Reinstall the package

```bash
uv pip install -e .
```

---

## 🖥️ Run in iOS Simulator

The iOS Simulator is a virtual iPhone/iPad that runs on your Mac. No cable needed.

```bash
source .venv/bin/activate

# Create the iOS project (first time only — takes a few minutes)
briefcase create iOS

# Build the app
briefcase build iOS

# Launch in the Simulator
briefcase run iOS
```

The iOS Simulator will open and your game will appear on a virtual iPhone screen.

> 💡 The Simulator uses your **mouse click** as a tap — so clicking = jumping.  
> You can choose different iPhone/iPad models from the Simulator's **File → Open Simulator** menu.

**To update and rerun after changing `game.py`:**

```bash
briefcase update iOS
briefcase run iOS
```

---

## 📱 Run on a Real iPhone or iPad

This puts the game on your actual device. You need a USB-C or Lightning cable.

---

### Step 1 — Connect your device

Plug your iPhone or iPad into your Mac with a cable.

On your iPhone/iPad: tap **Trust** when it asks "Trust This Computer?"

---

### Step 2 — Find your Apple Team ID

Open Terminal:

```bash
briefcase run iOS --device ?
```

This lists your connected devices and your Apple Team ID. It looks like: `A1B2C3D4E5`

---

### Step 3 — Build and sign for your device

```bash
briefcase build iOS --device "Your iPhone Name"
```

Briefcase will ask you to sign in — use your Apple ID.

---

### Step 4 — Install on your device via Xcode

```bash
briefcase run iOS --device "Your iPhone Name"
```

This opens Xcode. In Xcode:

1. Select your iPhone from the device list (top bar)
2. Click the **▶ Run** button (or press `Cmd+R`)
3. If you see a signing error, go to: **Project Navigator** → click the app name → **Signing & Capabilities** → choose your Apple ID team

Your iPhone will show: *"Verifying…"* then the app installs and opens!

---

### Step 5 — Trust the developer on your iPhone

The first time you install an app from a free Apple ID, your iPhone will block it.

On your iPhone:
1. **Settings** → **General** → **VPN & Device Management**
2. Tap your Apple ID under **Developer App**
3. Tap **Trust "your@appleid.com"**
4. Tap **Trust** again to confirm

Now open the app from your home screen — it works! 🎉

---

### After 7 days — re-sign

Free Apple IDs expire after 7 days. To renew:

```bash
briefcase build iOS --device "Your iPhone Name"
briefcase run iOS --device "Your iPhone Name"
```

Takes about 30 seconds.

---

## 🔍 Troubleshooting

---

### ❌ `ModuleNotFoundError: No module named 'briefcase'`

```bash
source .venv/bin/activate
uv pip install briefcase
```

---

### ❌ `xcode-select: error: tool 'xcodebuild' requires Xcode`

Xcode is not properly installed or the command-line tools are missing.

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
```

---

### ❌ `error: No signing certificate "iOS Development" found`

You need to set up signing in Xcode:

1. Open Xcode → **Settings** → **Accounts** → add your Apple ID
2. Click **Manage Certificates** → click **+** → **Apple Development**
3. Re-run `briefcase run iOS --device "Your iPhone Name"`

---

### ❌ `pygame` import error on device (but works on Mac)

Make sure you installed `pygame-ce` (not `pygame`) and updated `pyproject.toml`:

```bash
uv pip uninstall pygame
uv pip install pygame-ce
```

---

### ❌ The game runs but the screen is blank / black on iPhone

The window size is fixed at 800×400 but iPhone screens are portrait. Add this near the top of `run_game()` in `game.py` to make the game fill the screen:

```python
# Detect if running on a mobile screen and rotate/scale
info = pygame.display.Info()
if info.current_w < info.current_h:  # portrait screen (phone)
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
```

---

### ❌ "Untrusted Developer" message on iPhone

Go to: **Settings → General → VPN & Device Management → Trust** your Apple ID.  
See [Step 5 above](#step-5--trust-the-developer-on-your-iphone).

---

### ❌ `briefcase create iOS` fails with network error

Briefcase downloads the iOS support package from the internet. Make sure you have a working internet connection (not a VPN that blocks GitHub).

---

## 🔗 Quick Reference

| Task | Command |
|------|---------|
| Install Briefcase | `uv pip install briefcase` |
| Install pygame-ce | `uv pip uninstall pygame && uv pip install pygame-ce` |
| Create iOS project (first time) | `briefcase create iOS` |
| Build | `briefcase build iOS` |
| Run in Simulator | `briefcase run iOS` |
| List real devices | `briefcase run iOS --device ?` |
| Run on real device | `briefcase run iOS --device "iPhone Name"` |
| Update after code changes | `briefcase update iOS && briefcase run iOS` |

---

## 🗺️ What Happens Behind the Scenes

```
your Python game.py
        │
        ▼
briefcase create iOS
        │  ← downloads Python iOS runtime from BeeWare
        │  ← downloads your dependencies (pygame-ce, numpy)
        │  ← creates an Xcode project in build/geometrydash/iOS/
        ▼
briefcase build iOS
        │  ← compiles Python bytecode
        │  ← signs the app with your Apple ID
        ▼
briefcase run iOS
        │  ← installs .app into Simulator or onto device
        ▼
Game runs on iPhone! 🎮
```

---

> 📌 **Start with the Simulator** — it's much faster to test. Once the game looks good there, plug in your iPhone and deploy to the real device.  
> 🚀 **Once it's on your iPhone, show your friends — that's a real app you built!**

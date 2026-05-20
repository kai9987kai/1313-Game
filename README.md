# 1313: Underworld Run

A compact Pygame action-platformer inspired by the cancelled underworld project. The game now has structured levels, platform flooring, patrol waves, pickups, dash movement, tactical scan/heat vent abilities, interactable relays/turrets/coolant vents, timed hazards, between-level contracts, blaster heat tiers, a lightweight encounter Director, noise-reactive enemy behavior, health/shield systems, and in-game menu/pause/about screens.

## Run

```powershell
python -m pip install -r requirements.txt
python .\1313.py
```

Use `--mute` if you want to start without audio.

## Controls

- `A` / `D` or arrow keys: move
- `W` / up arrow: jump
- `Space`: blaster
- `Shift` or `X`: dash
- `E`: tactical scan
- `Q`: vent blaster heat
- `F`: use nearby device
- `P` or `Esc`: pause/resume
- `F1`: about
- `M`: mute
- `H`: high contrast
- `V`: reduced effects
- `R`: restart

## Test

Run a deterministic headless smoke test:

```powershell
python .\1313.py --smoke-test
```

The smoke test initializes Pygame with dummy video/audio drivers, simulates movement, jumping, shooting, and dashing, then prints a JSON state snapshot with assertions.

Optional frame count:

```powershell
python .\1313.py --smoke-test --frames 600
```

Background music is optional. If `music.ogg`, `music.mp3`, or the legacy MP3 is missing, the game runs without crashing.

Contracts appear between levels. Press `1`, `2`, or `3` to choose the next run modifier.


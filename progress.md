Original prompt: innovate advance improve evole and expermiment and optermise use sub agents and add new features as well use use best and new research

## 2026-05-20

- Started by inspecting the repository. It is a compact Pygame project centered on `1313.py` with image and sound assets.
- Confirmed `GoblinsfromMars TrapRemix.mp3` is referenced but missing, so audio needs graceful fallback.
- Planned upgrade: replace the monolithic loop with a testable game class, add levels/floors, better movement feel, powerups, HUD/menu flow, and a smoke-test mode.
- Implemented the upgrade in `1313.py`: asset-relative loading, optional audio, Pygame-only menus, levels/platforms, pickups, dash, coyote-time jump forgiveness, blaster heat, deterministic smoke testing, and cleaner update/render boundaries.
- Added `requirements.txt`, refreshed `README.md`, and added `.github/workflows/pygame-smoke.yml`.
- Verified with `python -m py_compile 1313.py`, `python -B .\1313.py --smoke-test`, and an import-side-effect check (`Game` importable while `pygame_init` remains false). Also rendered and visually inspected a gameplay frame during development.
- Second pass added heat-tier bullets, tactical scan, manual heat venting, noise pings that pull enemy investigation, adaptive Director reinforcements/drops, high-contrast and reduced-effects toggles, static world caching, particle caps, stronger smoke assertions, and expanded CI.
- Visual QA caught a wrong enemy asset sequence (`R10.png`/`R11.png` fallback instead of `R10E.png`/`R11E.png`), fixed via the `load_sequence(..., suffix="E")` path. Standard and high-contrast/reduced-effects render passes were inspected after the fix.

## TODO / Suggestions

- Add new custom character art when final designs are available; the current build reuses the existing sprites.
- Add a short original music loop named `music.ogg` or `music.mp3` if background music is desired. The old missing MP3 is now optional.
- Consider extracting entities into separate modules once the single-file version grows further.
- If the Director becomes too aggressive after more level content is added, tune `DIRECTOR_MIN_SPAWN_TIME`, `DIRECTOR_MAX_SPAWN_TIME`, and `DIRECTOR_MAX_ENEMIES` first.

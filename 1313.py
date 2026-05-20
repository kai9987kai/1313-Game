from __future__ import annotations

import argparse
import json
import math
import os
import random
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API.*", category=UserWarning)

import pygame


ASSET_DIR = Path(__file__).resolve().parent
WIDTH = 960
HEIGHT = 540
FPS = 60

PLAYER_SIZE = (64, 64)
ENEMY_SIZE = (64, 64)
FLOOR_Y = 482

GRAVITY = 1850
MAX_FALL_SPEED = 880
PLAYER_ACCEL = 2300
PLAYER_FRICTION = 2500
PLAYER_MAX_SPEED = 285
JUMP_VELOCITY = -680
COYOTE_TIME = 0.13
JUMP_BUFFER = 0.13
DASH_SPEED = 610
DASH_TIME = 0.12
DASH_COOLDOWN = 0.85

SHOT_COOLDOWN = 0.16
SHOT_HEAT = 17
HEAT_COOL_RATE = 38
OVERHEAT_TIME = 1.25

SCAN_COST = 38
SCAN_DURATION = 2.35
SCAN_COOLDOWN = 5.0
VENT_COOLDOWN = 0.85
VENT_AMOUNT = 45
DIRECTOR_MAX_ENEMIES = 5
DIRECTOR_MIN_SPAWN_TIME = 4.0
DIRECTOR_MAX_SPAWN_TIME = 9.0
INTERACT_RANGE = 54
TURRET_RANGE = 300
TURRET_COOLDOWN = 1.05


PALETTE = {
    "ink": (16, 19, 25),
    "panel": (25, 31, 39),
    "panel_soft": (39, 48, 59),
    "text": (237, 243, 246),
    "muted": (164, 181, 190),
    "amber": (245, 178, 74),
    "cyan": (69, 218, 229),
    "red": (238, 82, 83),
    "green": (95, 213, 137),
    "blue": (78, 146, 255),
    "floor": (67, 76, 87),
    "floor_edge": (183, 195, 202),
}


LEVELS = [
    {
        "name": "Docking Bay 13",
        "brief": "Clear the hangar and reach the lift.",
        "player": (74, 390),
        "platforms": [
            (0, FLOOR_Y, WIDTH, 58),
            (178, 380, 184, 18),
            (492, 332, 190, 18),
            (710, 424, 142, 18),
        ],
        "enemies": [
            {"x": 610, "y": 268, "left": 492, "right": 682, "kind": "patrol"},
            {"x": 760, "y": 360, "left": 700, "right": 890, "kind": "scout"},
        ],
        "pickups": [
            {"x": 250, "y": 338, "kind": "credit"},
            {"x": 558, "y": 290, "kind": "coolant"},
        ],
        "devices": [
            {"x": 214, "y": 346, "kind": "relay"},
            {"x": 532, "y": 300, "kind": "turret"},
            {"x": 792, "y": 392, "kind": "vent"},
        ],
        "hazards": [
            {"x": 412, "y": 430, "w": 34, "h": 52, "kind": "steam", "period": 2.8, "active": 0.9, "phase": 0.6},
        ],
        "exit": (888, 418, 48, 64),
    },
    {
        "name": "Market Underrail",
        "brief": "Use the upper routes to break the patrol.",
        "player": (70, 390),
        "platforms": [
            (0, FLOOR_Y, WIDTH, 58),
            (116, 410, 146, 18),
            (315, 350, 160, 18),
            (550, 300, 172, 18),
            (745, 390, 145, 18),
        ],
        "enemies": [
            {"x": 206, "y": 346, "left": 115, "right": 260, "kind": "scout"},
            {"x": 570, "y": 236, "left": 550, "right": 722, "kind": "patrol"},
            {"x": 795, "y": 326, "left": 745, "right": 895, "kind": "brute"},
        ],
        "pickups": [
            {"x": 372, "y": 308, "kind": "credit"},
            {"x": 615, "y": 258, "kind": "med"},
            {"x": 808, "y": 348, "kind": "shield"},
        ],
        "devices": [
            {"x": 146, "y": 378, "kind": "vent"},
            {"x": 594, "y": 268, "kind": "turret"},
            {"x": 785, "y": 358, "kind": "relay"},
        ],
        "hazards": [
            {"x": 478, "y": 454, "w": 86, "h": 28, "kind": "spark", "period": 3.1, "active": 1.0, "phase": 1.0},
            {"x": 708, "y": 438, "w": 44, "h": 44, "kind": "steam", "period": 2.4, "active": 0.7, "phase": 0.1},
        ],
        "exit": (900, 418, 44, 64),
    },
    {
        "name": "Foundry Lift",
        "brief": "Survive the last wave and claim the route out.",
        "player": (70, 390),
        "platforms": [
            (0, FLOOR_Y, WIDTH, 58),
            (85, 365, 150, 18),
            (318, 420, 150, 18),
            (548, 360, 150, 18),
            (740, 302, 170, 18),
        ],
        "enemies": [
            {"x": 145, "y": 301, "left": 85, "right": 235, "kind": "scout"},
            {"x": 390, "y": 356, "left": 318, "right": 468, "kind": "patrol"},
            {"x": 608, "y": 296, "left": 548, "right": 698, "kind": "scout"},
            {"x": 790, "y": 238, "left": 740, "right": 910, "kind": "brute"},
        ],
        "pickups": [
            {"x": 150, "y": 323, "kind": "coolant"},
            {"x": 376, "y": 378, "kind": "credit"},
            {"x": 812, "y": 260, "kind": "med"},
        ],
        "devices": [
            {"x": 118, "y": 333, "kind": "relay"},
            {"x": 586, "y": 328, "kind": "vent"},
            {"x": 790, "y": 270, "kind": "turret"},
        ],
        "hazards": [
            {"x": 252, "y": 438, "w": 52, "h": 44, "kind": "spark", "period": 2.2, "active": 0.8, "phase": 0.0},
            {"x": 688, "y": 408, "w": 44, "h": 74, "kind": "steam", "period": 2.7, "active": 1.1, "phase": 1.2},
        ],
        "exit": (904, 418, 42, 64),
    },
]


CONTRACTS = [
    {
        "id": "coolant",
        "name": "Coolant Syndicate",
        "body": "Cooling improves, but the Director gets bolder.",
        "mods": {"cooling": 1.35, "director": 0.08},
    },
    {
        "id": "dash",
        "name": "Dash License",
        "body": "Dash returns faster, but max health drops by one.",
        "mods": {"dash": 0.72, "max_health": -1},
    },
    {
        "id": "combo",
        "name": "Bounty Clause",
        "body": "Combos pay more, but heat builds faster.",
        "mods": {"score": 1.35, "heat_gain": 1.18},
    },
    {
        "id": "focus",
        "name": "Scanner Ghost",
        "body": "Focus recovers faster, but reinforcements arrive sooner.",
        "mods": {"focus": 1.45, "director": 0.06},
    },
]


@dataclass
class InputState:
    left: bool = False
    right: bool = False
    jump_down: bool = False
    jump_held: bool = False
    shoot: bool = False
    dash: bool = False
    pulse: bool = False
    vent: bool = False
    interact: bool = False


@dataclass
class Platform:
    rect: pygame.Rect


@dataclass
class Hazard:
    rect: pygame.Rect
    kind: str
    period: float
    active_time: float
    phase: float
    cooldown: float = 0.0

    def active(self, elapsed: float) -> bool:
        return ((elapsed + self.phase) % self.period) < self.active_time


@dataclass
class Device:
    rect: pygame.Rect
    kind: str
    hacked: bool = False
    cooldown: float = 0.0
    pulse: float = 0.0


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    damage: int = 1
    pierces: int = 0
    color: tuple[int, int, int] = PALETTE["amber"]
    tier: str = "standard"
    life: float = 1.1
    radius: int = 5

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.life -= dt
        return self.life > 0 and -20 <= self.x <= WIDTH + 20


@dataclass
class NoisePing:
    x: float
    y: float
    radius: float
    max_radius: float
    life: float
    color: tuple[int, int, int]

    def update(self, dt: float) -> bool:
        self.radius = min(self.max_radius, self.radius + self.max_radius * 1.65 * dt)
        self.life -= dt
        return self.life > 0


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple[int, int, int]
    radius: float

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 260 * dt
        self.life -= dt
        self.radius = max(0.5, self.radius - 7 * dt)
        return self.life > 0


@dataclass
class Director:
    pressure: float = 0.42
    spawn_timer: float = 6.0
    event: str = ""
    event_timer: float = 0.0

    def set_event(self, text: str, seconds: float = 1.4) -> None:
        self.event = text
        self.event_timer = seconds


@dataclass
class Pickup:
    rect: pygame.Rect
    kind: str
    bob: float = 0

    def update(self, dt: float) -> None:
        self.bob += dt * 4.5

    def draw(self, surface: pygame.Surface) -> None:
        cx = self.rect.centerx
        cy = self.rect.centery + int(math.sin(self.bob) * 4)
        color = {
            "credit": PALETTE["amber"],
            "coolant": PALETTE["cyan"],
            "med": PALETTE["green"],
            "shield": PALETTE["blue"],
        }.get(self.kind, PALETTE["text"])
        pygame.draw.circle(surface, (6, 8, 12), (cx, cy), 13)
        pygame.draw.circle(surface, color, (cx, cy), 10)
        if self.kind == "credit":
            pygame.draw.circle(surface, PALETTE["ink"], (cx, cy), 4, 2)
        elif self.kind == "coolant":
            pygame.draw.line(surface, PALETTE["ink"], (cx - 5, cy), (cx + 5, cy), 3)
        elif self.kind == "med":
            pygame.draw.line(surface, PALETTE["ink"], (cx - 5, cy), (cx + 5, cy), 3)
            pygame.draw.line(surface, PALETTE["ink"], (cx, cy - 5), (cx, cy + 5), 3)
        elif self.kind == "shield":
            pygame.draw.rect(surface, PALETTE["ink"], (cx - 4, cy - 5, 8, 10), 2)


class NullSound:
    def play(self) -> None:
        return None


@dataclass
class Assets:
    player_right: list[pygame.Surface]
    player_left: list[pygame.Surface]
    enemy_right: list[pygame.Surface]
    enemy_left: list[pygame.Surface]
    bg: pygame.Surface
    icon: pygame.Surface | None
    blaster: pygame.mixer.Sound | NullSound
    hit: pygame.mixer.Sound | NullSound


def load_image(name: str, size: tuple[int, int] | None = None, alpha: bool = True) -> pygame.Surface:
    path = ASSET_DIR / name
    if path.exists():
        image = pygame.image.load(path)
        image = image.convert_alpha() if alpha else image.convert()
    else:
        fallback = size or (64, 64)
        image = pygame.Surface(fallback, pygame.SRCALPHA if alpha else 0)
        image.fill((255, 0, 180, 255) if alpha else (255, 0, 180))
        pygame.draw.line(image, (20, 20, 20), (0, 0), (fallback[0], fallback[1]), 3)
        pygame.draw.line(image, (20, 20, 20), (fallback[0], 0), (0, fallback[1]), 3)
    if size and image.get_size() != size:
        image = pygame.transform.smoothscale(image, size)
    return image


def load_sequence(prefix: str, count: int, size: tuple[int, int], suffix: str = "") -> list[pygame.Surface]:
    return [load_image(f"{prefix}{i}{suffix}.png", size=size) for i in range(1, count + 1)]


def load_sound(name: str) -> pygame.mixer.Sound | NullSound:
    if pygame.mixer.get_init() is None:
        return NullSound()
    path = ASSET_DIR / name
    if not path.exists():
        return NullSound()
    try:
        return pygame.mixer.Sound(str(path))
    except pygame.error:
        return NullSound()


def load_assets() -> Assets:
    bg = load_image("bg.jpeg", size=(WIDTH, HEIGHT), alpha=False)
    icon_path = ASSET_DIR / "1313.jpg"
    icon = load_image("1313.jpg", size=(64, 64), alpha=False) if icon_path.exists() else None
    blaster = load_sound("Blastersound.wav")
    return Assets(
        player_right=load_sequence("R", 9, PLAYER_SIZE),
        player_left=load_sequence("L", 9, PLAYER_SIZE),
        enemy_right=load_sequence("R", 11, ENEMY_SIZE, "E"),
        enemy_left=load_sequence("L", 11, ENEMY_SIZE, "E"),
        bg=bg,
        icon=icon,
        blaster=blaster,
        hit=blaster,
    )


def try_start_music(muted: bool) -> bool:
    if muted or pygame.mixer.get_init() is None:
        return False
    for name in ("GoblinsfromMars TrapRemix.mp3", "music.ogg", "music.mp3"):
        path = ASSET_DIR / name
        if not path.exists():
            continue
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
            return True
        except pygame.error:
            return False
    return False


class Player:
    def __init__(self, x: int, y: int) -> None:
        self.x = float(x)
        self.y = float(y)
        self.w, self.h = PLAYER_SIZE
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1
        self.on_ground = False
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.invuln = 0.0
        self.health = 4
        self.max_health = 4
        self.shield = 0
        self.focus = 55.0
        self.max_focus = 100.0
        self.scan_timer = 0.0
        self.scan_cooldown = 0.0
        self.vent_cooldown = 0.0
        self.heat = 0.0
        self.overheated = 0.0
        self.shot_cooldown = 0.0
        self.walk_time = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x + 16), int(self.y + 8), 32, 56)

    @property
    def sprite_pos(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    def full_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


class Enemy:
    STATS = {
        "scout": {"health": 2, "speed": 118, "score": 90, "color": PALETTE["cyan"]},
        "patrol": {"health": 3, "speed": 86, "score": 120, "color": PALETTE["amber"]},
        "brute": {"health": 5, "speed": 58, "score": 180, "color": PALETTE["red"]},
    }

    def __init__(self, x: int, y: int, left: int, right: int, kind: str) -> None:
        stats = self.STATS[kind]
        self.x = float(x)
        self.y = float(y)
        self.left = float(left)
        self.right = float(right)
        self.kind = kind
        self.max_health = int(stats["health"])
        self.health = self.max_health
        self.speed = float(stats["speed"])
        self.score = int(stats["score"])
        self.color = stats["color"]
        self.direction = -1 if x > (left + right) / 2 else 1
        self.walk_time = 0.0
        self.hit_flash = 0.0
        self.state = "patrol"
        self.target_x = float(x)
        self.alert_timer = 0.0
        self.stun_timer = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x + 16), int(self.y + 6), 32, 58)

    def full_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), ENEMY_SIZE[0], ENEMY_SIZE[1])

    def update(self, dt: float, player: Player) -> None:
        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            self.hit_flash = max(0.0, self.hit_flash - dt)
            return

        if abs(player.rect.centerx - self.rect.centerx) < 180 and abs(player.rect.centery - self.rect.centery) < 95:
            self.state = "chase"
            self.alert_timer = max(self.alert_timer, 0.8)
            self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
        elif self.alert_timer > 0:
            self.state = "investigate"
            self.alert_timer = max(0.0, self.alert_timer - dt)
            self.direction = 1 if self.target_x > self.rect.centerx else -1
        else:
            self.state = "patrol"

        speed_scale = 1.26 if self.state in {"chase", "investigate"} else 1.0
        self.x += self.direction * self.speed * speed_scale * dt
        if self.x < self.left:
            self.x = self.left
            self.direction = 1
        elif self.x > self.right:
            self.x = self.right
            self.direction = -1
        self.walk_time += dt * 12
        self.hit_flash = max(0.0, self.hit_flash - dt)

    def investigate(self, x: float) -> None:
        self.target_x = max(self.left, min(self.right, x))
        self.alert_timer = max(self.alert_timer, 1.7)
        self.state = "investigate"

    def hit(self, amount: int) -> bool:
        self.health -= amount
        self.hit_flash = 0.08
        return self.health <= 0


class Game:
    def __init__(self, muted: bool = False) -> None:
        pygame.init()
        if not muted and pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init()
            except pygame.error:
                pass

        pygame.display.set_caption("1313: Underworld Run")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.assets = load_assets()
        if self.assets.icon is not None:
            pygame.display.set_icon(self.assets.icon)

        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.big_font = pygame.font.SysFont("arial", 54, bold=True)

        self.rng = random.Random(1313)
        self.muted = muted
        self.music_started = try_start_music(muted)
        self.high_contrast = False
        self.reduced_motion = False
        self.prev_jump_held = False
        self.prev_dash_held = False
        self.prev_pulse_held = False
        self.prev_vent_held = False
        self.prev_interact_held = False
        self.static_world = pygame.Surface((WIDTH, HEIGHT))
        self.director = Director()
        self.mods = {
            "cooling": 1.0,
            "dash": 1.0,
            "score": 1.0,
            "heat_gain": 1.0,
            "focus": 1.0,
            "director": 0.0,
        }
        self.active_contracts: list[str] = []
        self.pending_contracts: list[dict[str, object]] = []
        self.next_level_index = 0
        self.fullscreen = False
        self.mode = "menu"
        self.running = True
        self.level_index = 0
        self.score = 0
        self.combo = 1
        self.combo_timer = 0.0
        self.message = "ENTER to deploy"
        self.message_timer = 0.0
        self.time_alive = 0.0
        self.reset_level(0, keep_score=False)
        pygame.event.set_blocked((pygame.MOUSEMOTION,))

    def reset_level(self, index: int, keep_score: bool = True) -> None:
        level = LEVELS[index]
        self.level_index = index
        px, py = level["player"]
        self.player = Player(px, py)
        self.platforms = [Platform(pygame.Rect(*rect)) for rect in level["platforms"]]
        self.enemies = [
            Enemy(data["x"], data["y"], data["left"], data["right"], data["kind"]) for data in level["enemies"]
        ]
        self.pickups = [Pickup(pygame.Rect(data["x"], data["y"], 24, 24), data["kind"]) for data in level["pickups"]]
        self.devices = [Device(pygame.Rect(data["x"], data["y"], 34, 34), data["kind"]) for data in level.get("devices", [])]
        self.hazards = [
            Hazard(
                pygame.Rect(data["x"], data["y"], data["w"], data["h"]),
                data["kind"],
                float(data["period"]),
                float(data["active"]),
                float(data["phase"]),
            )
            for data in level.get("hazards", [])
        ]
        self.exit_rect = pygame.Rect(*level["exit"])
        self.bullets: list[Bullet] = []
        self.particles: list[Particle] = []
        self.noise_pings: list[NoisePing] = []
        self.director = Director(spawn_timer=self.rng.uniform(DIRECTOR_MIN_SPAWN_TIME, DIRECTOR_MAX_SPAWN_TIME))
        self.static_world = self.build_static_world()
        self.time_alive = 0.0
        self.message = level["brief"]
        self.message_timer = 2.5
        if not keep_score:
            self.score = 0
            self.combo = 1
            self.combo_timer = 0.0
        self.apply_player_mods()

    def restart(self) -> None:
        self.mods = {
            "cooling": 1.0,
            "dash": 1.0,
            "score": 1.0,
            "heat_gain": 1.0,
            "focus": 1.0,
            "director": 0.0,
        }
        self.active_contracts = []
        self.pending_contracts = []
        self.next_level_index = 0
        self.mode = "playing"
        self.reset_level(0, keep_score=False)

    def apply_player_mods(self) -> None:
        max_health = max(2, 4 + int(self.mods.get("max_health", 0)))
        self.player.max_health = max_health
        self.player.health = min(self.player.health, max_health)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.mode == "contract":
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        self.accept_contract(0)
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.accept_contract(1)
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.accept_contract(2)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.accept_contract(0)
                    elif event.key == pygame.K_r:
                        self.restart()
                    continue
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.mode in {"menu", "game_over", "victory"}:
                        self.restart()
                    elif self.mode == "about":
                        self.mode = "menu"
                elif event.key == pygame.K_ESCAPE:
                    if self.mode == "playing":
                        self.mode = "paused"
                    elif self.mode in {"paused", "about"}:
                        self.mode = "playing"
                    else:
                        self.running = False
                elif event.key == pygame.K_p and self.mode in {"playing", "paused"}:
                    self.mode = "paused" if self.mode == "playing" else "playing"
                elif event.key == pygame.K_F1:
                    self.mode = "about" if self.mode != "about" else "menu"
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_m:
                    self.toggle_mute()
                elif event.key == pygame.K_h:
                    self.high_contrast = not self.high_contrast
                    self.static_world = self.build_static_world()
                    self.message = "High contrast on" if self.high_contrast else "High contrast off"
                    self.message_timer = 1.0
                elif event.key == pygame.K_v:
                    self.reduced_motion = not self.reduced_motion
                    self.message = "Reduced effects on" if self.reduced_motion else "Reduced effects off"
                    self.message_timer = 1.0

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.muted:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.music.stop()
            self.music_started = False
        elif not self.music_started:
            self.music_started = try_start_music(False)

    def read_input(self) -> InputState:
        keys = pygame.key.get_pressed()
        jump_held = keys[pygame.K_UP] or keys[pygame.K_w]
        dash_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_x]
        pulse_held = keys[pygame.K_e]
        vent_held = keys[pygame.K_q]
        interact_held = keys[pygame.K_f]
        inputs = InputState(
            left=keys[pygame.K_LEFT] or keys[pygame.K_a],
            right=keys[pygame.K_RIGHT] or keys[pygame.K_d],
            jump_down=jump_held and not self.prev_jump_held,
            jump_held=jump_held,
            shoot=keys[pygame.K_SPACE],
            dash=dash_held and not self.prev_dash_held,
            pulse=pulse_held and not self.prev_pulse_held,
            vent=vent_held and not self.prev_vent_held,
            interact=interact_held and not self.prev_interact_held,
        )
        self.prev_jump_held = jump_held
        self.prev_dash_held = dash_held
        self.prev_pulse_held = pulse_held
        self.prev_vent_held = vent_held
        self.prev_interact_held = interact_held
        return inputs

    def step(self, dt: float, inputs: InputState | None = None) -> None:
        dt = min(dt, 1 / 20)
        if self.mode != "playing":
            return
        inputs = inputs or self.read_input()
        self.time_alive += dt
        self.message_timer = max(0.0, self.message_timer - dt)
        self.combo_timer = max(0.0, self.combo_timer - dt)
        if self.combo_timer <= 0:
            self.combo = 1

        focus_gain = (8 + self.director.pressure * 5) * float(self.mods.get("focus", 1.0))
        self.player.focus = min(self.player.max_focus, self.player.focus + focus_gain * dt)
        self.update_player(dt, inputs)
        self.update_devices(dt, inputs)
        self.update_hazards(dt)
        self.update_bullets(dt)
        self.update_enemies(dt)
        self.update_pickups(dt)
        self.update_director(dt)
        self.update_noise_pings(dt)
        self.update_particles(dt)
        self.check_exit()

    def update_player(self, dt: float, inputs: InputState) -> None:
        p = self.player
        p.invuln = max(0.0, p.invuln - dt)
        p.shot_cooldown = max(0.0, p.shot_cooldown - dt)
        p.dash_cooldown = max(0.0, p.dash_cooldown - dt)
        p.scan_timer = max(0.0, p.scan_timer - dt)
        p.scan_cooldown = max(0.0, p.scan_cooldown - dt)
        p.vent_cooldown = max(0.0, p.vent_cooldown - dt)
        p.overheated = max(0.0, p.overheated - dt)
        p.heat = max(0.0, p.heat - HEAT_COOL_RATE * float(self.mods.get("cooling", 1.0)) * dt)
        p.jump_buffer = JUMP_BUFFER if inputs.jump_down else max(0.0, p.jump_buffer - dt)

        move_axis = int(inputs.right) - int(inputs.left)
        if move_axis:
            p.vx += move_axis * PLAYER_ACCEL * dt
            p.facing = move_axis
        else:
            friction = PLAYER_FRICTION * dt
            if abs(p.vx) <= friction:
                p.vx = 0.0
            else:
                p.vx -= math.copysign(friction, p.vx)
        p.vx = max(-PLAYER_MAX_SPEED, min(PLAYER_MAX_SPEED, p.vx))

        if inputs.dash and p.dash_cooldown <= 0 and p.dash_timer <= 0:
            p.dash_timer = DASH_TIME
            p.dash_cooldown = DASH_COOLDOWN * float(self.mods.get("dash", 1.0))
            p.vx = DASH_SPEED * p.facing
            self.spawn_particles(p.rect.centerx, p.rect.centery, PALETTE["cyan"], 8)
            self.emit_noise(p.rect.centerx, p.rect.centery, 150, PALETTE["cyan"])

        if p.dash_timer > 0:
            p.dash_timer = max(0.0, p.dash_timer - dt)
            p.vx = DASH_SPEED * p.facing

        if p.on_ground:
            p.coyote = COYOTE_TIME
        else:
            p.coyote = max(0.0, p.coyote - dt)

        if p.jump_buffer > 0 and p.coyote > 0:
            p.vy = JUMP_VELOCITY
            p.on_ground = False
            p.coyote = 0.0
            p.jump_buffer = 0.0
            self.spawn_particles(p.rect.centerx, p.rect.bottom, PALETTE["floor_edge"], 5)
        elif not inputs.jump_held and p.vy < -150:
            p.vy = -150

        p.vy = min(MAX_FALL_SPEED, p.vy + GRAVITY * dt)

        self.move_player_axis(p.vx * dt, 0)
        self.move_player_axis(0, p.vy * dt)

        if p.y > HEIGHT + 80:
            self.damage_player(2, knockback=-p.facing * 180)
            spawn_x, spawn_y = LEVELS[self.level_index]["player"]
            p.x = float(spawn_x)
            p.y = float(spawn_y)
            p.vx = 0.0
            p.vy = 0.0

        if inputs.shoot:
            self.try_fire()
        if inputs.pulse:
            self.try_pulse()
        if inputs.vent:
            self.try_vent()

        if abs(p.vx) > 12 and p.on_ground:
            p.walk_time += dt * 14
        else:
            p.walk_time = 0.0

    def move_player_axis(self, dx: float, dy: float) -> None:
        p = self.player
        p.x += dx
        p.y += dy
        rect = p.rect

        if rect.left < 0:
            p.x += -rect.left
            p.vx = 0.0
        elif rect.right > WIDTH:
            p.x -= rect.right - WIDTH
            p.vx = 0.0
        rect = p.rect

        if dy:
            p.on_ground = False
        for platform in self.platforms:
            if not rect.colliderect(platform.rect):
                continue
            if dx > 0:
                p.x -= rect.right - platform.rect.left
                p.vx = 0.0
            elif dx < 0:
                p.x += platform.rect.right - rect.left
                p.vx = 0.0
            elif dy > 0:
                p.y -= rect.bottom - platform.rect.top
                p.vy = 0.0
                p.on_ground = True
            elif dy < 0:
                p.y += platform.rect.bottom - rect.top
                p.vy = 0.0
            rect = p.rect

    def try_fire(self) -> None:
        p = self.player
        if p.shot_cooldown > 0 or p.overheated > 0:
            return
        if len(self.bullets) >= 7:
            return
        self.assets.blaster.play()
        heat_before = p.heat
        if heat_before >= 72:
            tier = "volatile"
            damage = 2
            pierces = 0
            radius = 7
            speed = 640
            color = PALETTE["red"]
        elif heat_before >= 38:
            tier = "piercing"
            damage = 1
            pierces = 1
            radius = 5
            speed = 720
            color = PALETTE["cyan"]
        else:
            tier = "standard"
            damage = 1
            pierces = 0
            radius = 5
            speed = 690
            color = PALETTE["amber"]
        self.bullets.append(
            Bullet(
                p.rect.centerx + p.facing * 20,
                p.rect.centery - 6,
                speed * p.facing,
                damage=damage,
                pierces=pierces,
                color=color,
                tier=tier,
                radius=radius,
            )
        )
        p.shot_cooldown = SHOT_COOLDOWN
        p.heat += SHOT_HEAT * float(self.mods.get("heat_gain", 1.0))
        self.emit_noise(p.rect.centerx, p.rect.centery, 220 if tier == "volatile" else 175, color)
        if tier == "volatile":
            p.vx -= p.facing * 42
            self.spawn_particles(p.rect.centerx + p.facing * 24, p.rect.centery, PALETTE["red"], 5)
        if p.heat >= 100:
            p.overheated = OVERHEAT_TIME
            p.heat = 100
            self.message = "Blaster overheated"
            self.message_timer = 1.2

    def try_pulse(self) -> None:
        p = self.player
        if p.scan_cooldown > 0 or p.focus < SCAN_COST:
            return
        p.focus -= SCAN_COST
        p.scan_timer = SCAN_DURATION
        p.scan_cooldown = SCAN_COOLDOWN
        self.emit_noise(p.rect.centerx, p.rect.centery, 110, PALETTE["blue"])
        self.message = "Tactical scan"
        self.message_timer = 1.1
        for enemy in self.enemies:
            if abs(enemy.rect.centerx - p.rect.centerx) < 240:
                enemy.stun_timer = max(enemy.stun_timer, 0.38)
                enemy.hit_flash = 0.18

    def try_vent(self) -> None:
        p = self.player
        if p.vent_cooldown > 0 or p.heat < 15:
            return
        vented = min(VENT_AMOUNT, p.heat)
        p.heat -= vented
        p.overheated = 0.0
        p.vent_cooldown = VENT_COOLDOWN
        self.emit_noise(p.rect.centerx, p.rect.centery, 135 + vented, PALETTE["cyan"])
        self.spawn_particles(p.rect.centerx, p.rect.centery, PALETTE["cyan"], int(6 + vented / 9))
        self.message = "Heat vented"
        self.message_timer = 0.9

    def update_bullets(self, dt: float) -> None:
        live_bullets: list[Bullet] = []
        for bullet in self.bullets:
            if not bullet.update(dt):
                continue
            hit_enemy = None
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    hit_enemy = enemy
                    break
            if hit_enemy is None:
                live_bullets.append(bullet)
            else:
                self.assets.hit.play()
                self.spawn_particles(bullet.x, bullet.y, hit_enemy.color, 7)
                self.player.focus = min(self.player.max_focus, self.player.focus + 8 + bullet.damage * 4)
                if hit_enemy.hit(bullet.damage):
                    self.enemy_defeated(hit_enemy)
                if bullet.pierces > 0:
                    bullet.pierces -= 1
                    bullet.x += math.copysign(hit_enemy.rect.width + bullet.radius, bullet.vx)
                    live_bullets.append(bullet)
        self.bullets = live_bullets

    def enemy_defeated(self, enemy: Enemy) -> None:
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        self.combo = min(5, self.combo + 1)
        self.combo_timer = 2.2
        self.player.focus = min(self.player.max_focus, self.player.focus + 18)
        self.score += int(enemy.score * self.combo * float(self.mods.get("score", 1.0)))
        self.spawn_particles(enemy.rect.centerx, enemy.rect.centery, enemy.color, 18)
        self.emit_noise(enemy.rect.centerx, enemy.rect.centery, 210, enemy.color)
        if self.rng.random() < 0.28:
            kind = "coolant" if self.player.heat > 38 else "credit"
            self.pickups.append(Pickup(pygame.Rect(enemy.rect.centerx - 12, enemy.rect.centery - 12, 24, 24), kind))
        if not self.enemies:
            self.message = "Route open"
            self.message_timer = 1.8

    def update_enemies(self, dt: float) -> None:
        for enemy in list(self.enemies):
            for ping in self.noise_pings:
                distance = abs(enemy.rect.centerx - ping.x) + abs(enemy.rect.centery - ping.y) * 0.5
                if distance < ping.radius + 55:
                    enemy.investigate(ping.x)
            enemy.update(dt, self.player)
            if enemy.rect.colliderect(self.player.rect):
                knockback = -260 if self.player.rect.centerx < enemy.rect.centerx else 260
                self.damage_player(1, knockback)

    def damage_player(self, amount: int, knockback: float) -> None:
        p = self.player
        if p.invuln > 0:
            return
        if p.shield > 0:
            p.shield -= 1
        else:
            p.health -= amount
        p.invuln = 0.95
        p.vx = knockback
        p.vy = -240
        self.combo = 1
        self.combo_timer = 0.0
        self.spawn_particles(p.rect.centerx, p.rect.centery, PALETTE["red"], 12)
        self.message = "Hit"
        self.message_timer = 0.8
        if p.health <= 0:
            self.mode = "game_over"
            self.message = "Run failed"

    def update_pickups(self, dt: float) -> None:
        for pickup in list(self.pickups):
            pickup.update(dt)
            if not pickup.rect.colliderect(self.player.rect):
                continue
            if pickup.kind == "credit":
                self.score += 75
                self.message = "+75 credits"
            elif pickup.kind == "coolant":
                self.player.heat = max(0.0, self.player.heat - 55)
                self.player.overheated = 0.0
                self.message = "Coolant vented"
            elif pickup.kind == "med":
                self.player.health = min(self.player.max_health, self.player.health + 1)
                self.message = "Health restored"
            elif pickup.kind == "shield":
                self.player.shield = min(2, self.player.shield + 1)
                self.message = "Shield charged"
            self.message_timer = 1.0
            self.spawn_particles(pickup.rect.centerx, pickup.rect.centery, PALETTE["text"], 8)
            self.pickups.remove(pickup)

    def update_devices(self, dt: float, inputs: InputState) -> None:
        for device in self.devices:
            device.cooldown = max(0.0, device.cooldown - dt)
            device.pulse = max(0.0, device.pulse - dt)
            if device.kind == "turret" and device.hacked and device.cooldown <= 0:
                target = self.nearest_enemy(device.rect.center, TURRET_RANGE)
                if target is not None:
                    device.cooldown = TURRET_COOLDOWN
                    device.pulse = 0.28
                    target.stun_timer = max(target.stun_timer, 0.18)
                    self.spawn_particles(target.rect.centerx, target.rect.centery, PALETTE["blue"], 6)
                    if target.hit(1):
                        self.enemy_defeated(target)

        if inputs.interact:
            device = self.nearest_device()
            if device is not None:
                self.activate_device(device)

    def nearest_device(self) -> Device | None:
        player_center = self.player.rect.center
        best_device = None
        best_distance = INTERACT_RANGE
        for device in self.devices:
            distance = math.dist(player_center, device.rect.center)
            if distance <= best_distance:
                best_distance = distance
                best_device = device
        return best_device

    def nearest_enemy(self, point: tuple[int, int], max_distance: float) -> Enemy | None:
        best_enemy = None
        best_distance = max_distance
        for enemy in self.enemies:
            distance = math.dist(point, enemy.rect.center)
            if distance <= best_distance:
                best_distance = distance
                best_enemy = enemy
        return best_enemy

    def activate_device(self, device: Device) -> None:
        if device.kind == "relay":
            if device.hacked or self.player.focus < 18:
                self.message = "Relay locked" if not device.hacked else "Relay already routed"
                self.message_timer = 0.8
                return
            self.player.focus -= 18
            device.hacked = True
            device.pulse = 0.55
            self.director.pressure = max(0.12, self.director.pressure - 0.18)
            self.director.spawn_timer += 4.5
            self.score += 100
            for enemy in self.enemies:
                if abs(enemy.rect.centerx - device.rect.centerx) < 260:
                    enemy.stun_timer = max(enemy.stun_timer, 0.45)
                    enemy.hit_flash = 0.2
            self.message = "Relay hacked"
        elif device.kind == "vent":
            if device.cooldown > 0:
                self.message = "Vent cycling"
                self.message_timer = 0.7
                return
            device.cooldown = 5.0
            device.pulse = 0.7
            self.player.heat = max(0.0, self.player.heat - 75)
            self.player.overheated = 0.0
            for enemy in list(self.enemies):
                if math.dist(device.rect.center, enemy.rect.center) < 145:
                    enemy.stun_timer = max(enemy.stun_timer, 0.65)
                    if enemy.hit(1):
                        self.enemy_defeated(enemy)
            self.spawn_particles(device.rect.centerx, device.rect.centery, PALETTE["cyan"], 16)
            self.message = "Coolant burst"
        elif device.kind == "turret":
            if device.hacked:
                self.message = "Turret already friendly"
                self.message_timer = 0.7
                return
            if self.player.focus < 26:
                self.message = "Need focus for turret"
                self.message_timer = 0.8
                return
            self.player.focus -= 26
            device.hacked = True
            device.cooldown = 0.25
            device.pulse = 0.5
            self.score += 75
            self.message = "Turret converted"
        self.message_timer = 1.0

    def update_hazards(self, dt: float) -> None:
        for hazard in self.hazards:
            hazard.cooldown = max(0.0, hazard.cooldown - dt)
            if not hazard.active(self.time_alive) or hazard.cooldown > 0:
                continue
            triggered = False
            if hazard.rect.colliderect(self.player.rect):
                knockback = -220 if self.player.rect.centerx < hazard.rect.centerx else 220
                self.damage_player(1, knockback)
                triggered = True
            for enemy in list(self.enemies):
                if not hazard.rect.colliderect(enemy.rect):
                    continue
                enemy.stun_timer = max(enemy.stun_timer, 0.32)
                enemy.hit_flash = 0.18
                if enemy.hit(1):
                    self.enemy_defeated(enemy)
                triggered = True
            if triggered:
                hazard.cooldown = 0.42

    def update_director(self, dt: float) -> None:
        p = self.player
        health_pressure = 1 - (p.health / max(1, p.max_health))
        heat_pressure = p.heat / 100
        performance_pressure = min(1.0, self.combo / 5 + self.score / 6500)
        target = (
            0.18
            + performance_pressure * 0.46
            + heat_pressure * 0.18
            - health_pressure * 0.28
            + float(self.mods.get("director", 0.0))
        )
        self.director.pressure += (max(0.12, min(0.92, target)) - self.director.pressure) * min(1.0, dt * 0.55)
        self.director.event_timer = max(0.0, self.director.event_timer - dt)

        if not self.enemies or self.mode != "playing":
            return
        self.director.spawn_timer -= dt * (0.7 + self.director.pressure)
        if self.director.spawn_timer > 0:
            return

        self.director.spawn_timer = self.rng.uniform(
            DIRECTOR_MIN_SPAWN_TIME,
            DIRECTOR_MAX_SPAWN_TIME - self.director.pressure * 2.2,
        )
        if len(self.enemies) >= DIRECTOR_MAX_ENEMIES or p.health <= 1:
            if p.health <= 2 and self.rng.random() < 0.45:
                self.spawn_director_pickup("med")
            return
        if p.heat > 76 and self.rng.random() < 0.35:
            self.spawn_director_pickup("coolant")
            return
        self.spawn_director_enemy()

    def spawn_director_enemy(self) -> None:
        platform = self.rng.choice(self.platforms)
        left = platform.rect.left + 8
        right = platform.rect.right - ENEMY_SIZE[0] - 8
        if right <= left:
            return
        player_center = self.player.rect.centerx
        x = left if abs(left - player_center) > abs(right - player_center) else right
        y = platform.rect.top - ENEMY_SIZE[1]
        roll = self.rng.random()
        kind = "brute" if self.director.pressure > 0.72 and roll < 0.22 else "scout" if roll < 0.58 else "patrol"
        self.enemies.append(Enemy(int(x), int(y), int(left), int(right), kind))
        self.director.set_event("Director: reinforcements")
        self.message = "Reinforcements inbound"
        self.message_timer = 1.1

    def spawn_director_pickup(self, kind: str) -> None:
        platform = self.rng.choice(self.platforms)
        x = self.rng.randint(platform.rect.left + 18, max(platform.rect.left + 18, platform.rect.right - 42))
        y = platform.rect.top - 30
        self.pickups.append(Pickup(pygame.Rect(x, y, 24, 24), kind))
        self.director.set_event(f"Director: {kind} drop")

    def update_noise_pings(self, dt: float) -> None:
        self.noise_pings = [ping for ping in self.noise_pings if ping.update(dt)]

    def update_particles(self, dt: float) -> None:
        self.particles = [particle for particle in self.particles if particle.update(dt)]

    def check_exit(self) -> None:
        if self.enemies or not self.player.rect.colliderect(self.exit_rect):
            return
        if self.level_index + 1 >= len(LEVELS):
            self.mode = "victory"
            self.message = "Underworld route secured"
            return
        self.score += 350 + int(max(0, 90 - self.time_alive) * 4)
        self.open_contracts(self.level_index + 1)

    def open_contracts(self, next_level_index: int) -> None:
        self.next_level_index = next_level_index
        self.pending_contracts = self.rng.sample(CONTRACTS, 3)
        self.mode = "contract"
        self.message = "Choose an underworld contract"
        self.message_timer = 0.0

    def accept_contract(self, index: int) -> None:
        if not self.pending_contracts:
            return
        contract = self.pending_contracts[max(0, min(index, len(self.pending_contracts) - 1))]
        mods = contract["mods"]
        for key, value in mods.items():
            if key in {"cooling", "dash", "score", "heat_gain", "focus"}:
                self.mods[key] = float(self.mods.get(key, 1.0)) * float(value)
            else:
                self.mods[key] = float(self.mods.get(key, 0.0)) + float(value)
        self.active_contracts.append(str(contract["name"]))
        self.pending_contracts = []
        self.reset_level(self.next_level_index, keep_score=True)
        self.mode = "playing"
        self.message = f"Contract: {contract['name']}"
        self.message_timer = 1.5

    def spawn_particles(self, x: float, y: float, color: tuple[int, int, int], count: int) -> None:
        if self.reduced_motion:
            count = max(1, count // 3)
        available = max(0, 180 - len(self.particles))
        count = min(count, available)
        for _ in range(count):
            angle = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(55, 230)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    life=self.rng.uniform(0.18, 0.55),
                    color=color,
                    radius=self.rng.uniform(2.0, 4.2),
                )
            )

    def emit_noise(self, x: float, y: float, radius: float, color: tuple[int, int, int]) -> None:
        if self.reduced_motion and radius < 170:
            return
        if len(self.noise_pings) >= 8:
            self.noise_pings.pop(0)
        self.noise_pings.append(NoisePing(x, y, 10, radius, 0.62, color))

    def build_static_world(self) -> pygame.Surface:
        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.blit(self.assets.bg, (0, 0))
        if self.high_contrast:
            contrast = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            contrast.fill((0, 0, 0, 105))
            surface.blit(contrast, (0, 0))
        for platform in self.platforms:
            rect = platform.rect
            floor = (92, 103, 116) if self.high_contrast else PALETTE["floor"]
            edge = (255, 255, 255) if self.high_contrast else PALETTE["floor_edge"]
            pygame.draw.rect(surface, floor, rect, border_radius=4)
            pygame.draw.line(surface, edge, rect.topleft, rect.topright, 2)
            for x in range(rect.left + 8, rect.right, 28):
                pygame.draw.line(surface, (45, 53, 62), (x, rect.top + 4), (x + 12, rect.bottom - 4), 1)
        return surface

    def draw(self) -> None:
        self.draw_world()
        self.draw_hud()
        if self.mode == "menu":
            self.draw_menu()
        elif self.mode == "paused":
            self.draw_overlay("Paused", "P or Esc to resume   R to restart")
        elif self.mode == "about":
            self.draw_overlay(
                "About 1313",
                "A compact Pygame action-platformer inspired by the lost underworld project.",
            )
        elif self.mode == "game_over":
            self.draw_overlay("Run failed", "Enter to retry   Esc to quit")
        elif self.mode == "victory":
            self.draw_overlay("Route secured", f"Final score {self.score}   Enter to replay")
        pygame.display.flip()

    def draw_world(self) -> None:
        self.screen.blit(self.static_world, (0, 0))

        if not self.enemies:
            pygame.draw.rect(self.screen, (12, 18, 21), self.exit_rect, border_radius=6)
            pygame.draw.rect(self.screen, PALETTE["cyan"], self.exit_rect, 3, border_radius=6)
            pygame.draw.line(
                self.screen,
                PALETTE["text"],
                (self.exit_rect.centerx - 8, self.exit_rect.centery),
                (self.exit_rect.centerx + 10, self.exit_rect.centery),
                3,
            )
            pygame.draw.line(
                self.screen,
                PALETTE["text"],
                (self.exit_rect.centerx + 4, self.exit_rect.centery - 6),
                (self.exit_rect.centerx + 10, self.exit_rect.centery),
                3,
            )
            pygame.draw.line(
                self.screen,
                PALETTE["text"],
                (self.exit_rect.centerx + 4, self.exit_rect.centery + 6),
                (self.exit_rect.centerx + 10, self.exit_rect.centery),
                3,
            )

        for ping in self.noise_pings:
            if self.reduced_motion:
                continue
            diameter = int(ping.radius * 2)
            ring = pygame.Surface((diameter + 4, diameter + 4), pygame.SRCALPHA)
            alpha = max(40, int(150 * max(0.0, ping.life / 0.62)))
            pygame.draw.circle(ring, (*ping.color, alpha), (diameter // 2 + 2, diameter // 2 + 2), int(ping.radius), 2)
            self.screen.blit(ring, (int(ping.x - ping.radius - 2), int(ping.y - ping.radius - 2)))

        for pickup in self.pickups:
            pickup.draw(self.screen)
        for bullet in self.bullets:
            outline = PALETTE["text"] if self.high_contrast else bullet.color
            pygame.draw.circle(self.screen, outline, (int(bullet.x), int(bullet.y)), bullet.radius + 2)
            pygame.draw.circle(self.screen, bullet.color, (int(bullet.x), int(bullet.y)), bullet.radius)
            if bullet.pierces:
                pygame.draw.line(
                    self.screen,
                    PALETTE["text"],
                    (int(bullet.x - math.copysign(10, bullet.vx)), int(bullet.y)),
                    (int(bullet.x + math.copysign(6, bullet.vx)), int(bullet.y)),
                    2,
                )
        for enemy in self.enemies:
            self.draw_enemy(enemy)
        self.draw_player()
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle.color, (int(particle.x), int(particle.y)), int(particle.radius))

    def draw_player(self) -> None:
        p = self.player
        frames = self.assets.player_right if p.facing >= 0 else self.assets.player_left
        if abs(p.vx) > 12 and p.on_ground:
            frame = frames[int(p.walk_time) % len(frames)]
        else:
            frame = frames[0]
        if p.invuln > 0 and int(p.invuln * 18) % 2 == 0:
            return
        if p.shield > 0:
            pygame.draw.ellipse(self.screen, PALETTE["blue"], p.full_rect().inflate(12, 8), 2)
        self.screen.blit(frame, p.sprite_pos)
        if p.dash_timer > 0:
            tail_x = p.rect.centerx - p.facing * 35
            pygame.draw.line(self.screen, PALETTE["cyan"], (tail_x, p.rect.centery), p.rect.center, 4)

    def draw_enemy(self, enemy: Enemy) -> None:
        frames = self.assets.enemy_right if enemy.direction >= 0 else self.assets.enemy_left
        frame = frames[int(enemy.walk_time) % len(frames)]
        if enemy.hit_flash > 0:
            tint = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            tint.fill((255, 255, 255, 100))
            frame = frame.copy()
            frame.blit(tint, (0, 0))
        self.screen.blit(frame, (int(enemy.x), int(enemy.y)))
        if self.player.scan_timer > 0:
            pygame.draw.rect(self.screen, PALETTE["blue"], enemy.full_rect().inflate(10, 10), 2, border_radius=5)
        if enemy.state in {"chase", "investigate"}:
            marker = "!" if enemy.state == "chase" else "?"
            color = PALETTE["red"] if enemy.state == "chase" else PALETTE["amber"]
            self.draw_text(marker, enemy.rect.centerx - 4, enemy.rect.top - 32, color, self.small_font)
        pygame.draw.rect(self.screen, (12, 14, 18), (enemy.rect.left - 4, enemy.rect.top - 13, 40, 7), border_radius=3)
        fill = int(38 * enemy.health / enemy.max_health)
        pygame.draw.rect(self.screen, enemy.color, (enemy.rect.left - 3, enemy.rect.top - 12, fill, 5), border_radius=3)

    def draw_hud(self) -> None:
        pygame.draw.rect(self.screen, (10, 13, 18), (0, 0, WIDTH, 45))
        level = LEVELS[self.level_index]
        self.draw_text(f"{level['name']}", 18, 12, PALETTE["text"], self.small_font)
        self.draw_text(f"Score {self.score}", 218, 12, PALETTE["amber"], self.small_font)
        self.draw_text(f"x{self.combo}", 326, 12, PALETTE["cyan"], self.small_font)

        x = 372
        for i in range(self.player.max_health):
            color = PALETTE["red"] if i < self.player.health else (68, 71, 78)
            pygame.draw.rect(self.screen, color, (x + i * 20, 13, 14, 14), border_radius=3)
        if self.player.shield:
            self.draw_text(f"+{self.player.shield}", x + 88, 10, PALETTE["blue"], self.small_font)

        heat_rect = pygame.Rect(508, 15, 96, 10)
        pygame.draw.rect(self.screen, (58, 63, 72), heat_rect, border_radius=4)
        heat_color = PALETTE["red"] if self.player.overheated > 0 else PALETTE["cyan"]
        pygame.draw.rect(
            self.screen,
            heat_color,
            (heat_rect.left, heat_rect.top, int(heat_rect.width * self.player.heat / 100), heat_rect.height),
            border_radius=4,
        )
        self.draw_text("H", heat_rect.left - 14, 10, heat_color, self.small_font)

        focus_rect = pygame.Rect(644, 15, 86, 10)
        pygame.draw.rect(self.screen, (58, 63, 72), focus_rect, border_radius=4)
        pygame.draw.rect(
            self.screen,
            PALETTE["blue"],
            (focus_rect.left, focus_rect.top, int(focus_rect.width * self.player.focus / self.player.max_focus), 10),
            border_radius=4,
        )
        self.draw_text("F", focus_rect.left - 13, 10, PALETTE["blue"], self.small_font)

        pressure_rect = pygame.Rect(772, 15, 58, 10)
        pygame.draw.rect(self.screen, (58, 63, 72), pressure_rect, border_radius=4)
        pressure_color = PALETTE["red"] if self.director.pressure > 0.7 else PALETTE["amber"]
        pygame.draw.rect(
            self.screen,
            pressure_color,
            (pressure_rect.left, pressure_rect.top, int(pressure_rect.width * self.director.pressure), 10),
            border_radius=4,
        )
        self.draw_text("D", pressure_rect.left - 13, 10, pressure_color, self.small_font)
        self.draw_text("M F1 H V", 856, 12, PALETTE["muted"], self.small_font)

        if self.message_timer > 0:
            self.draw_text(self.message, 18, 48, PALETTE["text"], self.font)
        elif self.director.event_timer > 0:
            self.draw_text(self.director.event, 18, 48, PALETTE["amber"], self.font)

    def draw_menu(self) -> None:
        self.draw_overlay(
            "1313: Underworld Run",
            "Enter start   A/D move   W jump   Space blaster   Shift dash   E scan   Q vent",
            footer="Heat changes shot tiers. Noise pulls patrols. H contrast, V reduced effects.",
        )

    def draw_overlay(self, title: str, body: str, footer: str | None = None) -> None:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((6, 9, 13, 178))
        self.screen.blit(dim, (0, 0))
        panel = pygame.Rect(120, 132, WIDTH - 240, 244)
        pygame.draw.rect(self.screen, PALETTE["panel"], panel, border_radius=8)
        pygame.draw.rect(self.screen, PALETTE["cyan"], panel, 2, border_radius=8)
        title_surface = self.big_font.render(title, True, PALETTE["text"])
        self.screen.blit(title_surface, (panel.centerx - title_surface.get_width() // 2, panel.top + 42))
        body_surface = self.font.render(body, True, PALETTE["muted"])
        self.screen.blit(body_surface, (panel.centerx - body_surface.get_width() // 2, panel.top + 126))
        if footer:
            footer_surface = self.small_font.render(footer, True, PALETTE["amber"])
            self.screen.blit(footer_surface, (panel.centerx - footer_surface.get_width() // 2, panel.top + 176))

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
        font: pygame.font.Font,
    ) -> None:
        shadow = font.render(text, True, (0, 0, 0))
        surface = font.render(text, True, color)
        self.screen.blit(shadow, (x + 1, y + 1))
        self.screen.blit(surface, (x, y))

    def state_snapshot(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "level": self.level_index + 1,
            "score": self.score,
            "player": {
                "x": round(self.player.x, 2),
                "y": round(self.player.y, 2),
                "vx": round(self.player.vx, 2),
                "vy": round(self.player.vy, 2),
                "health": self.player.health,
                "shield": self.player.shield,
                "heat": round(self.player.heat, 1),
                "focus": round(self.player.focus, 1),
                "scan_timer": round(self.player.scan_timer, 2),
                "on_ground": self.player.on_ground,
            },
            "enemies": [
                {
                    "kind": enemy.kind,
                    "x": round(enemy.x, 2),
                    "y": round(enemy.y, 2),
                    "health": enemy.health,
                    "state": enemy.state,
                }
                for enemy in self.enemies
            ],
            "bullets": len(self.bullets),
            "bullet_tiers": [bullet.tier for bullet in self.bullets],
            "noise_pings": len(self.noise_pings),
            "pickups": [pickup.kind for pickup in self.pickups],
            "director": {
                "pressure": round(self.director.pressure, 2),
                "spawn_timer": round(self.director.spawn_timer, 2),
                "event": self.director.event if self.director.event_timer > 0 else "",
            },
            "accessibility": {
                "high_contrast": self.high_contrast,
                "reduced_motion": self.reduced_motion,
            },
            "message": self.message if self.message_timer > 0 else "",
            "coordinate_system": "origin top-left, x right, y down",
        }

    def run(self) -> int:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.step(dt)
            self.draw()
        pygame.quit()
        return 0


def run_smoke_test(frames: int = 420) -> int:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    game = Game(muted=True)
    game.mode = "playing"
    game.director.spawn_timer = 0.35

    previous_x = game.player.x
    jumped = False
    fired = False
    scan_used = False
    vent_used = False
    director_triggered = False
    bullet_tiers: set[str] = set()
    for frame in range(frames):
        inputs = InputState(
            right=frame < 155,
            left=220 <= frame < 260,
            jump_down=frame in {18, 96, 175},
            jump_held=frame % 90 < 28,
            shoot=frame % 8 == 0,
            dash=frame in {72, 180, 310},
            pulse=frame in {42, 260},
            vent=frame in {130, 300},
        )
        game.step(1 / FPS, inputs)
        if game.player.y < LEVELS[game.level_index]["player"][1] - 8:
            jumped = True
        if game.bullets or game.score > 0:
            fired = True
        if game.player.scan_timer > 0:
            scan_used = True
        if game.player.vent_cooldown > 0:
            vent_used = True
        if game.director.event or len(game.enemies) > len(LEVELS[0]["enemies"]):
            director_triggered = True
        bullet_tiers.update(bullet.tier for bullet in game.bullets)
        if game.mode in {"game_over", "victory"}:
            break

    snapshot = game.state_snapshot()
    assertions = {
        "player_moved": game.player.x != previous_x,
        "jumped": jumped,
        "fired": fired,
        "health_nonnegative": game.player.health >= 0,
        "bullet_cap_respected": len(game.bullets) <= 7,
        "scan_used": scan_used,
        "vent_used": vent_used,
        "director_triggered": director_triggered,
        "heat_tiers_seen": bool({"piercing", "volatile"} & bullet_tiers),
        "noise_system_active": bool(game.noise_pings) or any(enemy.state != "patrol" for enemy in game.enemies),
        "mode_valid": game.mode in {"playing", "game_over", "victory"},
    }
    snapshot["observed_bullet_tiers"] = sorted(bullet_tiers)
    snapshot["assertions"] = assertions
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    pygame.quit()
    return 0 if all(assertions.values()) else 1


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run 1313: Underworld Run.")
    parser.add_argument("--mute", action="store_true", help="Start with music and sound effects muted.")
    parser.add_argument("--smoke-test", action="store_true", help="Run a deterministic headless mechanics smoke test.")
    parser.add_argument("--frames", type=int, default=420, help="Frame count for --smoke-test.")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.smoke_test:
        return run_smoke_test(args.frames)
    game = Game(muted=args.mute)
    return game.run()


if __name__ == "__main__":
    raise SystemExit(main())

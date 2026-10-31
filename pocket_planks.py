"""
Pocket Planks — Phase 2
A relaxed puzzle-platformer. Place blocks, then play the level.
"""

import pygame
import sys

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TITLE = "Pocket Planks"

# Physics
GRAVITY       = 1.1     # snappier fall
JUMP_SPEED    = 18      # higher, faster jump
SPRING_SPEED  = 34      # spring still ~2x jump
PLAYER_SPEED  = 7       # faster horizontal movement
MAX_FALL      = 22      # terminal velocity downward

# Player dimensions
PLAYER_W = 32
PLAYER_H = 44

# Block dimensions
PLANK_W,  PLANK_H  = 140, 18
BOX_W,    BOX_H    = 44,  44
SPRING_W, SPRING_H = 44,  22

# Freeze frames after spike hit  (unused in Phase 1 — placeholder)
FREEZE_FRAMES = 48

# ─────────────────────────────────────────────
#  COLOURS
# ─────────────────────────────────────────────
C_BG          = (30,  32,  40)
C_PLAYER      = (100, 200, 255)
C_PLAYER_FROZEN = (220, 100, 100)   # tint when spike-frozen
C_PLAYER_EYE  = (20,  20,  30)
C_START       = (60,  160,  60)
C_WIN         = (255, 210,  50)
C_WIN_BORDER  = (220, 160,  10)
C_STATIC      = (90,  90, 110)
C_SPIKE       = (200,  55,  55)
C_SPIKE_DARK  = (140,  30,  30)
C_PLANK       = (160, 110,  60)
C_PLANK_EDGE  = (110,  70,  30)
C_BOX         = (130, 130, 140)
C_BOX_EDGE    = ( 80,  80,  90)
C_SPRING      = ( 60, 190, 170)
C_SPRING_EDGE = ( 30, 130, 120)
C_HUD_BG      = (20,  22,  30, 180)
C_HUD_TEXT    = (230, 230, 230)
C_PHASE_BUILD = (80,  200, 120)
C_PHASE_PLAY  = (255, 160,  60)
C_GHOST       = (255, 255, 255, 60)
C_GHOST_BLOCK = (200, 200, 200, 80)


# ─────────────────────────────────────────────
#  BLOCK CLASSES
# ─────────────────────────────────────────────
class Block:
    """Base class for all place-able blocks."""
    kind   = "block"
    color  = C_BOX
    ecolor = C_BOX_EDGE
    w      = BOX_W
    h      = BOX_H

    def __init__(self, x, y):
        self.x = x   # left
        self.y = y   # top

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf, ghost=False):
        r = self.rect
        if ghost:
            s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            s.fill((*self.color[:3], 100))
            surf.blit(s, (r.x, r.y))
            pygame.draw.rect(surf, (*self.ecolor[:3], 160), r, 2)
        else:
            pygame.draw.rect(surf, self.color, r)
            pygame.draw.rect(surf, self.ecolor, r, 2)

    def snap_center(self, cx, cy):
        """Move block so its center is at (cx, cy)."""
        self.x = cx - self.w // 2
        self.y = cy - self.h // 2

    def collides_any(self, others):
        """True if this block overlaps any rect in others."""
        r = self.rect
        for o in others:
            if isinstance(o, pygame.Rect):
                if r.colliderect(o):
                    return True
            else:
                if r.colliderect(o.rect):
                    return True
        return False


class Plank(Block):
    kind   = "plank"
    color  = C_PLANK
    ecolor = C_PLANK_EDGE
    w      = PLANK_W
    h      = PLANK_H


class Box(Block):
    kind   = "box"
    color  = C_BOX
    ecolor = C_BOX_EDGE
    w      = BOX_W
    h      = BOX_H


class Spring(Block):
    kind   = "spring"
    color  = C_SPRING
    ecolor = C_SPRING_EDGE
    w      = SPRING_W
    h      = SPRING_H

    def draw(self, surf, ghost=False):
        r = self.rect
        alpha = 100 if ghost else 255
        # Body
        body = pygame.Rect(r.x, r.y + r.h // 2, r.w, r.h // 2)
        top  = pygame.Rect(r.x + 4, r.y, r.w - 8, r.h // 2)
        if ghost:
            for sub in (body, top):
                s = pygame.Surface((sub.w, sub.h), pygame.SRCALPHA)
                s.fill((*self.color[:3], 80))
                surf.blit(s, (sub.x, sub.y))
        else:
            pygame.draw.rect(surf, self.color, body)
            pygame.draw.rect(surf, self.ecolor, body, 2)
            pygame.draw.rect(surf, self.color, top)
            pygame.draw.rect(surf, self.ecolor, top, 2)
            # little coil lines
            for i in range(3):
                yy = r.y + 4 + i * 4
                pygame.draw.line(surf, self.ecolor,
                                 (r.x + 6, yy), (r.x + r.w - 6, yy), 1)


BLOCK_CLASSES = {"plank": Plank, "box": Box, "spring": Spring}


def make_block(kind, x, y):
    return BLOCK_CLASSES[kind](x, y)


# ─────────────────────────────────────────────
#  LEVEL DEFINITIONS
# ─────────────────────────────────────────────
def _rect(*args):
    return pygame.Rect(*args)


LEVELS = [
    # ── Level 1: tutorial — 1 plank, 1 spring ──────────────────────────────
    {
        "name": "Level 1 — Tutorial",
        "terrain": [
            _rect(500, 530,  180,  20),   # mid platform
            _rect(950, 380,  180,  20),   # upper platform
        ],
        "start_platform": _rect( 60, 580, 180, 20),
        "win_zone":        _rect(960, 305, 160, 55),
        "spikes":          [],
        "blocks_in_hand":  {"plank": 1, "spring": 1},
    },

    # ── Level 2: spikes + boxes ─────────────────────────────────────────────
    {
        "name": "Level 2 — Spikes",
        "terrain": [
            _rect(  0, 630, 1280,  90),   # floor
            _rect(980, 450,  240,  20),   # raised end ledge
        ],
        "start_platform": _rect( 60, 570, 180, 20),
        "win_zone":        _rect(995, 375, 200, 55),
        "spikes": [
            _rect(340, 618,  72, 12),
            _rect(560, 618,  72, 12),
            _rect(760, 618,  72, 12),
        ],
        "blocks_in_hand": {"box": 2},
    },

    # ── Level 3: spring chain ───────────────────────────────────────────────
    {
        "name": "Level 3 — Springs",
        "terrain": [
            _rect(1060, 450,  180,  20),  # landing platform at far right
        ],
        "start_platform": _rect( 60, 580, 180, 20),
        "win_zone":        _rect(1070, 375, 160, 55),
        "spikes":          [],
        "blocks_in_hand":  {"spring": 5},
    },
]


# ─────────────────────────────────────────────
#  PLAYER
# ─────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.x  = float(x)   # left
        self.y  = float(y)   # top
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.freeze_timer = 0   # frames left frozen (spike hit)
        self.spring_launched = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), PLAYER_W, PLAYER_H)

    @property
    def cx(self):
        return self.x + PLAYER_W / 2

    def respawn(self, start_platform):
        """Drop in from top of screen, land on start platform."""
        self.x  = start_platform.centerx - PLAYER_W / 2
        self.y  = -PLAYER_H * 2   # above screen
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.spring_launched = False
        self.freeze_timer = 0

    def hit_spike(self):
        """Called when the player touches a spike."""
        if self.freeze_timer == 0:   # don't re-trigger while already frozen
            self.freeze_timer = FREEZE_FRAMES
            self.vx = 0.0
            self.vy = 0.0

    def jump(self):
        if self.on_ground and self.freeze_timer == 0:
            self.vy = -JUMP_SPEED
            self.on_ground = False

    def apply_input(self, keys):
        if self.freeze_timer > 0:
            return
        if keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
        elif keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
        else:
            self.vx = 0.0

    def update(self, all_rects, start_platform, spike_rects=None):
        """Physics step.
        all_rects  — list of pygame.Rect or (rect, "spring") tuples
        spike_rects — list of pygame.Rect for spike collision
        Returns a string token or None: 'respawn', 'spring', 'spike'
        """
        result = None
        if spike_rects is None:
            spike_rects = []

        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer == 0:
                # launch straight down off screen
                self.vy = MAX_FALL
                self.vx = 0.0
            return result

        # Gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL

        self.on_ground = False

        # ── Move X ──
        self.x += self.vx
        pr = self.rect
        for info in all_rects:
            r = info[0] if isinstance(info, tuple) else info
            if pr.colliderect(r):
                if self.vx > 0:
                    self.x = r.left - PLAYER_W
                elif self.vx < 0:
                    self.x = r.right
                self.vx = 0
                pr = self.rect

        # Clamp horizontal to screen
        self.x = max(0, min(SCREEN_W - PLAYER_W, self.x))

        # ── Move Y ──
        self.y += self.vy
        pr = self.rect
        landed_spring = False
        for info in all_rects:
            is_spring = isinstance(info, tuple) and info[1] == "spring"
            r = info[0] if isinstance(info, tuple) else info
            if pr.colliderect(r):
                if self.vy > 0:   # falling
                    prev_bottom = self.y - self.vy + PLAYER_H
                    if prev_bottom <= r.top + 4:   # landed on top
                        self.y = r.top - PLAYER_H
                        self.vy = 0
                        self.on_ground = True
                        if is_spring:
                            landed_spring = True
                elif self.vy < 0:  # hitting ceiling
                    self.y = r.bottom
                    self.vy = 0
            pr = self.rect

        if landed_spring:
            self.vy = -SPRING_SPEED
            self.on_ground = False
            result = "spring"

        # ── Spike collision ──
        # Only check when not already frozen (avoid re-triggering)
        if self.freeze_timer == 0:
            pr = self.rect
            for sr in spike_rects:
                if pr.colliderect(sr):
                    self.hit_spike()
                    result = "spike"
                    break

        # ── Off bottom ──
        if self.y > SCREEN_H + 20:
            self.respawn(start_platform)
            result = "respawn"

        return result

    def draw(self, surf):
        r = self.rect
        body_col = C_PLAYER_FROZEN if self.freeze_timer > 0 else C_PLAYER
        pygame.draw.rect(surf, body_col, r, border_radius=4)
        # eyes
        eye_y = r.y + 10
        pygame.draw.circle(surf, C_PLAYER_EYE, (r.x + 9,  eye_y), 4)
        pygame.draw.circle(surf, C_PLAYER_EYE, (r.x + 23, eye_y), 4)
        pygame.draw.circle(surf, (255,255,255), (r.x + 10, eye_y), 2)
        pygame.draw.circle(surf, (255,255,255), (r.x + 24, eye_y), 2)


# ─────────────────────────────────────────────
#  GAME
# ─────────────────────────────────────────────
class Game:
    def __init__(self, screen, font_lg, font_sm, font_xs):
        self.screen   = screen
        self.font_lg  = font_lg
        self.font_sm  = font_sm
        self.font_xs  = font_xs
        self.clock    = pygame.time.Clock()
        self.level_idx = 0
        self._load_level(0)

    # ── Level loading ─────────────────────────────────────────────────────
    def _load_level(self, idx):
        self.level_idx = idx
        lvl = LEVELS[idx]
        self.level        = lvl
        self.phase        = "build"   # 'build' | 'play' | 'win'
        self.terrain      = lvl["terrain"]
        self.start_plat   = lvl["start_platform"]
        self.win_zone     = lvl["win_zone"]
        self.spikes       = lvl["spikes"]

        # blocks in hand: {kind: count}
        self.hand         = dict(lvl["blocks_in_hand"])
        self.placed       = []   # list of Block instances

        # build-phase UI state — pick the first kind that has stock
        available = [k for k, v in self.hand.items() if v > 0]
        self.selected_kind    = available[0] if available else next(iter(self.hand))
        self.dragging         = None
        self.drag_from_placed = False
        self.mouse_pos        = (0, 0)

        # spawn player on start platform
        self.player = Player(
            self.start_plat.centerx - PLAYER_W // 2,
            self.start_plat.top - PLAYER_H
        )

    def _forbidden_rects(self, exclude=None):
        """All rects where blocks must NOT be placed."""
        rects = list(self.terrain) + [self.start_plat, self.win_zone]
        for b in self.placed:
            if b is not exclude:
                rects.append(b.rect)
        return rects

    def _is_placeable(self, block, exclude=None):
        """True if block position is valid (on screen, no overlap with forbidden)."""
        r = block.rect
        # Must be at least partially on screen
        if r.right < 0 or r.left > SCREEN_W or r.bottom < 0 or r.top > SCREEN_H:
            return False
        for fr in self._forbidden_rects(exclude=exclude):
            if r.colliderect(fr):
                return False
        return True

    def _all_solid_rects(self):
        """All rects the player should collide with, tagged for springs."""
        rects = list(self.terrain) + [self.start_plat]
        for b in self.placed:
            if b.kind == "spring":
                rects.append((b.rect, "spring"))
            else:
                rects.append(b.rect)
        return rects

    def _on_start_platform(self):
        """True if player is standing on the start platform."""
        pr = self.player.rect
        sp = self.start_plat
        touching_top = abs((pr.bottom) - sp.top) <= 4
        horizontally_on = pr.right > sp.left and pr.left < sp.right
        return self.player.on_ground and touching_top and horizontally_on

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)

            self._update()
            self._draw()
            pygame.display.flip()

    # ── Event handling ────────────────────────────────────────────────────
    def _handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos

        if self.phase == "build":
            self._build_event(event)
        elif self.phase == "play":
            self._play_event(event)
        elif self.phase == "win":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                next_idx = self.level_idx + 1
                if next_idx < len(LEVELS):
                    self._load_level(next_idx)
                # else: stay on win screen (beat the game)

    def _build_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Number keys to select block type
            if event.key == pygame.K_1 and "plank" in self.hand:
                self.selected_kind = "plank"
            elif event.key == pygame.K_2 and "box" in self.hand:
                self.selected_kind = "box"
            elif event.key == pygame.K_3 and "spring" in self.hand:
                self.selected_kind = "spring"

            if event.key == pygame.K_SPACE:
                self.phase = "play"
                self.dragging = None
                # ensure selected_kind is still valid (counts may have changed)
                if self.hand.get(self.selected_kind, 0) == 0:
                    available = [k for k, v in self.hand.items() if v > 0]
                    if available:
                        self.selected_kind = available[0]
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Clicking a placed block picks it up for re-positioning
            for b in reversed(self.placed):
                if b.rect.collidepoint(mx, my):
                    self.placed.remove(b)
                    self.dragging = b
                    self.drag_from_placed = True
                    return
            # Otherwise try to grab a new block from hand
            if self.hand.get(self.selected_kind, 0) > 0:
                cls = BLOCK_CLASSES[self.selected_kind]
                b = cls(0, 0)
                b.snap_center(mx, my)
                self.dragging = b
                self.drag_from_placed = False
                self.hand[self.selected_kind] -= 1

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging is not None:
                b = self.dragging
                b.snap_center(*event.pos)
                if self._is_placeable(b):
                    self.placed.append(b)
                else:
                    self.hand[b.kind] = self.hand.get(b.kind, 0) + 1
                self.dragging = None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # Right-click a placed block → return it to hand
            mx, my = event.pos
            for b in reversed(self.placed):
                if b.rect.collidepoint(mx, my):
                    self.placed.remove(b)
                    self.hand[b.kind] = self.hand.get(b.kind, 0) + 1
                    return

    def _play_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                if self._on_start_platform():
                    self.phase = "build"
                else:
                    self.player.jump()

    # ── Update ────────────────────────────────────────────────────────────
    def _update(self):
        if self.phase != "play":
            return

        keys = pygame.key.get_pressed()
        self.player.apply_input(keys)

        # _all_solid_rects returns plain Rects and (rect, "spring") tuples
        collision_list = self._all_solid_rects()
        result = self.player.update(collision_list, self.start_plat,
                                    spike_rects=self.spikes)

        # Win check — only when player is alive (not mid-respawn)
        if self.player.y < SCREEN_H and self.win_zone.colliderect(self.player.rect):
            next_idx = self.level_idx + 1
            if next_idx < len(LEVELS):
                self._load_level(next_idx)
            else:
                self.phase = "win"

    # ── Drawing ───────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(C_BG)

        # Static terrain
        for r in self.terrain:
            pygame.draw.rect(self.screen, C_STATIC, r)
            pygame.draw.rect(self.screen, (50, 50, 65), r, 2)

        # Start platform
        pygame.draw.rect(self.screen, C_START, self.start_plat)
        pygame.draw.rect(self.screen, (30, 110, 30), self.start_plat, 2)

        # Win zone
        pygame.draw.rect(self.screen, C_WIN, self.win_zone)
        pygame.draw.rect(self.screen, C_WIN_BORDER, self.win_zone, 3)
        lbl = self.font_xs.render("WIN", True, (80, 50, 0))
        self.screen.blit(lbl, lbl.get_rect(center=self.win_zone.center))

        # Spikes — draw a row of triangles for each spike rect
        for sr in self.spikes:
            spike_w = 16   # width of each individual spike triangle
            count   = max(1, sr.w // spike_w)
            for i in range(count):
                bx = sr.x + i * spike_w
                tip_x = bx + spike_w // 2
                pts = [
                    (bx,           sr.bottom),
                    (tip_x,        sr.top),
                    (bx + spike_w, sr.bottom),
                ]
                pygame.draw.polygon(self.screen, C_SPIKE, pts)
                pygame.draw.polygon(self.screen, C_SPIKE_DARK, pts, 1)

        # Placed blocks
        for b in self.placed:
            b.draw(self.screen)

        # Ghost block (build phase cursor preview)
        if self.phase == "build":
            self._draw_ghost()

        # Player
        if self.phase in ("play", "build"):
            self.player.draw(self.screen)

        # HUD
        self._draw_hud()

        # Win overlay
        if self.phase == "win":
            self._draw_win_screen()

    def _draw_ghost(self):
        if self.dragging is not None:
            b = self.dragging
            b.snap_center(*self.mouse_pos)
            ok = self._is_placeable(b)
            b.draw(self.screen, ghost=True)
            if not ok:
                # red tint to show invalid
                r = b.rect
                s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                s.fill((220, 60, 60, 80))
                self.screen.blit(s, (r.x, r.y))
        elif self.hand.get(self.selected_kind, 0) > 0:
            cls = BLOCK_CLASSES[self.selected_kind]
            b_temp = cls(0, 0)
            b_temp.snap_center(*self.mouse_pos)
            ok = self._is_placeable(b_temp)
            b_temp.draw(self.screen, ghost=True)
            if not ok:
                r = b_temp.rect
                s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                s.fill((220, 60, 60, 80))
                self.screen.blit(s, (r.x, r.y))

    def _draw_hud(self):
        # Phase indicator
        phase_text = "● BUILD" if self.phase == "build" else "▶ PLAY"
        phase_col  = C_PHASE_BUILD if self.phase == "build" else C_PHASE_PLAY
        ps = self.font_sm.render(phase_text, True, phase_col)
        self.screen.blit(ps, (20, 16))

        # Level name
        lvl_s = self.font_xs.render(self.level["name"], True, (170, 170, 180))
        self.screen.blit(lvl_s, (20, 46))

        # Block inventory
        if self.phase == "build":
            panel_x = SCREEN_W - 220
            panel_y = 16
            kinds = list(self.hand.keys())
            box_size = 48
            gap = 12

            for i, kind in enumerate(kinds):
                count = self.hand.get(kind, 0)
                bx = panel_x + i * (box_size + gap)
                by = panel_y

                # Highlight selected
                sel = (kind == self.selected_kind)
                bg_col = (60, 62, 80) if not sel else (90, 92, 120)
                border_col = (120, 120, 140) if not sel else (200, 200, 100)
                pygame.draw.rect(self.screen, bg_col,    (bx, by, box_size, box_size), border_radius=6)
                pygame.draw.rect(self.screen, border_col,(bx, by, box_size, box_size), 2, border_radius=6)

                # Mini block icon
                cls = BLOCK_CLASSES[kind]
                icon_w = min(cls.w, box_size - 8)
                icon_h = min(cls.h, box_size - 8)
                icon_r = pygame.Rect(bx + (box_size - icon_w)//2,
                                     by + (box_size - icon_h)//2 - 4,
                                     icon_w, icon_h)
                col = cls.color if count > 0 else (80, 80, 80)
                pygame.draw.rect(self.screen, col, icon_r, border_radius=3)

                # Count
                cnt_s = self.font_xs.render(str(count), True, C_HUD_TEXT)
                self.screen.blit(cnt_s, cnt_s.get_rect(center=(bx + box_size//2, by + box_size - 8)))

                # Kind label
                kl = self.font_xs.render(kind, True, (150, 150, 160))
                self.screen.blit(kl, kl.get_rect(center=(bx + box_size//2, by + box_size + 10)))

            # Instruction hints
            hints = [
                "Click to place  •  Right-click to pick up",
                "SPACE — start playing",
            ]
            for j, h in enumerate(hints):
                hs = self.font_xs.render(h, True, (120, 120, 135))
                self.screen.blit(hs, (SCREEN_W - 320, SCREEN_H - 48 + j * 18))

        elif self.phase == "play":
            hints = ["A/D — move   W/SPACE — jump"]
            if self._on_start_platform():
                hints.append("SPACE — back to build")
            for j, h in enumerate(hints):
                hs = self.font_xs.render(h, True, (120, 120, 135))
                self.screen.blit(hs, (SCREEN_W - 280, SCREEN_H - 48 + j * 18))

    def _draw_win_screen(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_lg.render("You Beat the Game!", True, C_WIN)
        sub   = self.font_sm.render("Thanks for playing Pocket Planks  🎉", True, (200, 200, 200))
        hint  = self.font_xs.render("(press SPACE to play again  — restart the game)", True, (120, 120, 135))
        cy = SCREEN_H // 2
        self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, cy - 40)))
        self.screen.blit(sub,   sub.get_rect(center=(SCREEN_W//2, cy + 20)))
        self.screen.blit(hint,  hint.get_rect(center=(SCREEN_W//2, cy + 60)))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)

    font_lg = pygame.font.SysFont("Arial", 52, bold=True)
    font_sm = pygame.font.SysFont("Arial", 26, bold=True)
    font_xs = pygame.font.SysFont("Arial", 17)

    game = Game(screen, font_lg, font_sm, font_xs)
    game.run()


if __name__ == "__main__":
    main()

"""
Pocket Planks — Phase 2
A relaxed puzzle-platformer. Place blocks, then play the level.
"""

import pygame
import sys

import art

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TITLE = "Pocket Planks"

# Physics
GRAVITY       = 1.1     # snappier fall
JUMP_SPEED    = 18      # higher, faster jump
SPRING_SPEED  = 25      # ~2x jump height (height scales with speed squared)
PLAYER_SPEED  = 7       # faster horizontal movement
MAX_FALL      = 22      # terminal velocity downward

# Fixed timestep — physics always runs at FPS steps per second
STEP_MS             = 1000 / FPS
LOOP_HZ             = FPS * 2   # checking twice per step keeps steps evenly spaced
MAX_STEPS_PER_FRAME = 5         # a longer hitch is skipped, not fast-forwarded

# Jump assists
COYOTE_FRAMES      = 6   # frames after walking off an edge that a jump still works
JUMP_BUFFER_FRAMES = 6   # frames before landing that a W press still counts
JUMP_CUT_SPEED     = 6   # upward speed a jump drops to when W is released

# Player dimensions
PLAYER_W = 32
PLAYER_H = 44

# Block dimensions
PLANK_W,  PLANK_H  = 140, 18
BOX_W,    BOX_H    = 44,  44
SPRING_W, SPRING_H = 44,  22

# Placed blocks snap their top-left corner to this grid
GRID = 22

# Freeze frames after spike hit  (unused in Phase 1 — placeholder)
FREEZE_FRAMES = 48

# ─────────────────────────────────────────────
#  BLOCK CLASSES
# ─────────────────────────────────────────────
class Block:
    """Base class for all place-able blocks."""
    kind   = "block"
    w      = BOX_W
    h      = BOX_H

    def __init__(self, x, y):
        self.x = x   # left
        self.y = y   # top

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf, ghost=False):
        sprite = art.ghost if ghost else art.block
        surf.blit(sprite(self.kind, self.w, self.h), self.rect)

    def snap_center(self, cx, cy):
        """Move block to the grid point that puts its center closest to (cx, cy)."""
        self.x = (cx - self.w // 2 + GRID // 2) // GRID * GRID
        self.y = (cy - self.h // 2 + GRID // 2) // GRID * GRID

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
    w      = PLANK_W
    h      = PLANK_H


class Box(Block):
    kind   = "box"
    w      = BOX_W
    h      = BOX_H


class Spring(Block):
    kind   = "spring"
    w      = SPRING_W
    h      = SPRING_H


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
        # The ledge is too high and far for either block alone: jump onto the
        # plank, then onto the spring.
        "terrain": [
            _rect(800, 320,  240,  20),   # upper ledge
        ],
        "start_platform": _rect( 60, 580, 180, 20),
        "win_zone":        _rect(810, 245, 220, 55),
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
        self.facing = 1   # 1 = right, -1 = left
        self.on_ground = False
        self.freeze_timer = 0   # frames left frozen (spike hit)
        self.spike_falling = False   # dropping through everything after a freeze
        self.coyote_timer = 0   # frames left to jump after walking off an edge
        self.jump_buffer = 0    # frames left for a W press to count on landing
        self.jump_cuttable = False   # releasing W can shorten this rise (not springs)

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
        self.freeze_timer = 0
        self.spike_falling = False
        self.coyote_timer = 0
        self.jump_buffer = 0

    def hit_spike(self):
        """Called when the player touches a spike."""
        if self.freeze_timer == 0:   # don't re-trigger while already frozen
            self.freeze_timer = FREEZE_FRAMES
            self.vx = 0.0
            self.vy = 0.0
            self.on_ground = False
            self.coyote_timer = 0
            self.jump_buffer = 0

    def press_jump(self):
        """W pressed: jump now if possible, otherwise remember it for landing."""
        if self.freeze_timer > 0 or self.spike_falling:
            return
        self.jump_buffer = JUMP_BUFFER_FRAMES + 1   # +1: the current step uses one up
        self._try_jump()

    def release_jump(self):
        """W released: cut a rising jump short."""
        if self.jump_cuttable and self.vy < -JUMP_CUT_SPEED:
            self.vy = -JUMP_CUT_SPEED

    def _try_jump(self):
        """Jump if standing or within coyote time. True if the jump happened."""
        if not (self.on_ground or self.coyote_timer > 0):
            return False
        self.vy = -JUMP_SPEED
        self.on_ground = False
        self.coyote_timer = 0
        self.jump_buffer = 0
        self.jump_cuttable = True
        return True

    def apply_input(self, keys):
        if self.freeze_timer > 0 or self.spike_falling:
            return
        if keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing = -1
        elif keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing = 1
        else:
            self.vx = 0.0

    def update(self, all_rects, start_platform, spike_rects=None):
        """Physics step.
        all_rects  — list of pygame.Rect or (rect, "spring") tuples
        spike_rects — list of pygame.Rect for spike collision
        Returns a string token or None: 'respawn', 'spring', 'spike', or
        'jump' for a buffered jump, which lands and takes off in the same step
        """
        result = None
        if spike_rects is None:
            spike_rects = []

        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer == 0:
                # drop straight down off screen, through floors and blocks
                self.spike_falling = True
            return result

        if self.spike_falling:
            self.y += MAX_FALL
            if self.y > SCREEN_H + 20:
                self.respawn(start_platform)
                result = "respawn"
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
            self.coyote_timer = 0
            self.jump_buffer = 0
            self.jump_cuttable = False
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

        # ── Buffered jump, on the landing frame ──
        if self.on_ground and self.jump_buffer > 0 and self._try_jump():
            result = "jump"

        # ── Off bottom ──
        if self.y > SCREEN_H + 20:
            self.respawn(start_platform)
            result = "respawn"

        # ── Jump timers ──
        if self.on_ground:
            self.coyote_timer = COYOTE_FRAMES + 1   # +1: the step leaving the edge uses one up
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        return result

    def draw(self, surf):
        hurt = self.freeze_timer > 0 or self.spike_falling
        sprite = art.player(PLAYER_W, PLAYER_H, self.facing, hurt)
        surf.blit(sprite, self.rect.move(-art.PLAYER_PAD, -art.PLAYER_PAD))


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
        rects = list(self.terrain) + list(self.spikes)
        rects += [self.start_plat, self.win_zone, self.player.rect]
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

    def _inventory_slots(self):
        """(kind, rect) for each block slot in the HUD."""
        panel_x, panel_y = SCREEN_W - 220, 16
        box_size, gap = 48, 12
        return [(kind, pygame.Rect(panel_x + i * (box_size + gap), panel_y,
                                   box_size, box_size))
                for i, kind in enumerate(self.hand)]

    def _select_available(self):
        """Move the selection to a block still in hand, if the current one ran out."""
        if self.hand.get(self.selected_kind, 0) == 0:
            available = [k for k, v in self.hand.items() if v > 0]
            if available:
                self.selected_kind = available[0]

    def _on_start_platform(self):
        """True if player is standing on the start platform."""
        pr = self.player.rect
        sp = self.start_plat
        touching_top = abs((pr.bottom) - sp.top) <= 4
        horizontally_on = pr.right > sp.left and pr.left < sp.right
        return self.player.on_ground and touching_top and horizontally_on

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        accumulator = 0.0
        while True:
            accumulator += min(self.clock.tick(LOOP_HZ),
                               MAX_STEPS_PER_FRAME * STEP_MS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)

            stepped = False
            while accumulator >= STEP_MS:
                self._update()
                accumulator -= STEP_MS
                stepped = True

            if stepped:
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

    def _build_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Number keys to select block type
            if event.key == pygame.K_1 and self.hand.get("plank", 0) > 0:
                self.selected_kind = "plank"
            elif event.key == pygame.K_2 and self.hand.get("box", 0) > 0:
                self.selected_kind = "box"
            elif event.key == pygame.K_3 and self.hand.get("spring", 0) > 0:
                self.selected_kind = "spring"

            if event.key == pygame.K_SPACE:
                self.phase = "play"
                # a block still being dragged goes back to the hand
                if self.dragging is not None:
                    self.hand[self.dragging.kind] += 1
                    self.dragging = None
                self._select_available()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Clicking an inventory slot chooses that block
            for kind, slot in self._inventory_slots():
                if slot.collidepoint(mx, my):
                    self.selected_kind = kind
                    return
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
                self._select_available()

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
            if event.key == pygame.K_w:
                self.player.press_jump()
            elif event.key == pygame.K_SPACE and self._on_start_platform():
                self.phase = "build"
        elif event.type == pygame.KEYUP and event.key == pygame.K_w:
            self.player.release_jump()

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

        # Win check — the player has to land, not just pass through the zone
        landed = self.player.on_ground or result == "jump"
        if landed and self.win_zone.colliderect(self.player.rect):
            next_idx = self.level_idx + 1
            if next_idx < len(LEVELS):
                self._load_level(next_idx)
            else:
                self.phase = "win"

    # ── Drawing ───────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.blit(art.background(SCREEN_W, SCREEN_H), (0, 0))

        # Placement grid
        if self.phase == "build":
            self.screen.blit(art.grid_dots(SCREEN_W, SCREEN_H, GRID), (0, 0))

        # Static terrain
        for r in self.terrain:
            self.screen.blit(art.ground(r.w, r.h), r)

        # Start platform, marked with a flag
        self.screen.blit(art.ground(self.start_plat.w, self.start_plat.h),
                         self.start_plat)
        pole = art.flag()
        self.screen.blit(pole, (self.start_plat.x + 8,
                                self.start_plat.top - pole.get_height()))

        # Win zone
        self.screen.blit(art.win_zone(self.win_zone.w, self.win_zone.h),
                         self.win_zone)

        # Spikes
        for sr in self.spikes:
            self.screen.blit(art.spikes(sr.w, sr.h), sr)

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
        # Phase indicator and level name
        self.screen.blit(art.panel(190, 78), (10, 8))
        phase_text = "BUILD" if self.phase == "build" else "PLAY"
        phase_col  = art.LEAF_LIGHT if self.phase == "build" else art.GOLD_LIGHT
        self.screen.blit(art.text(self.font_sm, phase_text, phase_col), (24, 14))
        self.screen.blit(art.text(self.font_xs, self.level["name"]), (24, 48))

        # Block inventory
        if self.phase == "build":
            slots = self._inventory_slots()
            left = slots[0][1].left - 12
            self.screen.blit(art.panel(slots[-1][1].right + 12 - left, 92), (left, 8))

            for kind, slot in slots:
                count = self.hand.get(kind, 0)
                bx, by = slot.topleft
                box_size = slot.w

                # Highlight selected
                sel = (kind == self.selected_kind)
                self.screen.blit(art.slot(box_size, sel), slot)

                # Block icon, greyed out when none are left
                icon = art.icon(kind, box_size - 16, count == 0)
                self.screen.blit(icon, icon.get_rect(center=slot.center))

                # Count
                cnt_s = art.text(self.font_xs, str(count))
                self.screen.blit(cnt_s, cnt_s.get_rect(center=(bx + box_size - 8, by + box_size - 8)))

                # Kind label
                kl = art.text(self.font_xs, kind)
                self.screen.blit(kl, kl.get_rect(center=(bx + box_size//2, by + box_size + 16)))

            # Instruction hints
            hints = [
                "Click an icon to choose  •  Click to place",
                "Drag to move  •  Right-click to pick up",
                "SPACE — start playing",
            ]
            self._draw_hints(hints)

        elif self.phase == "play":
            hints = ["A/D — move   W — jump"]
            if self._on_start_platform():
                hints.append("SPACE — back to build")
            self._draw_hints(hints)

    def _draw_hints(self, hints):
        """Hint lines stacked in the bottom-right corner."""
        top = SCREEN_H - 12 - len(hints) * 20
        for j, h in enumerate(hints):
            hs = art.text(self.font_xs, h)
            self.screen.blit(hs, hs.get_rect(topright=(SCREEN_W - 14, top + j * 20)))

    def _draw_win_screen(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 180))
        self.screen.blit(overlay, (0, 0))

        title = art.text(self.font_lg, "You Beat the Game!", art.GOLD)
        sub   = art.text(self.font_sm, "Thanks for playing Pocket Planks")
        cy = SCREEN_H // 2
        self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, cy - 40)))
        self.screen.blit(sub,   sub.get_rect(center=(SCREEN_W//2, cy + 20)))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)

    font_lg = pygame.font.SysFont("arialroundedmtbold,arial", 52)
    font_sm = pygame.font.SysFont("arialroundedmtbold,arial", 26)
    font_xs = pygame.font.SysFont("arialroundedmtbold,arial", 17)

    game = Game(screen, font_lg, font_sm, font_xs)
    game.run()


if __name__ == "__main__":
    main()

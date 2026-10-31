"""
Pocket Planks — art
Cartoon sprites drawn in code with pygame: dark outlines, flat colour with one
highlight, grass-over-dirt terrain and white "sticker" borders on icons.

Everything is drawn at S times its final size and smooth-scaled down, which
gives clean anti-aliased edges. Sprites are cached, so each is only drawn once.
"""

import math
import random
from functools import lru_cache

import pygame

S = 4   # supersampling factor

# ─────────────────────────────────────────────
#  PALETTE
# ─────────────────────────────────────────────
SKY          = (155, 203, 219)
HILL         = (140, 190, 196)
CLOUD        = (226, 241, 244)
WATER        = (122, 182, 204)
WATER_LIGHT  = (168, 214, 228)
OUTLINE      = ( 58,  38,  30)
WHITE        = (255, 255, 255)

GRASS        = (134, 184,  82)
GRASS_TUFT   = (112, 164,  70)
GRASS_RIM    = (184, 219, 108)
GRASS_DARK   = ( 74, 117,  66)
GRASS_EDGE   = ( 56,  92,  54)
DIRT         = (134,  88,  76)
DIRT_MARK    = (112,  70,  60)
DIRT_EDGE    = ( 92,  56,  50)

WOOD         = (201, 150,  84)
WOOD_LIGHT   = (230, 190, 120)
WOOD_DARK    = (150, 100,  52)
WOOD_DEEP    = (112,  72,  38)
NAIL         = ( 96,  84,  76)

STEEL        = (172, 176, 180)
STEEL_LIGHT  = (226, 230, 232)
STEEL_DARK   = (104, 108, 116)
RED          = (196,  62,  52)
RED_LIGHT    = (236, 122, 104)
RED_DARK     = (140,  36,  34)

GOLD         = (246, 200,  70)
GOLD_LIGHT   = (255, 232, 136)
GOLD_DARK    = (206, 146,  34)

ORANGE       = (240, 146,  62)
ORANGE_LIGHT = (252, 186, 104)
ORANGE_DARK  = (206, 104,  40)
LEAF         = (106, 176,  72)
LEAF_LIGHT   = (160, 212,  96)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def _canvas(w, h):
    return pygame.Surface((w * S, h * S), pygame.SRCALPHA)


def _finish(canvas):
    return pygame.transform.smoothscale(
        canvas, (canvas.get_width() // S, canvas.get_height() // S))


def _circle(canvas, color, x, y, r):
    pygame.draw.circle(canvas, color, (int(x * S), int(y * S)), int(r * S))


def _ellipse(canvas, color, x, y, w, h):
    pygame.draw.ellipse(canvas, color,
                        (int(x * S), int(y * S), int(w * S), int(h * S)))


def _rrect(canvas, color, x, y, w, h, r=0, width=0):
    pygame.draw.rect(canvas, color,
                     (int(x * S), int(y * S), int(w * S), int(h * S)),
                     int(width * S), border_radius=int(r * S))


def _line(canvas, color, a, b, width=1):
    pygame.draw.line(canvas, color,
                     (int(a[0] * S), int(a[1] * S)),
                     (int(b[0] * S), int(b[1] * S)), int(width * S))


def _poly(canvas, color, pts, width=0):
    pygame.draw.polygon(canvas, color,
                        [(int(x * S), int(y * S)) for x, y in pts], int(width * S))


def _sticker(surf, border=2):
    """Add a white die-cut border around a sprite."""
    k = 3
    pad = border + 1
    w, h = surf.get_size()
    big = pygame.transform.smoothscale(surf, (w * k, h * k))
    out = pygame.Surface(((w + pad * 2) * k, (h + pad * 2) * k), pygame.SRCALPHA)
    white = pygame.mask.from_surface(big).to_surface(
        setcolor=WHITE + (255,), unsetcolor=(0, 0, 0, 0))
    for i in range(24):
        a = i * math.tau / 24
        out.blit(white, (pad * k + round(math.cos(a) * border * k),
                         pad * k + round(math.sin(a) * border * k)))
    out.blit(big, (pad * k, pad * k))
    return pygame.transform.smoothscale(out, (w + pad * 2, h + pad * 2))


# ─────────────────────────────────────────────
#  BACKGROUND
# ─────────────────────────────────────────────
def _cloud(w, h):
    c = _canvas(w, h)
    for fx, fy, fr in ((.22, .68, .22), (.42, .46, .32), (.64, .54, .26), (.82, .72, .16)):
        _circle(c, CLOUD, w * fx, h * fy, h * fr * 1.5)
    _rrect(c, CLOUD, w * .08, h * .62, w * .84, h * .34, h * .17)
    return _finish(c)


@lru_cache(maxsize=None)
def background(w, h):
    surf = pygame.Surface((w, h))
    surf.fill(SKY)

    # Distant hills
    water_top = h - 44
    for cx, r in ((180, 170), (470, 120), (820, 210), (1160, 150)):
        pygame.draw.circle(surf, HILL, (cx, water_top + r // 2), r)

    for x, y, cw, ch in ((90, 70, 170, 62), (430, 130, 120, 44),
                         (720, 50, 200, 70), (1010, 170, 130, 48)):
        surf.blit(_cloud(cw, ch), (x, y))

    # Water, with crescent ripples
    pygame.draw.rect(surf, WATER, (0, water_top, w, 44))
    pygame.draw.rect(surf, WATER_LIGHT, (0, water_top, w, 3))
    rng = random.Random(7)
    for _ in range(26):
        x, y = rng.randrange(w), rng.randrange(water_top + 10, h - 6)
        pygame.draw.arc(surf, WATER_LIGHT, (x, y, 28, 10), math.pi, math.tau, 2)
    return surf


# ─────────────────────────────────────────────
#  TERRAIN
# ─────────────────────────────────────────────
@lru_cache(maxsize=None)
def ground(w, h):
    """Grass strip with a scalloped dark edge over rounded dirt."""
    c = _canvas(w, h)
    thin = h < 40
    grass_h  = 6 if thin else 14
    scallop  = 4 if thin else 9
    corner   = min(h // 2, 16)
    rng = random.Random(w * 1000 + h)

    _rrect(c, DIRT, 0, 0, w, h)

    # Dark grass overhang
    band = grass_h + scallop * .6
    _rrect(c, GRASS_DARK, 0, 0, w, band)
    x = -scallop
    while x < w + scallop:
        r = scallop * rng.uniform(.75, 1.05)
        _circle(c, GRASS_DARK, x, band, r)
        x += r * 1.5

    # Grass surface and its light rim
    _rrect(c, GRASS, 0, 0, w, grass_h)
    _rrect(c, GRASS_RIM, 0, grass_h - 2, w, 2)
    x = 0
    while x < w:
        step = rng.uniform(16, 34)
        _circle(c, GRASS_RIM, x, grass_h - 1, 1.6)
        x += step

    # Dirt marks and grass tufts on the taller pieces
    if not thin:
        for _ in range(w * h // 2600):
            mx = rng.uniform(8, w - 22)
            my = rng.uniform(grass_h + scallop + 8, h - 12)
            rect = (int(mx * S), int(my * S), 16 * S, 8 * S)
            pygame.draw.arc(c, DIRT_MARK, rect, math.pi, math.tau, S * 2)
        for _ in range(w // 90):
            mx = rng.uniform(8, w - 14)
            _ellipse(c, GRASS_TUFT, mx, 3, 7, 5)
            _ellipse(c, GRASS_TUFT, mx + 6, 3, 7, 5)

    # Round the bottom corners, then outline
    shape = pygame.Surface(c.get_size(), pygame.SRCALPHA)
    box = (0, 0, w * S, h * S)
    radii = dict(border_top_left_radius=3 * S, border_top_right_radius=3 * S,
                 border_bottom_left_radius=corner * S,
                 border_bottom_right_radius=corner * S)
    pygame.draw.rect(shape, WHITE + (255,), box, **radii)
    c.blit(shape, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    split = (grass_h + scallop) * S
    c.set_clip((0, 0, w * S, split))
    pygame.draw.rect(c, GRASS_EDGE, box, 2 * S, **radii)
    c.set_clip((0, split, w * S, h * S))
    pygame.draw.rect(c, DIRT_EDGE, box, 2 * S, **radii)
    c.set_clip(None)
    return _finish(c)


@lru_cache(maxsize=None)
def flag():
    """Red pennant marking the start platform. Stands on its bottom edge."""
    w, h = 34, 62
    c = _canvas(w, h)
    _poly(c, OUTLINE, [(6, 3), (32, 12), (6, 23)])
    _poly(c, RED, [(8, 6), (28, 12), (8, 20)])
    _poly(c, RED_LIGHT, [(8, 6), (18, 9.5), (8, 12)])
    _rrect(c, OUTLINE, 3, 0, 5, h, 2)
    _rrect(c, WOOD, 4, 1, 3, h - 2, 1)
    return _finish(c)


@lru_cache(maxsize=None)
def spikes(w, h):
    """Row of steel teeth filling the whole hitbox, with red tips."""
    c = _canvas(w, h)
    count = max(1, round(w / 16))
    tooth = w / count
    for i in range(count):
        left, tip, right = i * tooth, (i + .5) * tooth, (i + 1) * tooth
        _poly(c, OUTLINE, [(left, h), (tip, 0), (right, h)])
        _poly(c, STEEL, [(left + 1.5, h - 1), (tip, 2.5), (right - 1.5, h - 1)])
        _poly(c, STEEL_DARK, [(tip, 2.5), (right - 1.5, h - 1), (tip, h - 1)])
        _poly(c, RED, [(tip - 2, 6), (tip, 2.5), (tip + 2, 6)])
    return _finish(c)


# ─────────────────────────────────────────────
#  BLOCKS
# ─────────────────────────────────────────────
def _plank(w, h):
    c = _canvas(w, h)
    _rrect(c, OUTLINE, 0, 0, w, h, 4)
    _rrect(c, WOOD_DARK, 2, 2, w - 4, h - 4, 3)
    _rrect(c, WOOD, 2, 2, w - 4, h - 7, 3)
    _rrect(c, WOOD_LIGHT, 4, 3, w - 8, 2, 1)
    rng = random.Random(w)
    for _ in range(max(3, w // 22)):
        x = rng.uniform(10, w - 34)
        y = rng.uniform(6.5, max(7, h - 8))
        _line(c, WOOD_DARK, (x, y), (x + rng.uniform(10, 24), y), 1)
    for x in (7, w - 7):
        _circle(c, NAIL, x, h / 2 - 1, 1.6)
    return _finish(c)


def _box(w, h):
    c = _canvas(w, h)
    _rrect(c, OUTLINE, 0, 0, w, h, 5)
    _rrect(c, WOOD, 2, 2, w - 4, h - 4, 4)
    _rrect(c, WOOD_DARK, 8, 8, w - 16, h - 16, 2)
    # Boards behind the brace
    for i in range(1, 3):
        x = 8 + i * (w - 16) / 3
        _line(c, WOOD_DEEP, (x, 8), (x, h - 9), 1)
    _line(c, WOOD, (9, h - 11), (w - 11, 9), 5)
    _line(c, WOOD_LIGHT, (9, h - 13), (w - 13, 9), 1)
    _rrect(c, WOOD_LIGHT, 4, 3, w - 8, 2, 1)
    _rrect(c, OUTLINE, 7, 7, w - 14, h - 14, 2, 1)
    for x, y in ((5, 5), (w - 5, 5), (5, h - 5), (w - 5, h - 5)):
        _circle(c, NAIL, x, y, 1.6)
    return _finish(c)


def _spring(w, h):
    """Wooden base, steel coil and a red cap. The cap is the top of the hitbox."""
    c = _canvas(w, h)
    cap_h = h * .34
    base_h = h * .3
    _rrect(c, OUTLINE, 1, h - base_h, w - 2, base_h, 3)
    _rrect(c, WOOD, 3, h - base_h + 1.5, w - 6, base_h - 3, 2)
    top, bottom = cap_h - 1, h - base_h + 1
    coils = 3
    for i in range(coils):
        y = top + (bottom - top) * i / coils
        ch = (bottom - top) / coils + 2
        _ellipse(c, OUTLINE, 7, y - .5, w - 14, ch)
        _ellipse(c, STEEL, 8.5, y + .5, w - 17, ch - 2)
        _ellipse(c, STEEL_LIGHT, 11, y + .5, w - 26, 1.5)
    _rrect(c, OUTLINE, 0, 0, w, cap_h, 3.5)
    _rrect(c, RED, 2, 1.5, w - 4, cap_h - 3, 2)
    _rrect(c, RED_LIGHT, 5, 2, w - 16, 1.5, 1)
    return _finish(c)


_BLOCK_ART = {"plank": _plank, "box": _box, "spring": _spring}


@lru_cache(maxsize=None)
def block(kind, w, h):
    return _BLOCK_ART[kind](w, h)


@lru_cache(maxsize=None)
def ghost(kind, w, h):
    """See-through copy of a block, for placement previews."""
    surf = block(kind, w, h).copy()
    surf.set_alpha(150)
    return surf


# Drawn at icon proportions: a full-length plank would shrink to a sliver
_ICON_DIMS = {"plank": (60, 20), "box": (44, 44), "spring": (44, 24)}


@lru_cache(maxsize=None)
def icon(kind, size, empty=False):
    """Stickered inventory icon, scaled to fit a size-by-size square."""
    w, h = _ICON_DIMS[kind]
    scale = size / max(w, h)
    art = pygame.transform.smoothscale(
        _BLOCK_ART[kind](w, h), (round(w * scale), round(h * scale)))
    surf = _sticker(art)
    if empty:
        surf.fill((120, 120, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return surf


# ─────────────────────────────────────────────
#  PLAYER
# ─────────────────────────────────────────────
PLAYER_PAD = 3   # sprite margin around the hitbox, for the sticker border


@lru_cache(maxsize=None)
def player(w, h, facing=1, hurt=False):
    """A little turnip. Drawn facing right, then flipped when needed."""
    c = _canvas(w, h)
    body_top = 12

    # Leaves
    for pts in (((16, 15), (3, 8), (8, 1), (14, 6)),
                ((16, 15), (29, 8), (24, 1), (18, 6)),
                ((16, 15), (10, 4), (16, 0), (22, 4))):
        _poly(c, OUTLINE, pts)
        inner = [(x * .78 + 16 * .22, y * .78 + 8 * .22) for x, y in pts]
        _poly(c, LEAF, inner)
    _line(c, LEAF_LIGHT, (16, 12), (16, 4), 1)

    # Body
    _rrect(c, OUTLINE, 0, body_top, w, h - body_top, 13)
    _rrect(c, ORANGE_DARK, 2, body_top + 2, w - 4, h - body_top - 4, 11)
    _rrect(c, ORANGE, 2, body_top + 2, w - 6, h - body_top - 8, 11)
    _ellipse(c, ORANGE_LIGHT, 6, body_top + 4, 11, 5)
    for y in (h - 13, h - 8):
        _line(c, ORANGE_DARK, (8, y), (15, y), 1)

    # Face
    ey = body_top + 13
    if hurt:
        for ex in (15, 25):
            _line(c, OUTLINE, (ex - 3, ey - 3), (ex + 3, ey + 3), 2)
            _line(c, OUTLINE, (ex - 3, ey + 3), (ex + 3, ey - 3), 2)
    else:
        for ex in (15, 25):
            _ellipse(c, OUTLINE, ex - 3, ey - 4, 6, 8)
            _circle(c, WHITE, ex + 1, ey - 2, 1.4)
    _circle(c, RED_LIGHT, 10, ey + 6, 2.2)

    surf = _sticker(_finish(c), PLAYER_PAD - 1)
    if hurt:
        surf.fill((255, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
    if facing < 0:
        surf = pygame.transform.flip(surf, True, False)
    return surf


# ─────────────────────────────────────────────
#  WIN ZONE
# ─────────────────────────────────────────────
def _coin(d):
    c = _canvas(d, d)
    m = d / 2
    _circle(c, OUTLINE, m, m, m)
    _circle(c, GOLD_DARK, m, m, m - 2)
    _circle(c, GOLD, m, m - .5, m - 3.5)
    _circle(c, GOLD_LIGHT, m, m - .5, m - 6)
    _circle(c, GOLD, m, m, m - 7)
    crown = [(m - 9, m + 6), (m - 10, m - 5), (m - 4.5, m - 1), (m, m - 8),
             (m + 4.5, m - 1), (m + 10, m - 5), (m + 9, m + 6)]
    _poly(c, OUTLINE, crown)
    _poly(c, GOLD_LIGHT, [(x * .76 + m * .24, y * .76 + m * .24) for x, y in crown])
    return _sticker(_finish(c))


@lru_cache(maxsize=None)
def win_zone(w, h):
    """Soft golden glow with a crown coin at its centre."""
    c = _canvas(w, h)
    _rrect(c, (255, 214, 96, 190), 0, 0, w, h, 10)
    _rrect(c, GOLD_DARK + (255,), 0, 0, w, h, 10, 2)
    surf = _finish(c)
    coin = _coin(min(h - 12, 42))
    surf.blit(coin, coin.get_rect(center=(w // 2, h // 2)))
    rng = random.Random(w)
    for _ in range(6):
        x, y = rng.randrange(14, w - 14), rng.randrange(10, h - 10)
        if abs(x - w // 2) > 34:
            pygame.draw.line(surf, WHITE, (x - 4, y), (x + 4, y))
            pygame.draw.line(surf, WHITE, (x, y - 4), (x, y + 4))
    return surf


# ─────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────
@lru_cache(maxsize=None)
def panel(w, h):
    """Wooden sign behind HUD elements."""
    c = _canvas(w, h)
    _rrect(c, OUTLINE, 0, 0, w, h, 9)
    _rrect(c, WOOD_DARK, 2, 2, w - 4, h - 4, 7)
    _rrect(c, WOOD, 2, 2, w - 4, h - 7, 7)
    _rrect(c, WOOD_LIGHT, 7, 3, w - 14, 2, 1)
    for x, y in ((7, 7), (w - 7, 7), (7, h - 9), (w - 7, h - 9)):
        _circle(c, NAIL, x, y, 1.6)
    return _finish(c)


@lru_cache(maxsize=None)
def slot(size, selected=False):
    c = _canvas(size, size)
    _rrect(c, GOLD if selected else OUTLINE, 0, 0, size, size, 7)
    _rrect(c, WOOD_DEEP, 3, 3, size - 6, size - 6, 5)
    return _finish(c)


@lru_cache(maxsize=512)
def text(font, string, color=WHITE, outline=OUTLINE):
    """Text with a dark outline, readable over sky, grass or wood."""
    body = font.render(string, True, color)
    edge = font.render(string, True, outline)
    w, h = body.get_size()
    surf = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(edge, (2 + dx, 2 + dy))
    surf.blit(body, (2, 2))
    return surf

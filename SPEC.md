# SPEC: Pocket Planks

## The Game

Pocket Planks is a relaxed, quick puzzle-platformer that feels like a browser game. Each level gives you a small set of blocks. First you place them with the mouse, then you play the level with WASD and try to reach the win zone using only what you placed.

The fun comes from figuring out how to get across with the limited blocks you're given. Levels are short and low-pressure. Failing isn't harsh: if you fall off the bottom of the screen, you drop back in from the top onto the starting platform.

**Feel:** relaxed, fun, and quick. The jump should feel clicky and responsive, like a good platformer: no floatiness and no delay.

## How a Level Works

1. **Build phase.** The level appears with the player on the starting platform. The player can see which blocks they've been given ("in hand"). They place blocks into the level with the mouse.
2. **Play phase.** The player presses Space to start. Blocks stay where they were placed, and the player moves with WASD to try to reach the win zone.
3. **Win.** Landing in the win zone completes the level and moves on to the next one.
4. **Falling.** If the player falls off the bottom of the screen, they fall back in from the top of the screen onto the starting platform. Placed blocks stay where they are.
5. **Editing.** Whenever the player is standing on the starting platform, they can press Space to go back to the build phase, move or remove their placed blocks, and try again.

## Blocks

- **Plank:** a wide, flat platform the player can stand on. Its exact size is up to the builder; it should be a sensible size relative to the player and the rest of the level.
- **Box:** a solid square block, roughly the player's size. Unlike the plank, it's tall enough to use as a step, and boxes can be stacked.
- **Spring:** launches the player upward when they land on it, to about twice the height of a normal jump.

## Obstacles

- **Spikes:** make levels harder. Touching spikes makes the player freeze briefly, then fall straight down off the bottom of the screen. From there it works like any other fall: they drop back in from the top onto the starting platform.

## Levels

The game has 3 levels. Each level gives a different set of blocks and has different obstacles.

- **Level 1 (tutorial):** In hand: 1 plank, 1 spring. The player places the plank, jumps onto it, then jumps onto the spring to reach the win zone.
- **Level 2 (spikes):** Spikes are placed around the level. In hand: 2 boxes, used as steps to help the player get up and over the spikes. The challenge is jumping over the spikes to reach the win zone.
- **Level 3 (springs):** In hand: several springs (the builder picks the exact number to fit the layout). The player must place them so they can bounce from spring to spring, landing on each one consecutively, until they reach the win zone at the end.

## Acceptance Criteria

**Build phase**
1. Each level starts in the build phase, with the player standing still on the starting platform.
2. The blocks available for the level are shown on screen, including how many of each are left.
3. The player can choose a block and place it in the level using the mouse.
4. The player cannot place more blocks than the level gives them.
5. During the build phase, the player can pick a placed block back up (returning it to their hand) or move it.
6. Pressing Space ends the build phase and starts the play phase. During the play phase, blocks can't be moved.
7. While the player is standing on the starting platform during the play phase, pressing Space returns to the build phase with all placed blocks where they were.

**Play phase**
8. A moves the player left and D moves them right. W jumps. S does nothing.
9. The player can only jump while standing on something, and the jump starts immediately when W is pressed.
10. The player can stand on planks and boxes, and can't walk through them.
11. Landing on a spring launches the player about twice as high as a normal jump.
12. Falling below the bottom of the screen makes the player fall in from the top of the screen and land on the starting platform. Placed blocks stay where they are.
13. Touching spikes freezes the player briefly (they can't move), then they fall straight down off the bottom of the screen and respawn as in criterion 12.
14. Landing in the win zone completes the level and loads the next level.
15. Completing the last level shows a message saying the player beat the game.

**Levels**
16. Level 1 is solvable as described above with 1 plank and 1 spring.
17. Level 2 is solvable as described above with 2 boxes, and touching its spikes behaves as in criterion 13.
18. Level 3 is solvable as described above by bouncing across consecutive springs.

## Priorities

Build the core basics first. If time runs short, protect things in this order:

1. **Most important:** Level 1 fully works from start to finish: placing blocks (criteria 1–4, 6), moving and jumping (8–9), planks and springs (10–11), falling back to start (12), and the win zone (14, 16).
2. **Next:** spikes and Level 2 (13, 17), editing blocks (5, 7), and Level 3 (18).
3. **Cut first:** the end-of-game message (15).

## Out of Scope

Not needed: art beyond simple shapes, sound, menus, level select, timers, and scores. Simple and working beats fancy.

---

## Phase 3 — Complexity Expansion Plan

This section outlines planned additions beyond the original spec, to be built after the core 3 levels are solid.

### New Block Types

- **Bouncy Wall** — a vertical spring placed on a wall. Launches the player sideways on contact. Opens up wall-bounce puzzles.
- **Ice Block** — same size as a box but frictionless. The player slides on landing and can't stop quickly. Changes how you approach jumps.
- **Crumble Block** — disappears ~1 second after the player first lands on it. Forces continuous movement; can't use it as a resting spot.
- **One-Way Platform** — the player can jump up through it but lands on top. Standard platformer mechanic, useful for vertical layouts.

### New Obstacles

- **Moving Spikes** — spikes that slide back and forth on a fixed path. Requires timing rather than just block placement.
- **Saw Blade** — circular obstacle rotating along a track. Instant respawn on touch (no freeze delay).
- **Falling Platform** — static terrain that drops after ~0.5s of contact. Can be used as a block but is risky to stand on.

### Level Mechanics

- **Moving Platforms** — terrain segments that oscillate horizontally or vertically. Placed blocks stay attached to them.
- **Wind Zones** — rectangular regions that apply a constant horizontal or vertical force to the player. Can push into spikes or help reach distant platforms.
- **Locked Door / Key** — a key pickup somewhere in the level that must be collected before the win zone activates. Adds a secondary objective.
- **Scrolling Camera** — levels taller or wider than the screen, with the camera following the player. Removes the single-screen constraint.

### Additional Levels (Levels 4–7)

- **Level 4 — Crumble:** All mid-platforms are crumble blocks. Player gets 2 planks to create safe resting spots before blocks disappear.
- **Level 5 — Moving:** A wide gap with a single moving platform oscillating back and forth. Player places a spring to time a launch onto it.
- **Level 6 — Wind:** A wind zone pushes the player left. Player places boxes as windbreaks or uses the wind to reach a distant platform.
- **Level 7 — Vertical:** A tall level requiring the camera to scroll upward. Player has springs and one-way platforms to ascend.

### Gameplay Systems

- **Undo (Z key):** Reverts the last block placement in build phase. Quality of life for harder levels.
- **Block Rotation (R key):** Rotate planks and boxes before placing. A plank at 45° becomes a ramp.
- **Star Rating:** 1–3 stars per level based on blocks used. Using fewer blocks = higher rating.
- **Screen Shake:** Short camera shake on spike hit and spring launch.
- **Particles:** Dust on landing, sparkle on spring bounce, red flash on spike hit.
- **Sound:** Jump, spring, spike, and level-complete audio via `pygame.mixer`.
- **Parallax Background:** Two or three background layers scrolling at different speeds.

### Priorities for Phase 3

1. Undo and block rotation — highest value, lowest effort.
2. Crumble block + Level 4 — new mechanic that fits cleanly into existing architecture.
3. Moving platforms + Level 5 — moderate complexity, high gameplay impact.
4. Screen shake and particles — polish pass.
5. Sound — straightforward with pygame.mixer once assets exist.
6. Remaining block types, obstacles, and levels — build out as time allows.

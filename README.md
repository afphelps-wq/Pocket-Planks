# Pocket Planks

A short puzzle-platformer in Python and pygame. In each level you place a limited set of blocks with the mouse, then play with the keyboard and try to reach the gold win zone using only what you placed.

The original design is in [SPEC.md](SPEC.md). The first commit is the original author's unmodified code, so `git diff 3ea1247` shows everything changed in Phase 2.

**Status:** all 3 levels can be beaten from start to finish. Of the 18 acceptance criteria, 17 are met and 1 is partially met.

## Run the game

You need Python 3 and pygame-ce. This was tested on Python 3.13 with pygame-ce 2.5.8; plain `pygame` was not tested.

```bash
python3 -m pip install pygame-ce
python3 pocket_planks.py
```

To quit, close the window.

## Controls

| Phase | Input | Action |
|---|---|---|
| Build | Click an inventory icon, or press `1` / `2` / `3` | Choose plank / box / spring |
| Build | Left-click in the level | Place the chosen block; hold and drag to position it |
| Build | Drag a placed block | Move it |
| Build | Right-click a placed block | Return it to your hand |
| Build | `Space` | Start playing |
| Play | `A` / `D` | Move left / right |
| Play | `W` | Jump; release early for a shorter hop |
| Play | `Space` on the starting platform | Return to the build phase |

## Acceptance criteria report

Testing was done with a scripted playtest that ran the real game code without a window, sent it input events and faked which keys were held. It finished with 64 of 64 checks passing and won all 3 levels in one run. Two short follow-up checks covered criteria 4 and 6. This shows the rules work, but it does not cover a real keyboard, a real window or how the game feels.

### Build phase

| # | Criterion | Status | Notes |
|---|---|---|---|
| 1 | Level starts in build, player still on the starting platform | **Met** | Each level loads in the build phase with the player standing on the platform. |
| 2 | Available blocks and counts are shown | **Met** | The inventory panel shows each block with its count and greys out any that have run out. |
| 3 | Choose a block and place it with the mouse | **Met** | Blocks are chosen by icon or number key, and they snap to a 22 px grid when placed. |
| 4 | Can't place more than the level gives | **Met** | On Level 2, a third click after placing both boxes added nothing. |
| 5 | Pick up or move a placed block | **Met** | Right-click returns a block to the hand and dragging moves it; a move dropped on an invalid spot also goes back to the hand. |
| 6 | Space starts play; blocks can't be moved during play | **Met** | Left and right clicks during play left every block in place. |
| 7 | Space on the starting platform returns to build, blocks intact | **Met** | Blocks stayed where they were, and Space anywhere else does nothing. |

### Play phase

| # | Criterion | Status | Notes |
|---|---|---|---|
| 8 | A left, D right, W jumps, S does nothing | **Met** | All four keys were checked, and holding S moved nothing. |
| 9 | Jump only while standing, and it starts immediately | **Partially met** | A normal jump starts on the key press, but two deliberate feel changes bend the wording: a jump still works for 6 frames after walking off an edge, and a W press up to 6 frames before landing fires on landing. |
| 10 | Stand on planks and boxes, can't walk through them | **Met** | Placed blocks float where dropped and are solid from all sides. |
| 11 | Spring launches about twice as high as a jump | **Met** | Measured at 1.96 times a normal jump, and releasing W does not shorten a spring launch. |
| 12 | Falling off the bottom respawns from the top | **Met** | The player drops in from above, lands on the starting platform, and placed blocks stay put. |
| 13 | Spikes freeze the player, who then falls off and respawns | **Met** | The freeze lasts 48 frames (0.8 seconds), then the player falls through floors and blocks and respawns as in criterion 12. |
| 14 | Landing in the win zone loads the next level | **Met** | The player has to land in the zone; passing through it in the air does not count. |
| 15 | Beating the last level shows a message | **Met** | A "You Beat the Game!" screen appears. |

### Levels

| # | Criterion | Status | Notes |
|---|---|---|---|
| 16 | Level 1 solvable with 1 plank and 1 spring | **Met** | The full route wins, but some layouts are very tight on timing; see [Known issues](#known-issues). |
| 17 | Level 2 solvable with 2 boxes; spikes behave as in 13 | **Met** | The full route wins using a two-box stack, though one box turned out to be enough. |
| 18 | Level 3 solvable by bouncing across consecutive springs | **Met** | The player bounced across 3 springs in a row to win; the level gives 5 springs, so 2 are spare. |

## Changes from the code as inherited

- **Level 1:** removed the middle platform and moved the upper ledge and win zone, so the level now needs both the plank and the spring.
- **Spikes:** the player now falls through everything after a hit, and blocks can no longer be placed on spikes.
- **Timing:** physics runs at a fixed 60 steps per second, so a slow frame no longer slows the game down.
- **Jump feel:** added coyote time, a jump buffer and variable jump height. `GRAVITY`, `JUMP_SPEED`, `SPRING_SPEED` and `PLAYER_SPEED` are unchanged.
- **Building:** added 22 px grid snapping with faint dots during the build phase, and number keys now only select blocks you still have.
- **Art:** all graphics were replaced with drawn sprites in `art.py`. The spec listed art beyond simple shapes as not needed, so this is an addition.

## Code map

| Path | Purpose |
|---|---|
| `pocket_planks.py` | The whole game: constants, blocks, levels, player physics, input and drawing |
| `art.py` | Every sprite, drawn in code and cached |
| `SPEC.md` | The original author's spec and Phase 3 plan, unchanged |
| `HANDOFF_REPORT.md` | Review of the code as inherited |
| `prompt_log.md` | Every AI prompt used in Phase 2 |
| `UI Screenshots/` | Art style references only; the game does not load them |

Inside `pocket_planks.py`, from top to bottom:

| Section | What to look at |
|---|---|
| Constants | Physics, timing, jump assist values, block sizes and `GRID` |
| Block classes | `Block` and its subclasses; `snap_center()` does the grid snapping |
| `LEVELS` | One dictionary per level: terrain, starting platform, win zone, spikes and blocks in hand |
| `Player` | `update()` is the physics step and returns what happened, such as `"spring"` or `"respawn"`; `press_jump()` and `release_jump()` handle W |
| `Game._load_level()` | Sets up a level |
| `Game._forbidden_rects()` and `_is_placeable()` | Decide where blocks may go |
| `Game.run()` | The fixed-timestep loop |
| `Game._build_event()` and `_play_event()` | Input for each phase |
| `Game._update()` | One game step, including the win check |
| `Game._draw()` and its helpers | Rendering; `_draw_hud()` draws the inventory and hints |

## Taking over

Keep these rules when changing the game:

- Placed blocks float where they are dropped. Never add gravity or support to them.
- Keep collision as axis-aligned `pygame.Rect`, with no rotation or slopes.
- All visuals go through `art.py`. Add any missing sprite there in the same style.
- Treat `GRAVITY`, `JUMP_SPEED`, `SPRING_SPEED`, `PLAYER_SPEED` and block sizes as locked unless you mean to retune every level.

To add a level, append a dictionary to `LEVELS`; the win screen appears after the last entry. Re-check that the level can be beaten afterwards, since the grid limits where blocks can go. For new features, start with the Phase 3 plan in [SPEC.md](SPEC.md). Its block rotation and ramps conflict with the no-rotation rule above, so that item needs a decision first.

### Known working layouts

Positions are each block's top-left corner in pixels. All of these won in the scripted run.

| Level | Blocks | How to play |
|---|---|---|
| 1 | Plank `(418, 506)`, spring `(594, 462)` | Jump to the plank, then to the spring, and hold `D` after the launch; this layout allows a `D` press up to 13 frames late |
| 2 | Boxes `(902, 572)` and `(902, 528)` | Jump the 3 spike rows, climb the stack, then jump to the ledge |
| 3 | Springs `(418, 528)`, `(726, 528)`, `(968, 528)` | Bounce across all 3, and release `D` once over the ledge |


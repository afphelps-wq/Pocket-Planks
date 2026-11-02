# Handoff Report: Pocket Planks

**Author:** Anabella Phelps
**Dates:** October 31 – November 1, 2026

## Summary

I took over Pocket Planks partway through. The spec and a working prototype were there, but Level 1 couldn't be beaten the way the spec describes. Now all 3 levels can be beaten start to finish. Of the 18 acceptance criteria, 17 are met and 1 is partially met. The per-criterion table is in [README.md](README.md#acceptance-criteria-report).

The game works. What's weakest is the level design, not the code. Levels 2 and 3 can both be beaten with fewer blocks than they hand you, so the next person should spend their time on puzzles, not features.

## What I inherited

- `pocket_planks.py`: the whole game in one file. That's physics, three levels, the build and play phases, and placeholder drawing.
- `SPEC.md`: the original spec, plus a Phase 3 plan with about 20 possible additions.
- No tests and no art beyond simple shapes.

The first commit (`3ea1247`) is the code exactly as I received it, so `git diff 3ea1247` shows everything I changed.

## How I assessed it

Before changing anything, I read the code against the spec and worked the physics out from the constants, stepping frame by frame the way `Player.update()` does:

| Measurement | Value |
|---|---|
| Normal jump height | 138.4 px |
| Spring launch height | 271.7 px (1.96× a jump, so criterion 11 holds) |
| Horizontal reach of one jump | ~231 px |

Those numbers made the design problems clear. One example: the Level 2 spikes are 72 px wide and a jump covers about 231 px, so you can clear them without placing anything.

## Decisions I made

- **Placed blocks float.** Blocks stay wherever you drop them, with no gravity and no support. I considered making them snap down onto surfaces and decided against it. This is intentional, so please don't "fix" it.
- **Collision stays axis-aligned.** Everything is `pygame.Rect`. That rules out the Phase 3 item "block rotation / 45° ramps," which would need slope collision, meaning a physics rewrite and not a small feature.
- **Jump feel beats the letter of criterion 9.** I added coyote time and a jump buffer because the spec's top feel goal is a clicky, responsive jump. Strictly, that bends "can only jump while standing," so I marked criterion 9 as partially met instead of claiming it.

## What I changed

1. **Level 1:** removed the middle platform and moved the ledge and win zone, so the level actually needs both the plank and the spring.
2. **Spikes:** after the freeze, the player now falls through everything, and blocks can't be placed on spikes.
3. **Fixed timestep:** physics runs at 60 steps per second, so a slow frame no longer slows the game down.
4. **Jump feel:** 6 frames of coyote time, a 6-frame jump buffer, and a shorter hop when you let go of W early. I didn't touch `GRAVITY`, `JUMP_SPEED`, `SPRING_SPEED` or `PLAYER_SPEED`.
5. **Grid snapping:** blocks snap to a 22 px grid, with faint dots shown during the build phase.
6. **Cleanup:** removed dead code, and number keys only select blocks you still have.
7. **Art:** replaced every placeholder with drawn sprites in `art.py`, using `UI Screenshots/` as the style reference.

## How I tested it

I ran a scripted playtest that drives the real game code without a window. It sends input events, fakes held keys, and beats all 3 levels in one run. All 64 of its checks passed. It confirms the rules work, but it can't judge how the game feels with a real keyboard, so I also played it by hand. The script isn't in the repo, which is the biggest gap I'm leaving.

## How I used AI

I used Claude Code for the implementation. Every prompt is in [prompt_log.md](prompt_log.md), word for word. I made the design calls: floating blocks, no rotation, which jump assists to add, and what to fix first. I wrote the prompts to lock those rules in, then checked each change by hand before moving on.

## Known issues

The full list is in [README.md](README.md#known-issues). The ones that matter most:

- **Level 2 is too easy.** One box wins, even though you're given 2, and the spikes never get in the way.
- **Level 3 has slack.** Only 3 of the 5 springs are needed.
- **Level 1 can come down to one frame.** With some layouts, `D` has to be held on the exact launch frame. Placing the spring further right makes this much more forgiving.
- **There are no automated tests.** Any change to physics or levels has to be re-checked by hand.

## What I'd do next

In this order:

1. **Add the playtest as a real test file.** Then add a small solver that searches grid placements and reports the minimum number of blocks each level needs. Every level change after that depends on it, because right now some routes work by 2 px.
2. **Make planks one-way** (jump up through them, land on top). Right now a plank does everything a box does and is 3× wider. One-way planks give each block its own job.
3. **Add no-build zones.** With floating blocks, the only limits are block count and jump reach. Zones where you can't place blocks force a specific route.
4. **Retune Level 2.** Use one spike bed about 350–400 px wide, too wide to jump, and raise the ledge to about 310 px above the floor so 1 box falls short. Confirm with the solver that 2 is the minimum.
5. **Retune Level 3.** Add spikes on the ceiling to cap bounce height, and tune the level so 3 springs is the real minimum.
6. **Optional: star ratings.** Floating blocks naturally leave slack, so "fewer blocks = more stars" rewards a real skill instead of being decoration.
7. **Update `SPEC.md`** so it matches the game. The box description still says boxes stack and work as steps, which doesn't mean much when blocks float.

## Getting started

```bash
python3 -m pip install pygame-ce
python3 pocket_planks.py
```

Controls, the code map and the rules for taking over are in [README.md](README.md).

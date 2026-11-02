# Prompt Log

Every prompt given to Claude Code during Phase 2 of Pocket Planks, in order and word for word, including typos. All of the work happened in one session. Times are US Eastern. Claude's replies and context added automatically by the tools are left out.

## 1. Project setup

Sat Oct 31, 1:31 PM

```text
read instructions.md and do all the set up for the project
```

## 2. Level 1

Sat Oct 31, 2:05 PM

```text
create level 1 based on the spec
```

## 3. Level 2 bug

Sat Oct 31, 2:17 PM

```text
fix the bug in level 2
```

## 4. Graphics

Sat Oct 31, 2:18 PM, sent while prompt 3 was still running

```text
when your done fixing the bug I want you to use a graphics package to make the game graphics look like the screenshots in the UI screenshots folder
```

## 5. Rules, fixes and jump assists

Sat Oct 31, 2:28 PM, three pasted blocks sent as one message

```text
I'm extending Pocket Planks, a pygame puzzle-platformer (attached: main game file + spec). Rules for every change:
- Placed blocks FLOAT where dropped. This is intentional; never add gravity or support to placed blocks.
- Keep collision axis-aligned pygame.Rect. No rotation, no slopes.
- Visuals go through art.py. If a needed sprite function doesn't exist, add one to art.py in the same style.
- Don't change GRAVITY, JUMP_SPEED, SPRING_SPEED, PLAYER_SPEED, or block sizes unless the prompt says to.
- After each change, tell me exactly what to test by hand.
```

```text
Make these fixes:
1. Add spike rects to _forbidden_rects so blocks can't be placed on or overlapping spikes.
2. Lock the physics to 60 steps/sec with a fixed-timestep accumulator in run(), so a slow frame doesn't slow the game down. The feel at 60 FPS must stay identical.
3. Remove dead code: Player.spring_launched, the unused dt, and the unreachable Space-to-next-level branch in the "win" phase.
4. Number keys 1/2/3 should only select a block kind with count > 0.
```

```text
Add to Player:
- Coyote time: a jump still works for 6 frames after walking off an edge, but not after a spring launch or a spike hit.
- Jump buffer: a W press up to 6 frames before landing jumps on the landing frame.
- Variable jump height: releasing W while rising with vy < -6 sets vy = -6. Spring launches are exempt.
Put the frame counts in named constants at the top of the file.
```

## 6. Commit

Sat Oct 31, 3:33 PM

```text
commit
```

## 7. Grid snapping

Sat Oct 31, 3:37 PM

```text
Snap block placement to a 22 px grid: the block's top-left lands on grid points. Apply this to the ghost preview, new placements, and moved blocks. Add a GRID constant, and draw faint grid dots only during the build phase. Placement validity rules stay the same.
```

## 8. Testing

Sat Oct 31, 3:42 PM

```text
test it using screenshots
```

## 9. Commit and push

Sun Nov 1, 6:24 PM

```text
commit and push everything
```

## 10. Submission checklist

Sun Nov 1, 6:25 PM, pasted checklist followed by a question

```text
The initial commit must be the other student's unmodified work, committed before you change anything (see Phase 2 Step 0). This is the easiest thing here to forget and the most annoying to fix later.
Your subsequent commits, ideally several small ones rather than one large one
Their SPEC.md, kept as you received it. Put any additions you want to propose in a clearly marked section at the bottom rather than editing theirs.
An updated README.md containing your acceptance criteria report, plus run instructions and code map, revised so the next person could take over from you
HANDOFF_REPORT.md, your honest review of what you inherited
prompt_log.md
```

```text
is this all correct
```


```

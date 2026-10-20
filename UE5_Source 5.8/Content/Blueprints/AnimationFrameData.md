# Animation Frame Data Specification

This document defines exact animation timing for combat moves,
based on the original PS2 game's frame data at 60 FPS.

## Combat Combo Timing

| Action | Startup Frames | Active Frames | Recovery Frames | Total | Window After |
|--------|---------------|---------------|-----------------|-------|--------------|
| Light Attack 1 | 6 | 4 | 8 | 18 | 21 frames (0.35s) |
| Light Attack 2 | 5 | 4 | 7 | 16 | 21 frames (0.35s) |
| Light Attack 3 | 6 | 5 | 9 | 20 | 27 frames (0.45s) |
| Heavy Attack (after L1) | 8 | 6 | 10 | 24 | - |
| Heavy Attack (after L2) | 8 | 6 | 10 | 24 | - |
| Heavy Attack (after L3) | 10 | 8 | 12 | 30 | - |
| Quick Step | 4 | 18 (invuln) | 6 | 28 | - |
| Guard Start | 2 | - | 2 | 4 | - |
| Guard Release | 2 | - | 2 | 4 | - |
| Perfect Guard Window | - | 6 (1 frame = 0.016s) | - | 6 | 0.1s total |

## Perfect Guard Timing
- Perfect Guard window: 0.1 seconds (6 frames at 60 FPS)
- Must release Guard within this window before enemy impact
- Successful Perfect Guard: 100% block + enemy stun + counter window

## Quick Step Timing
- Invulnerability frames: 0.3 seconds (18 frames at 60 FPS)
- Double Step window: 0.5 seconds (30 frames at 60 FPS)
- Quick Step cooldown: None (can be chained)

## Animation State Machine

```
Idle
├─ Light Attack 1 → Light Attack 2 (if input within 0.35s)
│   ├─ Light Attack 2 → Light Attack 3 (if input within 0.35s)
│   │   ├─ Light Attack 3 → Heavy Attack (final, if input within 0.60s)
│   │   └─ Light Attack 3 → Idle (if no input)
│   └─ Light Attack 2 → Heavy Attack (final, if input within 0.35s)
│       └─ Heavy Attack → Idle
├─ Light Attack 1 → Heavy Attack (final, if input within 0.35s)
│   └─ Heavy Attack → Idle
├─ Guard (hold) → Guard Release
│   └─ Guard Release → Idle (or Perfect Guard if timed)
├─ Quick Step → Idle (after 0.3s invulnerability)
│   └─ Quick Step → Quick Step (Double Step, if within 0.5s)
├─ Hit Reaction → Idle
└─ Death → Game Over
```

## Animation Blend Times
| Transition | Blend Time |
|------------|------------|
| Idle → Walk/Run | 0.1s |
| Walk/Run → Idle | 0.1s |
| Idle → Attack | 0.05s |
| Attack → Idle | 0.1s |
| Idle → Guard | 0.05s |
| Guard → Idle | 0.1s |
| Idle → Quick Step | 0.05s |
| Quick Step → Idle | 0.1s |
| Idle → Hit Reaction | 0.05s |
| Hit Reaction → Idle | 0.1s |

## Root Motion Settings
- Walk: Root motion enabled, velocity 150 UU/s
- Run: Root motion enabled, velocity 350 UU/s
- Sprint: Root motion enabled, velocity 525 UU/s
- Quick Step: Root motion enabled, velocity 800 UU/s
- Attack animations: Root motion disabled (in-place)

## Notify Events (Animation Notifies)
| Notify | Timing | Effect |
|--------|--------|--------|
| NS_WeaponSwingStart | Frame 2 | Play weapon swing sound |
| NS_WeaponSwingHit | Frame 4-6 | Enable hitbox |
| NS_WeaponSwingEnd | Frame 8 | Disable hitbox |
| NS_QuickStepStart | Frame 1 | Enable invulnerability |
| NS_QuickStepEnd | Frame 18 | Disable invulnerability |
| NS_GuardStart | Frame 1 | Enable guard state |
| NS_GuardEnd | Frame 4 | Disable guard state |
| NS_PerfectGuard | Frame 6 | Trigger perfect guard effects |
| NS_Footstep_L | Frame 3 | Play footstep sound (left) |
| NS_Footstep_R | Frame 6 | Play footstep sound (right) |

## Animation Retargeting
- All animations retargeted to UE5 Mannequin skeleton
- Use Animation Blueprints for state machine transitions
- Use Animation Montages for combat combos
- Animation Notifies for sound/VFX events
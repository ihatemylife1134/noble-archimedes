# Animation Blueprint State Machine Specification

This document defines the Animation Blueprint state machine for Hector (the player character),
based on the original Castlevania: Curse of Darkness animation timing at 60 FPS.

## 1. Animation States

| State Name | Type | Loop | Entry Condition | Exit Conditions |
|------------|------|------|-----------------|-----------------|
| Idle | Full Body | Yes | Default state | Move input, Attack input, Guard input, QuickStep input, Hit |
| Walk | Full Body | Yes | Move input (slow) | Stop move, Run input, Attack, Guard, QuickStep, Hit |
| Run | Full Body | Yes | Move input (fast) | Stop move, Walk input, Attack, Guard, QuickStep, Hit |
| Jump Start | Full Body | No | Jump input | Jump Land, Hit |
| Jump Loop | Full Body | Yes | In air | Jump Land, Hit |
| Jump Land | Full Body | No | Land | Idle |
| Light Attack 1 | Full Body | No | Light attack input | Light Attack 2, Heavy Attack, Idle |
| Light Attack 2 | Full Body | No | Light attack (within 0.35s) | Light Attack 3, Heavy Attack, Idle |
| Light Attack 3 | Full Body | No | Light attack (within 0.35s) | Heavy Attack, Idle |
| Heavy Attack | Full Body | No | Heavy attack input | Idle |
| Guard Start | Full Body | No | Guard press | Guard Loop |
| Guard Loop | Full Body | Yes | Guard held | Guard Release |
| Guard Release | Full Body | No | Guard release | Idle |
| Perfect Guard | Full Body | No | Guard release (within 0.1s) | Idle |
| Quick Step | Full Body | No | QuickStep input | Idle |
| Hit Reaction | Full Body | No | Take damage | Idle |
| Death | Full Body | No | Health <= 0 | None |

## 2. State Transitions

### Idle → Move
- **Condition**: Move input magnitude > 0.1
- **Blend Time**: 0.1s
- **Animation**: Walk (if speed < 350 UU/s) or Run (if speed >= 350 UU/s)

### Move → Idle
- **Condition**: Move input magnitude <= 0.1
- **Blend Time**: 0.1s
- **Animation**: Idle

### Idle → Light Attack 1
- **Condition**: Light attack input pressed
- **Blend Time**: 0.05s
- **Animation**: Light Attack 1

### Light Attack 1 → Light Attack 2
- **Condition**: Light attack input pressed within 0.35s of Light Attack 1 start
- **Blend Time**: 0.05s
- **Animation**: Light Attack 2

### Light Attack 2 → Light Attack 3
- **Condition**: Light attack input pressed within 0.35s of Light Attack 2 start
- **Blend Time**: 0.05s
- **Animation**: Light Attack 3

### Light Attack 3 → Heavy Attack
- **Condition**: Heavy attack input pressed within 0.60s of Light Attack 3 start
- **Blend Time**: 0.05s
- **Animation**: Heavy Attack

### Any Attack → Heavy Attack
- **Condition**: Heavy attack input pressed during any light attack combo window
- **Blend Time**: 0.05s
- **Animation**: Heavy Attack

### Any Attack → Idle
- **Condition**: Combo window expired (no input)
- **Blend Time**: 0.1s
- **Animation**: Idle

### Idle → Guard Start
- **Condition**: Guard input pressed
- **Blend Time**: 0.05s
- **Animation**: Guard Start

### Guard Start → Guard Loop
- **Condition**: Guard start animation complete
- **Blend Time**: 0.0s
- **Animation**: Guard Loop

### Guard Loop → Guard Release
- **Condition**: Guard input released
- **Blend Time**: 0.05s
- **Animation**: Guard Release

### Guard Release → Perfect Guard
- **Condition**: Guard released within 0.1s before enemy impact
- **Blend Time**: 0.0s
- **Animation**: Perfect Guard

### Guard Release → Idle
- **Condition**: Guard released outside perfect guard window
- **Blend Time**: 0.1s
- **Animation**: Idle

### Idle → Quick Step
- **Condition**: QuickStep input pressed
- **Blend Time**: 0.05s
- **Animation**: Quick Step

### Quick Step → Idal
- **Condition**: Quick step animation complete
- **Blend Time**: 0.1s
- **Animation**: Idle

### Any State → Hit Reaction
- **Condition**: Take damage (not invulnerable, not perfect guarding)
- **Blend Time**: 0.05s
- **Animation**: Hit Reaction

### Hit Reaction → Idle
- **Condition**: Hit reaction animation complete
- **Blend Time**: 0.1s
- **Animation**: Idle

### Any State → Death
- **Condition**: Health <= 0 (and no Death Doll)
- **Blend Time**: 0.0s
- **Animation**: Death

## 3. Animation Montages

| Montage Name | Sections | Loop | Root Motion | Notes |
|--------------|----------|------|-------------|-------|
| AM_Combo_Sword | Light1, Light2, Light3, Heavy1, Heavy2, Heavy3 | No | Yes | Sword combo |
| AM_Combo_Axe | Light1, Light2, Light3, Heavy1, Heavy2, Heavy3 | No | Yes | Axe combo |
| AM_Combo_Spear | Light1, Light2, Light3, Heavy1, Heavy2, Heavy3 | No | Yes | Spear combo |
| AM_Combo_Knuckles | Light1, Light2, Light3, Heavy1, Heavy2, Heavy3 | No | Yes | Knuckles combo |
| AM_Combo_Special | Light1, Light2, Heavy1, Heavy2 | No | Yes | Special weapon combo |
| AM_Guard | Start, Loop, Release | No | Yes | Guard animation |
| AM_QuickStep | Start, Loop, End | No | Yes | Dodge roll |
| AM_HitReaction | Light, Medium, Heavy | No | Yes | Damage reactions |
| AM_Death | Standard | No | Yes | Death animation |

## 4. Animation Notifies

| Notify Name | Frame/Timing | Effect |
|-------------|--------------|--------|
| NS_WeaponSwingStart | Attack frame 2 | Play weapon swing sound |
| NS_WeaponSwingHit | Attack frames 4-6 | Enable hitbox collision |
| NS_WeaponSwingEnd | Attack frame 8 | Disable hitbox collision |
| NS_QuickStepStart | Frame 1 | Enable invulnerability |
| NS_QuickStepEnd | Frame 18 | Disable invulnerability |
| NS_GuardStart | Frame 1 | Enable guard state |
| NS_GuardEnd | Frame 4 | Disable guard state |
| NS_PerfectGuard | Frame 6 | Trigger perfect guard VFX/SFX |
| NS_Footstep_L | Walk frame 3 | Play left footstep sound |
| NS_Footstep_R | Walk frame 6 | Play right footstep sound |
| NS_ItemPickup | Frame 1 | Play item pickup sound |
| NS_ItemUse | Frame 1 | Play item use sound |

## 5. Blend Spaces

| Blend Space Name | Input Parameters | Animations |
|------------------|------------------|------------|
| BS_Locomotion | Speed (0-525), Direction (-180 to 180) | Idle, Walk, Run, Sprint |
| BS_CombatIdle | HealthPercent (0-100) | Idle, HurtIdle |
| BS_AimOffset | Pitch (-90 to 90), Yaw (-180 to 180) | Aim animations |

## 6. Performance Requirements

| Animation Type | Max Bones | Max Curves | Max Notifies |
|----------------|-----------|------------|--------------|
| Character | 65 | 10 | 20 |
| Weapon | 5 | 5 | 5 |
| Companion | 50 | 5 | 10 |
| Enemy | 40 | 5 | 10 |

## 7. Implementation Steps in UE5

1. Create Animation Blueprint based on Hector skeleton
2. Create Idle/Walk/Run blend space
3. Create Attack montage for each weapon type
4. Create Guard montage
5. Create Quick Step montage
6. Create Hit Reaction montages (light, medium, heavy)
7. Create Death montage
8. Set up state machine transitions per spec above
9. Add Animation Notifies for sound/VFX
10. Test combo timing windows (0.35s/0.45s/0.60s)
11. Test Perfect Guard window (0.1s)
12. Test Quick Step invulnerability (0.3s)

---

**All animation timing is based on the original Castlevania: Curse of Darkness at 60 FPS.**
**Private use only — no copyrighted assets extracted.**
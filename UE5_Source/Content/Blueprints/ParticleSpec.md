# Particle System Specification — Niagara

This document defines all Niagara particle systems needed for the game.
Create these in UE5 using Niagara Editor.

## 1. Combat VFX

### P_WeaponTrail_Sword
- **Type**: Ribbon
- **Color**: Silver gradient (white → gray → transparent)
- **Lifetime**: 0.3s
- **Width**: 10 → 0 (taper)
- **Spawn**: On weapon swing animation notify
- **Socket**: Weapon tip socket

### P_WeaponTrail_Axe
- **Type**: Ribbon
- **Color**: Bronze gradient (brown → dark brown → transparent)
- **Lifetime**: 0.4s
- **Width**: 15 → 0
- **Spawn**: On weapon swing

### P_WeaponTrail_Spear
- **Type**: Ribbon
- **Color**: Iron gradient (dark gray → gray → transparent)
- **Lifetime**: 0.2s
- **Width**: 5 → 0
- **Spawn**: On weapon thrust

### P_WeaponTrail_Knuckles
- **Type**: Ribbon
- **Color**: Steel gradient (light gray → white → transparent)
- **Lifetime**: 0.15s
- **Width**: 8 → 0
- **Spawn**: On punch animation

### P_WeaponTrail_Special
- **Type**: Ribbon
- **Color**: Gold gradient (yellow → orange → transparent)
- **Lifetime**: 0.5s
- **Width**: 12 → 0
- **Spawn**: On projectile attack

## 2. Hit VFX

### P_HitSpark_Fire
- **Type**: Sprite burst
- **Color**: Orange → red → transparent
- **Count**: 5-10 particles
- **Lifetime**: 0.2-0.4s
- **Size**: 5-15 UU

### P_HitSpark_Ice
- **Type**: Sprite burst
- **Color**: Light blue → white → transparent
- **Count**: 5-10 particles
- **Lifetime**: 0.2-0.4s

### P_HitSpark_Light
- **Type**: Sprite burst
- **Color**: Yellow → white → transparent
- **Count**: 8-12 particles
- **Lifetime**: 0.1-0.3s

### P_HitSpark_Dark
- **Type**: Sprite burst
- **Color**: Purple → black → transparent
- **Count**: 5-10 particles
- **Lifetime**: 0.3-0.5s

### P_HitBlood
- **Type**: Sprite burst
- **Color**: Dark red → brown → transparent
- **Count**: 3-6 particles
- **Lifetime**: 0.5-1.0s
- **Size**: 3-8 UU

## 3. Defensive VFX

### P_QuickStepTrail
- **Type**: Ribbon + Sprite
- **Color**: White → transparent
- **Lifetime**: 0.3s
- **Width**: 20 → 5
- **Spawn**: Player dodge location

### P_PerfectGuardFlash
- **Type**: Sphere + Ring
- **Color**: Gold → white → transparent
- **Radius**: 50 → 100 UU
- **Lifetime**: 0.2s
- **Spawn**: Player guard release

### P_GuardBlockFlash
- **Type**: Ring
- **Color**: Silver → transparent
- **Radius**: 30 → 60 UU
- **Lifetime**: 0.15s
- **Spawn**: Player guard block

## 4. Innocent Devil VFX

### P_Innocent DevilSummon_Fairy
- **Type**: Sprite + Light
- **Color**: Light blue → white → transparent
- **Particles**: 20 sparkles
- **Lifetime**: 1.0s

### P_Innocent DevilEvolve
- **Type**: Sphere burst + Light
- **Color**: Gold → white → transparent
- **Radius**: 100 → 200 UU
- **Lifetime**: 1.5s

### P_Innocent DevilAttack_Fire
- **Type**: Sprite trail
- **Color**: Orange → red → transparent
- **Lifetime**: 0.4s

## 5. Item VFX

### P_ItemPickup
- **Type**: Sprite + Light
- **Color**: Yellow → white → transparent
- **Particles**: 5 sparkles
- **Lifetime**: 0.5s

### P_CandleBreak
- **Type**: Sprite burst
- **Color**: Orange → yellow → transparent
- **Count**: 15-20 particles
- **Lifetime**: 0.5-1.0s

### P_SaveRoomHeal
- **Type**: Sphere glow + Sprite
- **Color**: Green → light green → transparent
- **Radius**: 200 UU
- **Lifetime**: 2.0s

## 6. Ambient VFX

### P_DustMotes_Castle
- **Type**: Sprite
- **Color**: Gray → transparent
- **Count**: 30 particles
- **Area**: Castle rooms
- **Lifetime**: 2-5s (looping)

### P_Leaves_Forest
- **Type**: Sprite
- **Color**: Brown → transparent
- **Count**: 15 particles
- **Area**: Forest rooms
- **Lifetime**: 3-6s (looping)

### P_Steam_MachineTower
- **Type**: Sprite + Distortion
- **Color**: White → transparent
- **Count**: 10 particles
- **Area**: Machine tower rooms
- **Lifetime**: 2-4s (looping)

## Niagara Parameters (exposed to Blueprint)
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| VFXScale | Float | 1.0 | Overall particle scale |
| ColorOverride | LinearColor | White | Override particle color |
| LifetimeMultiplier | Float | 1.0 | Scale particle lifetime |
| SpawnRate | Float | 1.0 | Particles per second |

## Performance
- Max 500 particles per system
- Use LOD distances for distant effects
- Disable when camera > 1000 UU away
- GPU particles for simple sprites, CPU for complex interactions
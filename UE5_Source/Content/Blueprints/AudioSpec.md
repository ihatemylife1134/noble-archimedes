# Audio Specification — MetaSounds & Sound Cues

This document defines all audio assets needed for the game.
Create Sound Cues in UE5 and import original audio files.

## 1. Combat SFX

| Cue Name | Type | Description | Variations |
|----------|------|-------------|------------|
| SC_Combat_Swing_Sword | Sound Cue | Sword swing whoosh | 3 variations |
| SC_Combat_Swing_Axe | Sound Cue | Axe swing whoosh | 3 variations |
| SC_Combat_Swing_Spear | Sound Cue | Spear thrust whoosh | 3 variations |
| SC_Combat_Swing_Knuckles | Sound Cue | Punch whoosh | 3 variations |
| SC_Combat_Swing_Special | Sound Cue | Projectile whoosh | 3 variations |
| SC_Combat_Hit_Sword | Sound Cue | Sword hit impact | 4 variations |
| SC_Combat_Hit_Axe | Sound Cue | Axe hit impact | 4 variations |
| SC_Combat_Hit_Spear | Sound Cue | Spear hit impact | 4 variations |
| SC_Combat_Hit_Knuckles | Sound Cue | Punch impact | 4 variations |
| SC_Combat_Hit_Special | Sound Cue | Projectile impact | 4 variations |
| SC_Combat_PlayerHit | Sound Cue | Player takes damage | 3 variations |
| SC_Combat_EnemyHit | Sound Cue | Enemy takes damage | 4 variations |
| SC_Combat_QuickStep | Sound Cue | Dodge roll | 2 variations |
| SC_Combat_GuardBlock | Sound Cue | Guard block | 3 variations |
| SC_Combat_PerfectGuard | Sound Cue | Perfect parry | 2 variations |
| SC_Combat_Death | Sound Cue | Character death | 1 variation |

## 2. Companion SFX

| Cue Name | Type | Description | Variations |
|----------|------|-------------|------------|
| SC_Companion_Summon_Fairy | Sound Cue | Fairy summon | 2 variations |
| SC_Companion_Summon_Griffin | Sound Cue | Griffin summon | 2 variations |
| SC_Companion_Summon_Salamander | Sound Cue | Salamander summon | 2 variations |
| SC_Companion_Summon_Ogre | Sound Cue | Ogre summon | 2 variations |
| SC_Companion_Summon_Skeleton | Sound Cue | Skeleton summon | 2 variations |
| SC_Companion_Summon_Witch | Sound Cue | Witch summon | 2 variations |
| SC_Companion_Summon_Pumpkin | Sound Cue | Pumpkin summon | 2 variations |
| SC_Companion_Attack | Sound Cue | Companion attack | 3 per type |
| SC_Companion_Evolve | Sound Cue | Companion evolve | 2 variations |
| SC_Companion_Hit | Sound Cue | Companion damage | 3 per type |

## 3. Item SFX

| Cue Name | Type | Description |
|----------|------|-------------|
| SC_Item_Pickup | Sound Cue | Generic item pickup |
| SC_Item_Potion | Sound Cue | Drink potion |
| SC_Item_HighPotion | Sound Cue | Drink high potion |
| SC_Item_Serum | Sound Cue | Use serum |
| SC_Item_Uncurse | Sound Cue | Remove curse |
| SC_Item_Steal | Sound Cue | Successful steal |
| SC_Item_StealFail | Sound Cue | Failed steal attempt |
| SC_Item_Forge | Sound Cue | Weapon forge at anvil |

## 4. Environment SFX

| Cue Name | Type | Description | 3D |
|----------|------|-------------|----|
| SC_Env_CandleBreak | Sound Cue | Candle breaks | Yes |
| SC_Env_DoorOpen | Sound Cue | Door opens | Yes |
| SC_Env_DoorClose | Sound Cue | Door closes | Yes |
| SC_Env_ChestOpen | Sound Cue | Chest opens | Yes |
| SC_Env_SaveRoom | Sound Cue | Save room heal | Yes |
| SC_Env_Footstep_Stone | Sound Cue | Stone footsteps | Yes |
| SC_Env_Footstep_Wood | Sound Cue | Wood footsteps | Yes |
| SC_Env_Footstep_Metal | Sound Cue | Metal footsteps | Yes |
| SC_Env_Footstep_Dirt | Sound Cue | Dirt footsteps | Yes |

## 5. UI SFX

| Cue Name | Type | Description |
|----------|------|-------------|
| SC_UI_Click | Sound Cue | Button click |
| SC_UI_Hover | Sound Cue | Menu hover |
| SC_UI_MenuOpen | Sound Cue | Menu opens |
| SC_UI_MenuClose | Sound Cue | Menu closes |
| SC_UI_Save | Sound Cue | Game saved |
| SC_UI_Load | Sound Cue | Game loaded |
| SC_UI_Error | Sound Cue | Error/invalid action |

## 6. Ambient Beds (per chapter)

| Cue Name | Type | Chapter | Loop | Notes |
|----------|------|---------|------|-------|
| SC_Amb_Castle | Sound Cue | Chap 1 | Yes | Stone creaking, distant wind |
| SC_Amb_Mountains | Sound Cue | Chap 2 | Yes | Wind, distant thunder |
| SC_Amb_Temple | Sound Cue | Chap 3 | Yes | Distant chimes, echo |
| SC_Amb_Aqueduct | Sound Cue | Chap 4 | Yes | Flowing water, drips |
| SC_Amb_Forest | Sound Cue | Chap 5 | Yes | Birds, rustling leaves |
| SC_Amb_Town | Sound Cue | Chap 6 | Yes | Distant chatter, market |
| SC_Amb_Tower | Sound Cue | Chap 7 | Yes | Mechanical hum, steam |
| SC_Amb_Ruins | Sound Cue | Chap 8 | Yes | Wind through ruins |
| SC_Amb_Corridor | Sound Cue | Chap 9 | Yes | Low hum, atmospheric |
| SC_Amb_CastleFinal | Sound Cue | Chap 10 | Yes | Orchestral tension, organ |

## 7. Music (Original Composition)

| Cue Name | Type | Chapter | Loop | Notes |
|----------|------|---------|------|-------|
| SC_Music_Chap01 | Sound Cue | Chap 1 | Yes | Gothic exploration |
| SC_Music_Chap02 | Sound Cue | Chap 2 | Yes | Mountain exploration |
| SC_Music_Chap03 | Sound Cue | Chap 3 | Yes | Temple exploration |
| SC_Music_Chap04 | Sound Cue | Chap 4 | Yes | Aqueduct exploration |
| SC_Music_Chap05 | Sound Cue | Chap 5 | Yes | Forest exploration |
| SC_Music_Chap06 | Sound Cue | Chap 6 | Yes | Town theme |
| SC_Music_Chap07 | Sound Cue | Chap 7 | Yes | Mechanical theme |
| SC_Music_Chap08 | Sound Cue | Chap 8 | Yes | Ruins mystery |
| SC_Music_Chap09 | Sound Cue | Chap 9 | Yes | Surreal ambient |
| SC_Music_Chap10 | Sound Cue | Chap 10 | Yes | Final castle grand |
| SC_Music_Combat | Sound Cue | All | Yes | Battle music |
| SC_Music_Boss | Sound Cue | Boss | Yes | Boss battle |
| SC_Music_Victory | Sound Cue | All | No | Victory fanfare |
| SC_Music_GameOver | Sound Cue | All | No | Game over theme |

## Audio Settings (exposed to player)
| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Master Volume | 1.0 | 0.0-1.0 | Overall volume |
| SFX Volume | 1.0 | 0.0-1.0 | Sound effects |
| Music Volume | 0.7 | 0.0-1.0 | Background music |
| 3D Audio | On | On/Off | Spatial audio |
| Occlusion | On | On/Off | Sound through walls |

## Audio Implementation
- Use MetaSounds for procedural audio (footsteps, weapon swings with randomization)
- Use Sound Cues for one-shot SFX (attacks, UI, items)
- Use Sound Classes for volume grouping (Master, SFX, Music, Ambient, UI)
- Use Attenuation for 3D sound falloff
- Use Reverb Volumes per room type (castle, temple, forest, town)
- Use Occlusion for castle walls (muffled sound)
- All audio must be original composition/recording — no extracted game audio
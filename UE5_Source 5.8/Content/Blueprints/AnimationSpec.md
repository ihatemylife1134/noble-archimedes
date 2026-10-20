# Animation Specification — UE5 Fan Recreation

This document defines all animations needed for the game. Create these in UE5 using
the Mannequin skeleton or import custom FBX animations.

## 1. Player Character — "The Forgemaster"

### Locomotion
| Animation | Type | Speed | Loop | Notes |
|-----------|------|-------|------|-------|
| Idle | Full Body | - | Yes | Breathing, slight weapon sway |
| Walk | Full Body | 150 UU/s | Yes | Standard movement |
| Run | Full Body | 350 UU/s | Yes | Combat movement |
| Sprint | Full Body | 525 UU/s | Yes | Shift held |
| Jump Start | Full Body | - | No | Initiate jump |
| Jump Loop | Full Body | - | Yes | In air |
| Jump Land | Full Body | - | No | Landing impact |
| Fall Start | Full Body | - | No | Begin falling |
| Fall Loop | Full Body | - | Yes | Mid-air fall |

### Combat — Sword (default weapon)
| Animation | Type | Speed | Loop | Notes |
|-----------|------|-------|------|-------|
| Sword_Idle | Full Body | - | Yes | Ready stance |
| Sword_Light1 | Full Body | - | No | First combo hit |
| Sword_Light2 | Full Body | - | No | Second combo hit |
| Sword_Light3 | Full Body | - | No | Third combo hit |
| Sword_Heavy1 | Full Body | - | No | Final attack after stage 1 |
| Sword_Heavy2 | Full Body | - | No | Final attack after stage 2 |
| Sword_Heavy3 | Full Body | - | No | Final attack after stage 3 |
| Sword_GuardStart | Full Body | - | No | Raise guard |
| Sword_GuardLoop | Full Body | - | Yes | Holding guard |
| Sword_GuardEnd | Full Body | - | No | Lower guard |
| Sword_GuardHit | Full Body | - | No | Hit while guarding |
| Sword_PerfectGuard | Full Body | - | No | Perfect parry flash |
| Sword_QuickStep | Full Body | - | No | Dodge roll forward |
| Sword_QuickStepLeft | Full Body | - | No | Dodge roll left |
| Sword_QuickStepRight | Full Body | - | No | Dodge roll right |
| Sword_QuickStepBack | Full Body | - | No | Dodge roll backward |
| Sword_HitReaction | Full Body | - | No | React to taking damage |
| Sword_Death | Full Body | - | No | Death animation |

### Combat — Axe
| Animation | Notes |
|-----------|-------|
| Axe_Idle | Heavier, slower stance |
| Axe_Light1/2/3 | Slower, more powerful swings |
| Axe_Heavy1/2/3 | Overhead smash variations |
| Axe_QuickStep | Shorter roll, more weight |

### Combat — Spear
| Animation | Notes |
|-----------|-------|
| Spear_Idle | Long weapon held ready |
| Spear_Light1/2/3 | Thrusting attacks |
| Spear_Heavy1/2/3 | Sweeping attacks |
| Spear_QuickStep | Lunge forward |

### Combat — Knuckles
| Animation | Notes |
|-----------|-------|
| Knuckles_Idle | Fast, boxer stance |
| Knuckles_Light1/2/3 | Rapid punches |
| Knuckles_Heavy1/2/3 | Uppercut, spinning strike |
| Knuckles_QuickStep | Quick sidestep |

### Combat — Special (projectile weapons)
| Animation | Notes |
|-----------|-------|
| Special_Idle | Weapon-specific stance |
| Special_Light1/2/3 | Projectile attacks |
| Special_Heavy1/2/3 | Charged projectile |
| Special_QuickStep | Quick backstep |

### Generic (all weapons)
| Animation | Notes |
|-----------|-------|
| Interact | Use items, open doors |
| SummonInnocent Devil | Call innocent devil |
| SwitchWeapon | Change equipped weapon |
| Victory | Win pose |
| Defeat | Lose pose |

## 2. Enemies

### Generic Enemy
| Animation | Notes |
|-----------|-------|
| Idle | Breathing, idle movement |
| Walk | Patrol movement |
| Run | Chase player |
| Attack1 | Primary attack |
| Attack2 | Secondary attack |
| Attack3 | Heavy/special attack |
| HitReaction | React to damage |
| Death | Die animation |
| Spawn | Appear in room |

### Boss Enemy
| Animation | Notes |
|-----------|-------|
| Idle | More elaborate idle |
| Attack1/2/3 | Unique boss attacks |
| PhaseTransition | Change boss phase |
| HitReaction | Boss flinch |
| Death | Boss defeat |
| Intro | Boss entrance cutscene |

## 3. Innocent Devils (Innocent Devils)

### Generic Innocent Devil
| Animation | Notes |
|-----------|-------|
| Idle | Floating/standing idle |
| Walk | Follow player |
| Attack | Attack enemy |
| Guard | Block attacks |
| HitReaction | React to damage |
| Death | Innocent Devil defeated |
| Summon | Appear from summon circle |
| Evolve | Transform to next form |
| Dismiss | Return to summon |

### Innocent Devil-Specific
| Innocent Devil | Unique Animation |
|-----------|-----------------|
| Fairy | Fly, hover, sparkle trail |
| Griffin | Wing flap, dive attack |
| Salamander | Fire breath, tail swipe |
| Ogre | Ground pound, club swing |
| Skeleton | Bone rattle, skull throw |
| Witch | Magic cast, cauldron |
| Pumpkin | Glow, lantern swing |

## 4. Weapon Combining (Forge)
| Animation | Notes |
|-----------|-------|
| ForgeStart | Anvil hammer start |
| ForgeLoop | Anvil hammer loop |
| ForgeEnd | Weapon reveal |
| ForgeFail | Spark failure |

## 5. Environment
| Animation | Notes |
|-----------|-------|
| CandleBreak | Flame extinguish, wax fall |
| DoorOpen | Door swing open |
| DoorClose | Door swing shut |
| ChestOpen | Chest lid open |
| ChestClose | Chest lid close |
| SaveRoomHeal | Floor tile glow |
| GreenDoorOpen | Portal activate |

## Animation Retargeting
- All animations should be retargeted to UE5 Mannequin skeleton
- Use Animation Blueprints for state machine
- Use Animation Montages for combat combos
- Use Animation Notifies for sound/VFX events (footsteps, weapon swings, hits)

## Performance
- LOD 0: Full quality (player, bosses)
- LOD 1: Medium quality (enemies)
- LOD 2: Low quality (distant innocent devils)
- Max 60 animations per character (keep lean)
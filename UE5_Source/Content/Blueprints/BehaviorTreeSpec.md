# Behavior Tree Specification — Enemy AI

This document defines enemy AI behavior trees based on the original Castlevania: Curse of Darkness enemy AI.

## 1. Behavior Tree Structure

```
BT_EnemyBase
├─ Selector: Root
│  ├─ Sequence: Combat
│  │  ├─ Decorator: CanSeePlayer
│  │  ├─ Decorator: IsInAttackRange
│  │  ├─ Task: FacePlayer
│  │  └─ Task: PlayAttackAnimation
│  ├─ Sequence: Chase
│  │  ├─ Decorator: CanSeePlayer
│  │  ├─ Decorator: IsNotInAttackRange
│  │  ├─ Task: MoveToPlayer
│  │  └─ Task: PlayChaseAnimation
│  ├─ Sequence: Patrol
│  │  ├─ Decorator: CannotSeePlayer
│  │  ├─ Task: MoveToPatrolPoint
│  │  └─ Task: WaitAtPatrolPoint
│  └─ Sequence: Idle
│     ├─ Decorator: CannotSeePlayer
│     ├─ Decorator: AtPatrolPoint
│     └─ Task: PlayIdleAnimation
```

## 2. Enemy Types and AI Parameters

| Enemy Type | Detection Range | Attack Range | Move Speed | Patrol Points | Aggression |
|------------|----------------|--------------|------------|---------------|------------|
| Skeleton | 600 UU | 150 UU | 300 UU/s | 4 | Medium |
| Zombie | 500 UU | 120 UU | 200 UU/s | 3 | Low |
| Ghoul | 550 UU | 140 UU | 250 UU/s | 3 | Medium |
| Harpy | 800 UU | 200 UU | 400 UU/s | 5 | High |
| Bat | 400 UU | 100 UU | 350 UU/s | 4 | Low |
| Mountain Beast | 700 UU | 180 UU | 350 UU/s | 4 | High |
| Temple Guardian | 650 UU | 160 UU | 300 UU/s | 3 | Medium |
| Cultist | 600 UU | 140 UU | 250 UU/s | 3 | Medium |
| Dark Priest | 700 UU | 150 UU | 250 UU/s | 3 | Medium |
| Water Creature | 600 UU | 170 UU | 300 UU/s | 3 | Medium |
| Aqueduct Guard | 550 UU | 150 UU | 280 UU/s | 3 | Medium |
| Forest Stalker | 750 UU | 130 UU | 350 UU/s | 4 | High |
| Nature Spirit | 800 UU | 140 UU | 350 UU/s | 4 | Medium |
| Town Guard | 500 UU | 150 UU | 280 UU/s | 4 | Medium |
| Citizen | 300 UU | 100 UU | 200 UU/s | 5 | None |
| Clockwork Soldier | 600 UU | 160 UU | 300 UU/s | 4 | Medium |
| Mechanical Trap | 400 UU | 100 UU | 100 UU/s | 1 | None |
| Ruin Guardian | 650 UU | 170 UU | 300 UU/s | 3 | Medium |
| Ancient Construct | 700 UU | 180 UU | 250 UU/s | 3 | Medium |
| Corridor Phantom | 900 UU | 140 UU | 350 UU/s | 5 | High |
| Surreal Entity | 1000 UU | 160 UU | 350 UU/s | 5 | High |
| Castle Elite | 700 UU | 180 UU | 350 UU/s | 4 | High |
| Final Boss | 1000 UU | 250 UU | 400 UU/s | 6 | Very High |

## 3. Steal System

| Enemy Type | Can Steal | Steal Item | Steal Window (frames) | Steal Chance |
|------------|-----------|------------|----------------------|--------------|
| Skeleton | Yes | Bone Shard | 10 | 30% |
| Zombie | No | - | - | - |
| Ghoul | Yes | Bone Shard | 10 | 30% |
| Harpy | Yes | Harpy Feather | 8 | 30% |
| Bat | Yes | Small Coin | 12 | 30% |
| Mountain Beast | Yes | Mountain Herb | 12 | 30% |
| Sentinel Knight | No | - | - | - |
| Temple Guardian | Yes | Temple Key | 10 | 30% |
| Cultist | Yes | Cultist Robe | 10 | 30% |
| Dark Priest | Yes | Dark Crystal | 12 | 30% |
| High Inquisitor | No | - | - | - |
| Water Creature | Yes | Aqueduct Gem | 10 | 30% |
| Aqueduct Guard | Yes | Iron Shard | 10 | 30% |
| Aqueduct Sentinel | No | - | - | - |
| Forest Stalker | Yes | Forest Mushroom | 12 | 30% |
| Nature Spirit | Yes | Nature Essence | 12 | 30% |
| Forest Warden | No | - | - | - |
| Town Guard | Yes | Town Key | 10 | 30% |
| Citizen | No | - | - | - |
| Town Captain | No | - | - | - |
| Clockwork Soldier | Yes | Gear Component | 12 | 30% |
| Mechanical Trap | No | - | - | - |
| Tower Automaton | No | - | - | - |
| Ruin Guardian | Yes | Ancient Coin | 10 | 30% |
| Ancient Construct | Yes | Ancient Relic | 12 | 30% |
| Ruin Sentinel | No | - | - | - |
| Corridor Phantom | Yes | Ethereal Dust | 12 | 30% |
| Surreal Entity | Yes | Surreal Fragment | 12 | 30% |
| Mirror Entity | No | - | - | - |
| Castle Elite | Yes | Castle Key | 10 | 30% |
| Final Boss | No | - | - | - |

## 3. Blackboard Keys

| Key Name | Type | Description |
|----------|------|-------------|
| Player | Object | Reference to Hector |
| CanSeePlayer | Boolean | Can enemy see player? |
| IsInAttackRange | Boolean | Is player in attack range? |
| IsNotInAttackRange | Boolean | Is player NOT in attack range? |
| PatrolPoint | Vector | Current patrol destination |
| PatrolIndex | Integer | Current patrol point index |
| AttackTimer | Float | Time since last attack |
| AttackCooldown | Float | Time between attacks |
| StealWindow | Float | Time remaining for steal opportunity |
| IsStealable | Boolean | Can player steal from this enemy? |
| DetectRadius | Float | Detection range for this enemy type |
| AttackRadius | Float | Attack range for this enemy type |

## 4. Services

| Service Name | Tick Interval | Description |
|--------------|---------------|-------------|
| UpdateCanSeePlayer | 0.1s | Check line of sight to player |
| UpdateIsInAttackRange | 0.1s | Check distance to player |
| UpdateStealWindow | 0.1s | Update steal opportunity timer |
| UpdatePatrolPoint | 1.0s | Cycle through patrol points |

## 5. Tasks

| Task Name | Description |
|-----------|-------------|
| FacePlayer | Rotate enemy to face player |
| MoveToPlayer | Move toward player using navigation |
| MoveToPatrolPoint | Move to current patrol point |
| WaitAtPatrolPoint | Wait at patrol point for random duration |
| PlayAttackAnimation | Play enemy attack montage |
| PlayChaseAnimation | Play chase movement animation |
| PlayIdleAnimation | Play idle animation |
| CheckStealWindow | Check if player can steal |
| ApplyDamage | Apply damage to player on hit |

## 6. Decorators

| Decorator Name | Description |
|----------------|-------------|
| CanSeePlayer | Line of sight check to player |
| IsInAttackRange | Distance check <= attack range |
| IsNotInAttackRange | Distance check > attack range |
| CanSteal | Check if steal window is open |
| IsOnPatrol | Check if enemy is at patrol point |

## 7. Implementation Steps in UE5

1. Create Behavior Tree for each enemy type
2. Create Blackboard with all keys listed above
3. Create Services for perception and range checks
4. Create Tasks for movement and attacks
5. Create Decorators for conditions
6. Set up detection ranges per enemy type
7. Test combat AI (chase, attack, patrol)
8. Test steal system (steal window timing)
9. Test patrol behavior
10. Test boss AI (multi-phase)

## 8. Boss AI Phases

| Boss | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| Sentinel Knight | Melee attacks | + Charge attack | - |
| Sky Drake | Fly + Fire breath | + Dive attack | - |
| High Inquisitor | Magic attacks | + Summon minions | - |
| Aqueduct Sentinel | Water attacks | + Ice attacks | - |
| Forest Warden | Nature attacks | + Root attacks | - |
| Town Captain | Guard + Sword | + Shield bash | - |
| Tower Automaton | Melee + Steam | + Laser attack | - |
| Ruin Sentinel | Stone attacks | + Earthquake | - |
| Mirror Entity | Copy player | + Mirror damage | - |
| Final Boss | All previous | + Final form | - |

---

**All AI behavior is based on the original Castlevania: Curse of Darkness enemy patterns.**
**Private use only — no copyrighted assets extracted.**
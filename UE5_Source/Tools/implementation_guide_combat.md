# Combat Implementation Guide

Complete implementation guide for the combat system in UE5.

## 1. Combat Component Setup

### 3.1 Create Combat Component Blueprint
1. In UE5 Editor, right-click in Content Browser
2. Select **Blueprint Class**
3. Select `NobleArchimedesCombatComponent` as parent class
4. Name it `BP_CombatComponent`
5. Save to `Content/Blueprints/Combat/`

### 3.2 Configure Combat Component Properties
| Property | Value | Description |
|----------|-------|-------------|
| Max Health | 100 | Hector's maximum health |
| Perfect Guard Window | 0.1 | Seconds to release guard for perfect guard |
| Quick Step Iframes | 0.3 | Seconds of invulnerability during dodge |
| Double Step Window | 0.5 | Seconds between double step inputs |

### 3.3 Set Weapon Data Table
1. Create `DT_WeaponData` Data Table from `WeaponDataTable.csv`
2. Assign to `WeaponDataTable` property on Combat Component

## 2. Attack State Machine

### 2.1 States
| State | Animation | Duration | Next States |
|-------|-----------|----------|-------------|
| Idle | Idle | Loop | LightAttack1, HeavyAttack, QuickStep, Guard |
| LightAttack1 | AM_Combo_Sword/Light1 | 18 frames | LightAttack2, HeavyAttack, Idle |
| LightAttack2 | AM_Combo_Sword/Light2 | 16 frames | LightAttack3, HeavyAttack, Idle |
| LightAttack3 | AM_Combo_Sword/Light3 | 20 frames | HeavyAttack, Idle |
| HeavyAttack | AM_Combo_Sword/Heavy1/2/3 | 24-30 frames | Idle |
| QuickStep | AM_QuickStep | 28 frames | Idle |
| Guard | AM_Guard/Start, Loop, End | Variable | Idle |
| PerfectGuard | AM_Guard/Start, Flash, End | Variable | Idle |
| Stunned | AM_HitReaction | 30 frames | Idle |
| Dead | AM_Death | Loop | None |

### 2.2 Combo Timing Windows
| Stage | Window | Action |
|-------|--------|--------|
| After Light1 | 0.35s | Input Light2 or Heavy |
| After Light2 | 0.45s | Input Light3 or Heavy |
| After Light3 | 0.60s | Input Heavy |

## 3. Guard System

### 3.1 Guard States
| State | Duration | Effect |
|-------|----------|--------|
| Guard Start | 4 frames | Enter guard stance |
| Guard Loop | Variable | 70% damage reduction |
| Guard Release | 4 frames | Check perfect guard |
| Perfect Guard | 6 frames | 100% block + stun enemy |

### 3.2 Perfect Guard Logic
1. Player presses Guard button → Start guard
2. Player releases Guard button → Check timing
3. If released within 0.1s before enemy attack connects → Perfect Guard
4. If released outside window → Regular guard (70% damage reduction)

## 4. Quick Step System

### 4.1 Quick Step Properties
| Property | Value |
|----------|-------|
| Invulnerability Duration | 0.3 seconds (18 frames) |
| Launch Speed | 800 UU/s |
| Double Step Window | 0.5 seconds |
| Cooldown | None |

### 4.2 Quick Step Logic
1. Player presses Dodge button → Start Quick Step
2. Character becomes invulnerable for 0.3 seconds
3. Character launches in input direction
4. If second Quick Step within 0.5s → Double Step

## 5. Damage System

### 5.1 Damage Calculation
```
Base Damage × Weapon Multiplier × Type Multiplier × Guard Modifier = Final Damage
```

### 5.2 Type Multipliers
| Attacker Type | Defender Type | Multiplier |
|---------------|---------------|------------|
| Fire | Ice | 1.5x |
| Ice | Fire | 1.5x |
| Light | Dark | 1.5x |
| Dark | Light | 1.5x |
| Same | Same | 1.0x |
| Other | Other | 1.0x |

### 5.3 Guard Modifiers
| Guard State | Damage Multiplier |
|-------------|-------------------|
| No Guard | 1.0x |
| Regular Guard | 0.3x |
| Perfect Guard | 0.0x |

## 6. Death Doll System

### 6.1 Death Doll Mechanics
- Item that prevents death once
- When Hector would die, Death Doll activates instead
- Hector revives at 50% health
- Death Doll is consumed

### 6.2 Implementation
```cpp
void UNobleArchimedesCombatComponent::TakeDamage(float Damage, EDamageType Type)
{
    if (bIsInvulnerable) return;
    
    float FinalDamage = Damage;
    ApplyDamageReduction(FinalDamage, Type);
    
    if (bIsGuarding) {
        FinalDamage *= 0.3f;
        if (bPerfectGuard) FinalDamage = 0.0f;
    }
    
    CurrentHealth -= FinalDamage;
    
    if (CurrentHealth <= 0 && bHasDeathDoll) {
        CurrentHealth = MaxHealth * 0.5f;
        bHasDeathDoll = false;
        return; // Don't die
    }
    
    if (CurrentHealth <= 0) {
        // Trigger death
    }
}
```

## 7. Testing Checklist

- [ ] Light attack combos chain correctly
- [ ] Heavy attack follows any light attack
- [ ] Perfect Guard blocks 100% damage
- [ ] Regular Guard blocks 70% damage
- [ ] Quick Step provides 0.3s invulnerability
- [ ] Double Step works within 0.5s window
- [ ] Death Doll revives Hector once
- [ ] All 5 weapon types have unique animations
- [ ] All 11 damage types work correctly
- [ ] Weakness pairs deal 1.5x damage

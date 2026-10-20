# Weapon Forge Implementation Guide

Complete implementation guide for the weapon combining (forge) system in UE5.

## 1. Weapon Forge Component Setup

### 1.1 Create Component Blueprint
1. In UE5 Editor, right-click in Content Browser
2. Select **Blueprint Class**
3. Select `NobleArchimedesWeaponForge` as parent class
4. Name it `BP_WeaponForge`
5. Save to `Content/Blueprints/Combat/`

### 2. Material Data Table
1. Create `DT_MaterialData` from `MaterialDataTable.csv`
2. Contains 40 materials with colors, rarity, descriptions

### 3. Weapon Recipe Data Table
1. Create `DT_WeaponRecipe` from `WeaponRecipeTable.csv`
2. Contains 15 forge recipes with material requirements

## 2. Weapon Forge UI

### 2.1 Widget Layout
```
┌─────────────────────────────────────────┐
│         WEAPON FORGE                    │
│                                         │
│  Materials:                             │
│  [Iron Shard x5] [Silver Ingot x2]      │
│  [Dark Crystal x1]                      │
│                                         │
│  Recipes:                               │
│  [Short Sword]  [Broad Sword]           │
│  [Battle Axe]   [Long Spear]            │
│                                         │
│  Preview: [Weapon Model]                │
│                                         │
│   [FORGE] [CANCEL]                      │
│                                         │
└─────────────────────────────────────────┘
```

### 2.2 Widget Logic
1. Display player's material inventory
2. Show all forgeable recipes
3. Highlight available recipes
4. Show weapon preview on selection
5. Execute forge on button click

## 3. Forge Logic

### 3.1 Recipe Matching
```cpp
bool UNobleArchimedesWeaponForge::CombineWeapons(TArray<FName> Materials, FName& OutWeapon)
{
    for (const auto& Recipe : WeaponRecipes)
    {
        // Check if player has all required materials
        bool bCanForge = true;
        for (const auto& RequiredMat : Recipe.RequiredMaterials)
        {
            int32 Count = GetMaterialQuantity(RequiredMat);
            if (Count < 1) {
                bCanForge = false;
                break;
            }
        }
        
        if (bCanForge) {
            OutWeapon = Recipe.WeaponName;
            return true;
        }
    }
    return false;
}
```

### 3.2 Material Consumption
- When weapon is forged, consume required materials
- Decrement material counts in inventory
- If material count reaches 0, remove from inventory

## 3. Weapon Recipe List

| Weapon | Type | Materials | Forge Level |
|--------|------|-----------|-------------|
| Short Sword | Sword | Iron Shard x1 | 1 |
| Iron Sword | Sword | Iron Shard x2 | 2 |
| Broad Sword | Sword | Iron Shard x2, Silver Ingot x1 | 2 |
| Long Sword | Sword | Silver Ingot x2, Dark Crystal x1 | 3 |
| Great Sword | Sword | Silver Ingot x1, Dark Crystal x1, Phoenix Feather x1 | 4 |
| Executioner Sword | Sword | Dark Crystal x1, Phoenix Feather x1, Dragon Scale x1 | 5 |
| Battle Axe | Axe | Iron Shard x2, Demon Bone x1 | 3 |
| Great Axe | Axe | Iron Shard x1, Silver Ingot x1, Demon Bone x1, Ghost Essence x1 | 4 |
| Executioner Axe | Axe | Silver Ingot x1, Demon Bone x1, Dark Crystal x1, Wizard's Orb x1 | 5 |
| Long Spear | Spear | Iron Shard x1, Silver Ingot x1, Dark Crystal x1 | 4 |
| Halberd | Spear | Silver Ingot x1, Dark Crystal x1, Dragon Scale x1 | 5 |
| Pike | Spear | Dark Crystal x1, Dragon Scale x1, Demon Bone x1 | 6 |
| Punch Rings | Knuckles | Silver Ingot x1, Ghost Essence x1 | 2 |
| Claws | Knuckles | Silver Ingot x1, Ghost Essence x1, Dark Crystal x1 | 3 |
| Brass Knuckles | Knuckles | Silver Ingot x1, Ghost Essence x1, Dark Crystal x1, Phoenix Feather x1 | 4 |
| Katar | Knuckles | Ghost Essence x1, Dark Crystal x1, Phoenix Feather x1, Dragon Scale x1 | 5 |
| Shuriken | Special | Iron Shard x1, Holy Water x1 | 2 |
| Bomb | Special | Iron Shard x1, Phoenix Feather x1, Demon Bone x1 | 3 |
| Gatling Gun | Special | Mithril Ore x1, Adamantite x1, Orichalcum x1, Wizard's Orb x1 | 5 |

## 4. Material Locations

Materials are obtained from:
- Enemy drops (see EnemyDataTable.csv)
- Chest drops
- Shop purchases (Julia's Shop)
- Environment objects (candles, crates)

## 5. Testing Checklist

- [ ] All 15 weapon recipes work correctly
- [ ] Materials are consumed on forge
- [ ] Weapon is created with correct stats
- [ ] Evo Crystal color matches weapon type
- [ ] Cannot forge without required materials
- [ ] Forge UI updates after forging
- [ ] All 40 materials are obtainable

# Innocent Devil Implementation Guide

Complete implementation guide for the Innocent Devil (companion) system in UE5.

## 1. Innocent Devil Component Setup

### 1.1 Create Component Blueprint
1. In UE5 Editor, right-click in Content Browser
2. Select **Blueprint Class**
3. Select `NobleArchimedesInnocentDevilComponent` as parent class
4. Name it `BP_InnocentDevilComponent`
5. Save to `Content/Blueprints/Companions/`

### 3.2 Configure Component Properties
| Property | Value | Description |
|----------|-------|-------------|
| Follow Distance | 300 UU | Distance to follow Hector |
| Follow Speed | 600 UU/s | Movement speed |
| Active Devil | None | Currently active devil |

## 2. Innocent Devil Data Table

### 2.1 Create Data Table
1. Create `DT_InnocentDevilData` from `InnocentDevilDataTable.csv`
2. Assign to Innocent Devil Component

### 2.2 Devil Statistics

| Devil | Health | Attack | Mode | Evolution Crystal |
|-------|--------|--------|------|-------------------|
| Fairy | 50 | 8 | Auto/Command/Guard | Light |
| Griffin | 80 | 12 | Auto/Command/Guard | Fire |
| Salamander | 70 | 10 | Auto/Command/Guard | Fire |
| Ogre | 120 | 15 | Auto/Command/Guard | Slash |
| Skeleton Devil | 60 | 9 | Auto/Command/Guard | Dark |
| Witch Devil | 55 | 11 | Auto/Command/Guard | Magic |
| Pumpkin | 100 | 20 | Auto/Command/Guard | Special |

## 3. Innocent Devil Modes

### 3.1 Auto Mode
- Devil acts independently
- Attacks enemies automatically
- Uses abilities when appropriate
- Follows Hector at Follow Distance

### 3.2 Command Mode
- Player issues direct commands
- Attack: Devil attacks current target
- Guard: Devil blocks attacks
- Heal: Devil heals Hector

### 3.3 Guard Mode
- Devil stays close to Hector
- Blocks incoming attacks
- Does not attack unless commanded

## 4. Evolution System

### 4.1 Evolution Requirements
| Devil | Base Form | Evolved Form | Final Form | Crystal | Count |
|-------|-----------|--------------|------------|---------|-------|
| Fairy | Fairy | Fairy Elite | Fairy Queen | Light | 10 / 20 |
| Griffin | Griffin | Griffin Lord | Griffin King | Fire | 10 / 20 |
| Salamander | Salamander | Salamander Lord | Salamander King | Fire | 10 / 20 |
| Ogre | Ogre | Ogre Lord | Ogre King | Slash | 10 / 20 |
| Skeleton Devil | Skeleton Devil | Skeleton Lord | Skeleton King | Dark | 10 / 20 |
| Witch Devil | Witch Devil | Witch Lord | Witch Queen | Magic | 10 / 20 |
| Pumpkin | Pumpkin | Pumpkin Lord | Pumpkin King | Special | 15 / 30 |

### 4.2 Evolution Effects
- +5 levels
- +50 max health
- +10 attack
- New abilities unlocked

## 5. Implementation Steps

### 5.1 Create Innocent Devil Blueprints
1. Create `BP_Fairy`, `BP_Griffin`, etc. based on `NobleArchimedesInnocentDevilComponent`
2. Set up skeletal meshes for each devil
3. Set up animation montages
4. Set up collision components

### 5.2 Implement Devil AI
1. Create Behavior Tree for each devil type
2. Set up patrol, chase, attack behaviors
3. Implement mode switching (Auto/Command/Guard)
4. Implement evolution visual effects

### 5.3 Connect to Hector Character
1. Add `UNobleArchimedesInnocentDevilComponent` to Hector
2. Implement summon function
3. Implement mode switching
4. Implement evolution function

## 6. Testing Checklist

- [ ] All 6 devils + Pumpkin can be summoned
- [ ] All 3 modes work (Auto, Command, Guard)
- [ ] Evolution works with correct crystals
- [ ] Devils follow Hector correctly
- [ ] Devils attack enemies in Auto mode
- [ ] Devils respond to commands in Command mode
- [ ] Devils block in Guard mode
- [ ] Devil evolution changes appearance and stats

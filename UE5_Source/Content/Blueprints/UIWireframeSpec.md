# UI Wireframe Specification

This document defines all UI screens and layouts for the fan recreation,
based on the original Castlevania: Curse of Darkness UI.

## 1. Main Menu

```
┌─────────────────────────────────────────┐
│                                         │
│   NOBLE ARCHIMEDES                      │
│   Castlevania: Curse of Darkness        │
│   Fan Recreation v0.3.0                 │
│                                         │
│   [NEW GAME]                            │
│   [LOAD GAME]                           │
│   [OPTIONS]                             │
│   [QUIT]                                │
│                                         │
│   Private use only — Educational        │
│                                         │
└─────────────────────────────────────────┘
```

**Elements:**
- Title text (center top)
- 4 menu buttons (center)
- Version text (bottom left)
- Legal text (bottom center)

## 2. In-Game HUD

```
┌─────────────────────────────────────────┐
│  [HP] ██████████████████ 100/100        │
│  [MP] ██████████████████ 100/100        │
│                                         │
│   COMBO x3                              │
│                                         │
│  [Sword] [Fairy]                        │
│                                         │
│  Chapter 1: Abandoned Castle            │
│                                         │
└─────────────────────────────────────────┘
```

**Elements:**
- Health bar (green, top left)
- Mana bar (blue, top left)
- Combo counter (center top)
- Weapon icon (center, below combo)
- Innocent Devil icon (center, below weapon)
- Chapter name (bottom left)

## 3. Pause Menu

```
┌─────────────────────────────────────────┐
│                                         │
│       PAUSE                             │
│                                         │
│   [RESUME]                              │
│   [SAVE GAME]                           │
│   [LOAD GAME]                           │
│   [OPTIONS]                             │
│   [QUIT TO MAIN MENU]                   │
│                                         │
└─────────────────────────────────────────┘
```

**Elements:**
- Title (center top)
- 5 menu buttons (center)

## 4. Save/Load Menu

```
┌─────────────────────────────────────────┐
│                                         │
│       SAVE GAME                         │
│                                         │
│  [Slot 1]  Chapter 3    00:45:23        │
│  [Slot 2]  Chapter 1    00:12:10        │
│  [Slot 3]  Chapter 5    01:03:47        │
│  [Slot 4]  Empty                          │
│  [Slot 5]  Empty                          │
│                                         │
│   [SAVE] [LOAD] [DELETE] [CANCEL]       │
│                                         │
└─────────────────────────────────────────┘
```

**Elements:**
- Title (center top)
- 5 save slot rows (each with chapter name and timestamp)
- 4 action buttons (bottom)

## 5. Options Menu

```
┌─────────────────────────────────────────┐
│                                         │
│       OPTIONS                           │
│                                         │
│  Master Volume  ██████████ 100%         │
│  SFX Volume     ██████████ 100%         │
│  Music Volume   ██████████  70%         │
│                                         │
│  [V-Sync: ON]                           │
│  [Fullscreen: ON]                       │
│  [Resolution: 1920x1080]                │
│                                         │
│   [BACK]                                │
│                                         │
└─────────────────────────────────────────┘
```

**Elements:**
- Title (center top)
- 3 volume sliders
- 3 toggle/dropdown settings
- Back button

## 6. Weapon Forge (Julia's Shop)

```
┌─────────────────────────────────────────┐
│                                         │
│       WEAPON FORGE                      │
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

**Elements:**
- Title (center top)
- Material inventory (left)
- Recipe list (center)
- Weapon preview (right)
- Forge/Cancel buttons (bottom)

## 7. Innocent Devil Status

```
┌─────────────────────────────────────────┐
│                                         │
│       INNOCENT DEVIL                    │
│                                         │
│   [Fairy Portrait]                      │
│   Fairy  LVL 5                          │
│   HP ██████████ 50/50                   │
│                                         │
│   Mode: [Auto] [Command] [Guard]        │
│                                         │
│   Abilities:                            │
│   [Heal] [Revive]                       │
│                                         │
│   [EVOLVE]                              │
│                                         │
└─────────────────────────────────────────┘
```

**Elements:**
- Title (center top)
- Innocent Devil portrait (left)
- Name, Level, HP bar (center left)
- Mode buttons (center)
- Abilities list (center right)
- Evolve button (bottom)

## 8. UI Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Health Bar | #00FF00 (Green) | Player health |
| Mana Bar | #0000FF (Blue) | Player mana |
| Combo Counter | #FFFF00 (Yellow) | Combo count |
| Weapon Icon | #FFFFFF (White) | Weapon type |
| Innocent Devil Icon | #00FFFF (Cyan) | Companion type |
| Perfect Guard Flash | #FFFF00 (Yellow) | Perfect guard indicator |
| Quick Step Trail | #FFFFFF (White) | Dodge trail |

## 9. Implementation Steps in UE5

1. Create UMG Widget Blueprint for each screen
2. Set up anchor points for responsive layout
3. Bind health/mana to HectorCharacter stats
4. Bind combo counter to CombatComponent
5. Bind weapon icon to equipped weapon
6. Bind Innocent Devil icon to active companion
7. Create save/load slot widgets
8. Create forge widget with material/recipe lists
9. Create Innocent Devil status widget
10. Set up input mapping for menu navigation

---

**All UI layouts are based on the original Castlevania: Curse of Darkness HUD and menus.**
**Private use only — no copyrighted assets extracted.**
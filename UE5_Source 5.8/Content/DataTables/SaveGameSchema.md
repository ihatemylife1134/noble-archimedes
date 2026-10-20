# Save Game Schema Specification

This document defines the complete save game data structure,
matching the original PS2 memory card save format.

## Save Slot Structure

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| PlayerName | FString | "Hector" | Player character name |
| Health | int32 | 100 | Current health |
| MaxHealth | int32 | 100 | Maximum health |
| Mana | int32 | 100 | Current mana |
| MaxMana | int32 | 100 | Maximum mana |
| Level | int32 | 1 | Character level |
| Experience | int32 | 0 | Current XP |
| SkillPoints | int32 | 0 | Available skill points |
| CurrentChapter | int32 | 1 | Current chapter (1-10) |
| CompletedChapters | TArray<int32> | [] | Completed chapter IDs |
| CurrentLevelName | FString | "Chap_01_AbandonedCastle" | Current level |
| PlayerLocation | FVector | (0,0,0) | Player position |
| PlayerRotation | FRotator | (0,0,0) | Player rotation |
| InventoryItems | TArray<FInventoryItem> | [] | Inventory items |
| EquippedWeapons | TArray<FString> | [] | Equipped weapon names |
| EquippedWeaponType | EWeaponType | Sword | Currently equipped type |
| InnocentDevils | TArray<FInnocentDevilData> | [] | All devil data |
| ActiveInnocentDevilIndex | int32 | 0 | Currently active devil |
| UnlockedInnocentDevils | TArray<EInnocentDevilType> | [] | Unlocked devil types |
| bHasDeathDoll | bool | false | Has Death Doll item |
| DiscoveredRecipes | TArray<FName> | [] | Discovered forge recipes |
| ForgedWeapons | TArray<FName> | [] | Forged weapon names |
| MasterVolume | float | 1.0 | Master audio volume |
| SFXVolume | float | 1.0 | SFX volume |
| MusicVolume | float | 0.0 | Music volume |
| CurrentCameraMode | ECameraMode | Classic | Camera mode |

## Save Slots

| Slot | Type | Purpose |
|------|------|---------|
| 0-4 | Manual | Player saves (5 slots) |
| 5 | Auto | Auto-save (1 slot) |

## Auto-Save Triggers
- Chapter transition
- Save room entry
- Game quit

## Save File Location
`%LOCALAPPDATA%\NobleArchimedes\Saves\`

## Save File Format
UE5 USaveGame binary format

## Memory Card Equivalent
The original PS2 used Memory Card slots. The UE5 rebuild uses local file system saves with equivalent slot structure.

## Save Data Validation
- PlayerName must not be empty
- Health must be between 0 and MaxHealth
- CurrentChapter must be between 1 and 10
- InnocentDevils count must match UnlockedInnocentDevils count
- ActiveInnocentDevilIndex must reference a valid unlocked devil
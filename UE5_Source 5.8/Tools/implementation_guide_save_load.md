# Save/Load Implementation Guide

Complete implementation guide for the save/load system in UE5.

## 1. Save Game Data Structure

### 1.1 Save Game Class (`UNobleArchimedesSaveGame`)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
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

## 2. Save Game Instance

### 2.1 Save Game Instance Class (`UNobleArchimedesGameInstance`)

| Function | Parameters | Description |
|----------|-----------|-------------|
| SaveGame | int32 SlotIndex | Save game to slot |
| LoadGame | int32 SlotIndex | Load game from slot |
| HasSaveGame | int32 SlotIndex | Check if save exists |
| DeleteSaveGame | int32 SlotIndex | Delete save slot |
| GetSaveSlotNames | - | Get all save slot names |

### 2.2 Save Slots
| Slot | Type | Purpose |
|------|------|---------|
| 0-4 | Manual | Player saves (5 slots) |
| 5 | Auto | Auto-save (1 slot) |

## 3. Save Triggers

| Trigger | When | What |
|---------|------|------|
| Manual Save | Pause menu → Save Game | Current game state |
| Auto-Save | Chapter transition | Current game state |
| Auto-Save | Save room entry | Full heal + save |
| Auto-Save | Game quit | Current game state |

## 4. Save Room Mechanics

### 4.1 Save Room Behavior
1. Player enters save room
2. Full heal player (health, mana, Innocent Devils)
3. Auto-save game state
4. Visual: glowing floor tile
5. Audio: save confirmation sound

### 4.2 Save Room Implementation
```cpp
// In save room overlap event:
void ASaveRoom::OnPlayerOverlap(AActor* OverlappedActor, AActor* OtherActor)
{
    if (AHectorCharacter* Hector = Cast<AHectorCharacter>(OtherActor))
    {
        // Full heal
        Hector->SetHealth(Hector->GetMaxHealth());
        
        // Heal all Innocent Devils
        for (auto& Devil : Hector->GetInnocentDevils())
        {
            Devil.Health = Devil.MaxHealth;
        }
        
        // Auto-save
        UNobleArchimedesGameInstance* GI = Cast<UNobleArchimedesGameInstance>(GetGameInstance());
        if (GI) GI->SaveGame(5); // Auto-save slot
    }
}
```

## 5. Save File Format

### 5.1 Save File Location
`%LOCALAPPDATA%\NobleArchimedes\Saves\`

### 5.2 Save File Format
UE5 `USaveGame` binary format

### 5.3 Save File Contents
- All SaveGame properties
- Timestamp
- Version number

## 6. Load Game Pipeline

1. Main menu → Load Game
2. Show save slot list with timestamps
3. Player selects slot
4. Load save data into memory
5. Load chapter level
6. Spawn player at saved location
7. Restore health, mana, inventory, Innocent Devils
8. Apply camera and audio settings

## 7. Testing Checklist

- [ ] Manual save from pause menu works
- [ ] Auto-save on chapter transition works
- [ ] Auto-save on save room entry works
- [ ] Auto-save on game quit works
- [ ] Load game restores correct state
- [ ] Load game restores correct chapter
- [ ] Load game restores correct location
- [ ] Load game restores correct health/mana
- [ ] Load game restores correct inventory
- [ ] Load game restores correct Innocent Devils
- [ ] Delete save game works
- [ ] Save file corruption recovery works
- [ ] Multiple save slots work independently

## 8. Save Data Validation

| Validation | Rule |
|------------|------|
| PlayerName | Must not be empty |
| Health | Must be between 0 and MaxHealth |
| Mana | Must be between 0 and MaxMana |
| CurrentChapter | Must be between 1 and 10 |
| InnocentDevils count | Must match UnlockedInnocentDevils count |
| ActiveInnocentDevilIndex | Must reference valid unlocked devil |

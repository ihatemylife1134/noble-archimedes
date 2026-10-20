# Level Streaming Implementation Guide

Complete implementation guide for level streaming across all 10 chapters.

## 1. Level Structure

### 1.1 Persistent Level
Contains:
- Player character (Hector)
- UI/HUD
- Save game system
- Audio manager
- Game instance
- Global game mode

### 1.2 Chapter Levels
| Chapter | Level Name | Streaming |
|---------|-----------|-----------|
| 1 | Chap_01_AbandonedCastle | Stream in/out |
| 2 | Chap_02_BaljhetMountains | Stream in/out |
| 3 | Chap_03_GaribaldiTemple | Stream in/out |
| 4 | Chap_04_MortviaAqueduct | Stream in/out |
| 5 | Chap_05_ForestOfJigramunt | Stream in/out |
| 6 | Chap_06_CordovaTown | Stream in/out |
| 7 | Chap_07_EneomaosMachineTower | Stream in/out |
| 8 | Chap_08_AiolonRuins | Stream in/out |
| 9 | Chap_09_InfiniteCorridor | Stream in/out |
| 10 | Chap_10_DraculasCastle | Stream in/out |

## 2. Level Streaming Setup

### 2.1 Create Level Streaming Volumes
1. In UE5 Editor, open each chapter level
2. Place Level Streaming Volume at chapter boundaries
3. Configure streaming distance
4. Set load/unload distances

### 2.2 Streaming Distances
| Chapter | Load Distance | Unload Distance |
|---------|--------------|-----------------|
| 1-10 | 2000 UU | 3000 UU |

## 3. Chapter Transitions

### 3.1 Transition Flow
1. Player reaches chapter transition point
2. Room lock check (all enemies defeated or transition allowed)
3. Fade to black
4. Save game state
5. Unload current chapter level
6. Load next chapter level
7. Spawn player at chapter start location
8. Fade in
9. Restore game state

### 3.2 Transition Implementation
```cpp
void UNobleArchimedesLevelStreaming::TransitionToChapter(int32 ChapterIndex)
{
    // Unload previous chapter
    if (CurrentChapterIndex >= 0 && CurrentChapterIndex < ChapterLevelNames.Num())
    {
        UnloadChapter(CurrentChapterIndex);
    }
    
    // Load new chapter
    LoadChapter(ChapterIndex);
    CurrentChapterIndex = ChapterIndex;
}
```

## 3. Chapter Entry Points

| Chapter | Entry Point | Exit Points |
|---------|-------------|-------------|
| 1 | Courtyard | To Chapter 2 |
| 2 | Mountain Pass | To Chapter 3 |
| 3 | Temple Nave | To Chapter 4 |
| 4 | Aqueduct Entrance | To Chapter 5 |
| 5 | Forest Edge | To Chapter 6 |
| 6 | Town Square | To Chapter 7 |
| 7 | Gear Chamber | To Chapter 8 |
| 8 | Ruin Entrance | To Chapter 9 |
| 9 | Corridor Loop | To Chapter 10 |
| 10 | Grand Hall | (Final boss) |

## 4. Room System

### 4.1 Room Lock
- Room locks when enemies enter (red bars drop)
- Rooms unlock when all enemies defeated
- Cleared rooms remain unlocked on return
- Save rooms are always unlocked

### 4.2 Room Implementation
```cpp
// In room volume overlap event:
void ARoom::OnEnemyEnter(AActor* Enemy)
{
    if (Enemy->IsA<AEnemy>())
    {
        bRoomLocked = true;
        bRedBarsDropped = true;
        // Visual: red bars appear
    }
}

void ARoom::OnEnemyDefeat(AActor* Enemy)
{
    bool bAllDefeated = true;
    for (AActor* OtherEnemy : EnemiesInRoom)
    {
        if (!OtherEnemy->IsDead())
        {
            bAllDefeated = false;
            break;
        }
    }
    
    if (bAllDefeated && bRoomLocked)
    {
        bRoomLocked = false;
        bRedBarsDropped = false;
        // Visual: red bars raise
    }
}
```

## 5. Save Room Implementation

### 5.1 Save Room Behavior
1. Player enters save room
2. Full heal player (health, mana, Innocent Devils)
3. Auto-save game state
4. Visual: glowing floor tile
5. Audio: save confirmation sound

### 5.2 Save Room Implementation
```cpp
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

## 6. Candle System

### 6.1 Candle Behavior
- Breakable light sources
- Drop items when broken: Serum, Uncurse, Potions, High Potions (last two levels only)
- Visual: flickering flame
- Audio: candle break sound

### 6.2 Candle Implementation
```cpp
void ACandleBreakable::OnPlayerAttack(AActor* Attacker)
{
    // Spawn break effects
    UNobleArchimedesVFXComponent* VFX = Cast<UNobleArchimedesVFXComponent>(GetComponentByClass(UNobleArchimedesVFXComponent::StaticClass()));
    if (VFX) VFX->PlayCandleBreak(GetActorLocation());
    
    // Drop items
    UNobleArchimedesItemSystem* ItemSystem = Cast<UNobleArchimedesItemSystem>(GetComponentByClass(UNobleArchimedesItemSystem::StaticClass()));
    if (ItemSystem)
    {
        FName Item = GetRandomItemDrop();
        ItemSystem->AddItem(Item, 1);
    }
    
    // Destroy candle
    Destroy();
}
```

## 7. Testing Checklist

- [ ] Chapter 1 loads correctly
- [ ] Chapter transitions work
- [ ] Save rooms fully heal player
- [ ] Save rooms auto-save
- [ ] Candles drop items when broken
- [ ] Room locks when enemies enter
- [ ] Room unlocks when all enemies defeated
- [ ] Cleared rooms remain unlocked on return
- [ ] Level streaming doesn't cause hitches
- [ ] Player spawns at correct location after chapter transition
